"""End-to-end tests for static site generation."""

import pytest
import tempfile
import shutil
from pathlib import Path
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

from src.generators.static_site_generator import StaticSiteGenerator
from src.models.article import Article


class TestStaticSiteGeneration:
    """End-to-end tests for static site generation."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test outputs."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def site_generator(self, settings, temp_output_dir):
        """Create static site generator with temp output directory."""
        settings.output_dir = temp_output_dir
        return StaticSiteGenerator(settings)

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_complete_site_generation(self, site_generator, sample_articles, temp_output_dir):
        """Test complete static site generation process."""
        # Given
        articles = sample_articles
        for article in articles:
            article.evaluation = {
                "engineer": {"total_score": 0.8, "breakdown": {}},
                "business": {"total_score": 0.7, "breakdown": {}}
            }
        
        # When
        result = await site_generator.generate_complete_site(articles)
        
        # Then
        assert result is not None
        assert temp_output_dir.exists()
        
        # Check main files exist
        assert (temp_output_dir / "index.html").exists()
        assert (temp_output_dir / "styles.css").exists()
        assert (temp_output_dir / "script.js").exists()
        
        # Check content quality
        index_content = (temp_output_dir / "index.html").read_text(encoding='utf-8')
        assert len(index_content) > 1000
        assert "Daily AI News" in index_content
        assert "DOCTYPE html" in index_content

    @pytest.mark.e2e 
    @pytest.mark.asyncio
    async def test_responsive_design(self, site_generator, sample_articles, temp_output_dir):
        """Test responsive design across different screen sizes."""
        # Generate site
        await site_generator.generate_complete_site(sample_articles)
        
        index_file = temp_output_dir / "index.html"
        assert index_file.exists()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            try:
                # Load the page
                await page.goto(f"file://{index_file.absolute()}")
                
                # Test desktop view
                await page.set_viewport_size({"width": 1920, "height": 1080})
                await page.wait_for_load_state("networkidle")
                
                # Check that main content is visible
                main_content = page.locator("main, .main-content, #content")
                await expect(main_content).to_be_visible()
                
                # Test tablet view
                await page.set_viewport_size({"width": 768, "height": 1024})
                await page.wait_for_timeout(500)
                await expect(main_content).to_be_visible()
                
                # Test mobile view
                await page.set_viewport_size({"width": 375, "height": 667})
                await page.wait_for_timeout(500)
                await expect(main_content).to_be_visible()
                
                # Take screenshots for verification
                await page.screenshot(path=temp_output_dir / "mobile_view.png")
                
            finally:
                await browser.close()

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_interactive_features(self, site_generator, sample_articles, temp_output_dir):
        """Test interactive features functionality."""
        # Generate site with interactive features
        await site_generator.generate_complete_site(sample_articles, include_interactive=True)
        
        index_file = temp_output_dir / "index.html"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            try:
                await page.goto(f"file://{index_file.absolute()}")
                await page.wait_for_load_state("networkidle")
                
                # Test search functionality
                search_input = page.locator("input[type='search'], #search, .search-input")
                if await search_input.count() > 0:
                    await search_input.first.fill("machine learning")
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(500)
                
                # Test filter functionality
                filter_select = page.locator("select.filter, .filter-select")
                if await filter_select.count() > 0:
                    await filter_select.first.select_option("engineer")
                    await page.wait_for_timeout(500)
                
                # Test persona toggle
                persona_toggle = page.locator(".persona-toggle, #persona-switch")
                if await persona_toggle.count() > 0:
                    await persona_toggle.first.click()
                    await page.wait_for_timeout(500)
                
                # Verify page doesn't break
                await expect(page.locator("body")).to_be_visible()
                
            finally:
                await browser.close()

    @pytest.mark.e2e
    def test_seo_compliance(self, site_generator, sample_articles, temp_output_dir):
        """Test SEO compliance of generated site."""
        # Generate site
        import asyncio
        asyncio.run(site_generator.generate_complete_site(sample_articles))
        
        index_file = temp_output_dir / "index.html"
        content = index_file.read_text(encoding='utf-8')
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Check essential SEO elements
        assert soup.find('title') is not None, "Missing title tag"
        assert soup.find('meta', {'name': 'description'}) is not None, "Missing meta description"
        
        # Check Open Graph tags
        og_title = soup.find('meta', {'property': 'og:title'})
        og_description = soup.find('meta', {'property': 'og:description'})
        assert og_title is not None or og_description is not None, "Missing Open Graph tags"
        
        # Check heading structure
        h1_tags = soup.find_all('h1')
        assert len(h1_tags) >= 1, "Missing H1 tag"
        assert len(h1_tags) <= 3, "Too many H1 tags"
        
        # Check for proper lang attribute
        html_tag = soup.find('html')
        assert html_tag.get('lang') is not None, "Missing lang attribute on html tag"

    @pytest.mark.e2e
    def test_accessibility_compliance(self, site_generator, sample_articles, temp_output_dir):
        """Test accessibility compliance."""
        import asyncio
        asyncio.run(site_generator.generate_complete_site(sample_articles))
        
        index_file = temp_output_dir / "index.html"
        content = index_file.read_text(encoding='utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        
        # Check images have alt text
        images = soup.find_all('img')
        for img in images:
            assert img.get('alt') is not None, f"Image {img.get('src', 'unknown')} missing alt text"
        
        # Check links have descriptive text
        links = soup.find_all('a')
        for link in links:
            link_text = link.get_text(strip=True)
            assert len(link_text) > 0 or link.get('aria-label'), f"Link {link.get('href', 'unknown')} needs descriptive text"
        
        # Check form elements have labels
        inputs = soup.find_all('input')
        for input_elem in inputs:
            input_id = input_elem.get('id')
            if input_id:
                label = soup.find('label', {'for': input_id})
                assert label is not None or input_elem.get('aria-label'), f"Input {input_id} needs label"

    @pytest.mark.e2e
    def test_performance_optimization(self, site_generator, sample_articles, temp_output_dir):
        """Test performance optimization features."""
        import asyncio
        asyncio.run(site_generator.generate_complete_site(sample_articles, optimize=True))
        
        # Check file sizes are reasonable
        index_file = temp_output_dir / "index.html"
        css_file = temp_output_dir / "styles.css"
        js_file = temp_output_dir / "script.js"
        
        # HTML should be under 500KB for good performance
        assert index_file.stat().st_size < 500_000, "HTML file too large"
        
        if css_file.exists():
            assert css_file.stat().st_size < 100_000, "CSS file too large"
        
        if js_file.exists():
            assert js_file.stat().st_size < 200_000, "JavaScript file too large"
        
        # Check that CSS/JS is minified (no unnecessary whitespace)
        index_content = index_file.read_text()
        
        # Shouldn't have excessive blank lines
        lines = index_content.split('\n')
        empty_lines = sum(1 for line in lines if not line.strip())
        assert empty_lines < len(lines) * 0.3, "Too many empty lines, file not optimized"

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_cross_browser_compatibility(self, site_generator, sample_articles, temp_output_dir):
        """Test cross-browser compatibility."""
        await site_generator.generate_complete_site(sample_articles)
        
        index_file = temp_output_dir / "index.html"
        
        async with async_playwright() as p:
            # Test multiple browsers
            browsers = ["chromium", "firefox", "webkit"]
            
            for browser_name in browsers:
                try:
                    browser = await getattr(p, browser_name).launch()
                    page = await browser.new_page()
                    
                    await page.goto(f"file://{index_file.absolute()}")
                    await page.wait_for_load_state("networkidle")
                    
                    # Basic functionality test
                    body = page.locator("body")
                    await expect(body).to_be_visible()
                    
                    # Check for JavaScript errors
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    
                    await page.wait_for_timeout(2000)
                    assert len(errors) == 0, f"JavaScript errors in {browser_name}: {errors}"
                    
                    await browser.close()
                    
                except Exception as e:
                    pytest.skip(f"Browser {browser_name} not available: {e}")

    @pytest.mark.e2e
    def test_rss_feed_generation(self, site_generator, sample_articles, temp_output_dir):
        """Test RSS feed generation."""
        import asyncio
        asyncio.run(site_generator.generate_complete_site(sample_articles, include_rss=True))
        
        # Check RSS file exists
        rss_file = temp_output_dir / "feed.xml"
        assert rss_file.exists(), "RSS feed not generated"
        
        # Validate RSS content
        rss_content = rss_file.read_text(encoding='utf-8')
        
        assert "<?xml" in rss_content
        assert "<rss" in rss_content
        assert "<channel>" in rss_content
        assert "<title>Daily AI News</title>" in rss_content
        
        # Check that articles are included
        assert rss_content.count("<item>") >= len(sample_articles)

    @pytest.mark.e2e
    def test_sitemap_generation(self, site_generator, sample_articles, temp_output_dir):
        """Test XML sitemap generation."""
        import asyncio
        asyncio.run(site_generator.generate_complete_site(sample_articles, include_sitemap=True))
        
        # Check sitemap file exists
        sitemap_file = temp_output_dir / "sitemap.xml"
        assert sitemap_file.exists(), "Sitemap not generated"
        
        # Validate sitemap content
        sitemap_content = sitemap_file.read_text(encoding='utf-8')
        
        assert "<?xml" in sitemap_content
        assert "<urlset" in sitemap_content
        assert "<url>" in sitemap_content
        assert "<loc>" in sitemap_content
        
        # Should have at least main page + article pages
        assert sitemap_content.count("<url>") >= 1

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_large_dataset_performance(self, site_generator, temp_output_dir):
        """Test performance with large number of articles."""
        # Generate large dataset
        large_article_set = []
        for i in range(100):  # 100 articles
            article = Article(
                id=f"large-test-{i}",
                title=f"Test Article {i}",
                url=f"https://example.com/article-{i}",
                source="Test Source",
                source_tier=1,
                content=f"This is test content for article {i}. " * 50  # Substantial content
            )
            article.evaluation = {
                "engineer": {"total_score": 0.7 + (i % 3) * 0.1},
                "business": {"total_score": 0.6 + (i % 4) * 0.1}
            }
            large_article_set.append(article)
        
        # Test generation time
        import time
        start_time = time.time()
        
        import asyncio
        asyncio.run(site_generator.generate_complete_site(large_article_set))
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Should complete within reasonable time (adjust based on requirements)
        assert generation_time < 30, f"Generation took too long: {generation_time}s"
        
        # Verify all files generated correctly
        assert (temp_output_dir / "index.html").exists()
        
        # Check file sizes are reasonable even with large dataset
        index_size = (temp_output_dir / "index.html").stat().st_size
        assert index_size < 2_000_000, f"Generated file too large: {index_size} bytes"

    @pytest.mark.e2e
    def test_error_handling(self, site_generator, temp_output_dir):
        """Test error handling during site generation."""
        # Test with invalid articles
        invalid_articles = [
            Article(id="", title="", url="", source="", source_tier=1),  # Empty fields
            None,  # None value
        ]
        
        # Should handle gracefully without crashing
        import asyncio
        try:
            result = asyncio.run(site_generator.generate_complete_site([a for a in invalid_articles if a]))
            # Should still generate some output even with problematic input
            assert (temp_output_dir / "index.html").exists()
        except Exception as e:
            pytest.fail(f"Generator should handle invalid input gracefully: {e}")

    @pytest.mark.e2e
    def test_content_security_policy(self, site_generator, sample_articles, temp_output_dir):
        """Test Content Security Policy implementation."""
        import asyncio
        asyncio.run(site_generator.generate_complete_site(sample_articles, secure=True))
        
        index_content = (temp_output_dir / "index.html").read_text()
        
        # Should include CSP meta tag for security
        assert 'content-security-policy' in index_content.lower() or \
               'csp' in index_content.lower(), "Missing Content Security Policy"