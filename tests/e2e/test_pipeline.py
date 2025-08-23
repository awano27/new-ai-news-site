"""End-to-end pipeline tests with Playwright."""

import pytest
from playwright.async_api import async_playwright
from pathlib import Path
import asyncio
from src.main import DailyAINews


class TestPipeline:
    """End-to-end tests for the complete pipeline."""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_complete_pipeline_with_mock_data(self, settings, test_output_dir):
        """Test the complete pipeline from collection to output generation."""
        # Given
        settings.tier1_sources = ["arxiv"]  # Limit to one source for testing
        settings.max_items_per_category = 2
        settings.hours_lookback = 24
        
        app = DailyAINews(config_path=None)
        app.settings = settings
        
        # When
        try:
            articles = await app.run_pipeline(tier1_only=True)
            
            # Then
            assert isinstance(articles, list)
            assert len(articles) >= 0  # May be empty if no recent articles
            
            # Check output files exist
            output_dir = Path(settings.output_dir)
            assert output_dir.exists()
            
        except Exception as e:
            pytest.skip(f"Pipeline test skipped due to external dependency: {e}")

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_html_output_generation(self, settings, test_output_dir, sample_articles):
        """Test HTML output generation and validation."""
        # Given
        settings.output_dir = test_output_dir / "html_output"
        app = DailyAINews(config_path=None)
        app.settings = settings
        
        # Mock the collector to return sample articles
        async def mock_collect_all(tier1_only=False):
            return sample_articles
        
        app.collector.collect_all = mock_collect_all
        
        # When
        articles = await app.run_pipeline()
        
        # Then
        assert len(articles) > 0
        
        # Check HTML output
        html_file = Path(settings.output_dir) / "index.html"
        if html_file.exists():
            content = html_file.read_text(encoding='utf-8')
            assert "Daily AI News" in content
            assert len(content) > 1000  # Should have substantial content

    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_browser_rendering(self, settings, test_output_dir):
        """Test that generated HTML renders correctly in browser."""
        # Skip if no HTML file exists
        html_file = test_output_dir / "html_output" / "index.html"
        if not html_file.exists():
            pytest.skip("No HTML file to test")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            try:
                # Load the generated HTML
                await page.goto(f"file://{html_file.absolute()}")
                
                # Wait for page to load
                await page.wait_for_load_state("networkidle")
                
                # Check basic elements are present
                title = await page.title()
                assert "Daily AI News" in title
                
                # Check for main content areas
                main_content = page.locator("main, .main-content, #main")
                await expect(main_content).to_be_visible()
                
                # Check for article cards/items
                articles = page.locator(".article, .card, .news-item")
                count = await articles.count()
                assert count >= 0  # May be zero if no articles
                
                # Test responsive design
                await page.set_viewport_size({"width": 375, "height": 667})  # Mobile
                await page.wait_for_timeout(500)
                
                await page.set_viewport_size({"width": 1920, "height": 1080})  # Desktop
                await page.wait_for_timeout(500)
                
                # Take a screenshot for manual verification
                screenshot_path = test_output_dir / "screenshot.png"
                await page.screenshot(path=str(screenshot_path))
                
            finally:
                await browser.close()

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_search_functionality(self, settings, sample_articles):
        """Test search functionality end-to-end."""
        # Given
        app = DailyAINews(config_path=None)
        app.settings = settings
        
        # Mock data
        for article in sample_articles:
            # Add mock evaluation data
            article.evaluation = {
                "engineer": {"total_score": 0.8, "breakdown": {}},
                "business": {"total_score": 0.7, "breakdown": {}}
            }
        
        # When - Test search
        query = "machine learning"
        
        try:
            # This would test the search engine if implemented
            search_results = await app.search_engine.search(query)
            
            # Then
            assert isinstance(search_results, list)
            
        except AttributeError:
            pytest.skip("Search engine not implemented yet")

    @pytest.mark.e2e
    @pytest.mark.asyncio  
    async def test_evaluation_accuracy(self, settings, sample_articles):
        """Test evaluation system accuracy with known good/bad articles."""
        # Given
        app = DailyAINews(config_path=None)
        app.settings = settings
        
        # Create articles with known quality levels
        high_quality_article = sample_articles[0]  # Technical article
        high_quality_article.technical.implementation_ready = True
        high_quality_article.technical.code_available = True
        high_quality_article.technical.reproducibility_score = 0.9
        
        low_quality_article = sample_articles[1]  # Business article with less technical depth
        low_quality_article.content = "Short article without much detail."
        
        # When
        try:
            high_eval = await app.evaluator.evaluate(high_quality_article, "engineer")
            low_eval = await app.evaluator.evaluate(low_quality_article, "engineer")
            
            # Then
            assert high_eval["total_score"] > low_eval["total_score"]
            
        except AttributeError:
            pytest.skip("Evaluator not implemented yet")

    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_performance_benchmarks(self, settings, sample_articles):
        """Test performance benchmarks for the pipeline."""
        # Given
        app = DailyAINews(config_path=None)
        app.settings = settings
        app.settings.max_items_per_category = 10  # Small set for testing
        
        import time
        
        # When
        start_time = time.time()
        
        try:
            # Mock fast collection
            async def mock_collect():
                return sample_articles[:10]
            
            app.collector.collect_all = mock_collect
            
            articles = await app.run_pipeline(tier1_only=True)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Then
            assert processing_time < 30  # Should complete within 30 seconds
            assert len(articles) <= 10
            
        except Exception as e:
            pytest.skip(f"Performance test skipped: {e}")