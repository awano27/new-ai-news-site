#!/usr/bin/env python3
"""Phase 4 Test Runner - HTML generation and static site tests."""

import sys
import asyncio
import tempfile
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import Settings
from src.models.article import Article
from src.generators.html_generator import HTMLGenerator
from src.generators.static_site_generator import StaticSiteGenerator


def create_test_articles():
    """Create test articles for Phase 4 testing."""
    articles = []
    
    # Article 1: High-scoring engineer article
    article1 = Article(
        id="test-001",
        title="Revolutionary Transformer Architecture Breakthrough",
        url="https://example.com/transformer-breakthrough",
        source="ArXiv",
        source_tier=1,
        content="A groundbreaking new transformer architecture that achieves state-of-the-art results..."
    )
    article1.evaluation = {
        "engineer": {"total_score": 0.92, "breakdown": {"technical_depth": 0.95}},
        "business": {"total_score": 0.78, "breakdown": {"business_impact": 0.80}}
    }
    articles.append(article1)
    
    # Article 2: High-scoring business article
    article2 = Article(
        id="test-002", 
        title="AI Implementation ROI: $50M Cost Savings Case Study",
        url="https://example.com/roi-case-study",
        source="McKinsey",
        source_tier=1,
        content="Enterprise AI implementation delivers measurable business value..."
    )
    article2.evaluation = {
        "engineer": {"total_score": 0.65, "breakdown": {"technical_depth": 0.60}},
        "business": {"total_score": 0.88, "breakdown": {"business_impact": 0.90}}
    }
    articles.append(article2)
    
    # Article 3: Medium-tier article
    article3 = Article(
        id="test-003",
        title="Open Source LLM Training Guide",
        url="https://example.com/llm-training",
        source="TechBlog",
        source_tier=2,
        content="Step-by-step guide for training your own large language model..."
    )
    article3.evaluation = {
        "engineer": {"total_score": 0.74, "breakdown": {"technical_depth": 0.80}},
        "business": {"total_score": 0.62, "breakdown": {"business_impact": 0.65}}
    }
    articles.append(article3)
    
    return articles


async def test_html_generator():
    """Test HTML generator functionality."""
    print("🎨 Testing HTML Generator...")
    
    try:
        settings = Settings()
        generator = HTMLGenerator(settings)
        articles = create_test_articles()
        
        # Test basic generation
        result = generator.generate(articles, persona="engineer")
        assert result is not None
        print("✅ Basic HTML generation successful")
        
        # Test persona switching
        engineer_html = generator.generate(articles, persona="engineer")
        business_html = generator.generate(articles, persona="business")
        assert engineer_html != business_html
        print("✅ Persona-specific generation works")
        
        # Test article card rendering
        card_html = generator._render_article_card(articles[0], persona="engineer")
        assert articles[0].title in card_html
        assert "0.92" in card_html or "92" in card_html
        print("✅ Article card rendering includes scores")
        
        # Test template engine
        template_engine = generator.template_engine
        template = "<h1>{{title}}</h1><p>{{content}}</p>"
        variables = {"title": "Test Title", "content": "Test Content"}
        rendered = template_engine.render(template, variables)
        assert "Test Title" in rendered
        assert "Test Content" in rendered
        print("✅ Template engine working correctly")
        
        print("✅ HTML Generator: All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ HTML Generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_static_site_generator():
    """Test static site generator functionality."""
    print("\n🏗️ Testing Static Site Generator...")
    
    try:
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.output_dir = temp_dir
            
            generator = StaticSiteGenerator(settings)
            articles = create_test_articles()
            
            # Test complete site generation
            result = await generator.generate_complete_site(
                articles, 
                include_interactive=True,
                include_rss=True,
                include_sitemap=True
            )
            
            assert result["status"] == "success"
            assert result["total_articles"] == len(articles)
            print(f"✅ Generated site with {result['total_articles']} articles")
            
            # Check required files exist
            output_path = Path(temp_dir)
            required_files = ["index.html", "styles.css", "script.js", "feed.xml", "sitemap.xml"]
            
            for filename in required_files:
                file_path = output_path / filename
                assert file_path.exists(), f"Missing required file: {filename}"
                assert file_path.stat().st_size > 100, f"File too small: {filename}"
            
            print("✅ All required files generated")
            
            # Test content quality
            index_content = (output_path / "index.html").read_text(encoding='utf-8')
            assert len(index_content) > 2000
            assert "Daily AI News" in index_content
            assert "DOCTYPE html" in index_content
            assert articles[0].title in index_content
            print("✅ Generated HTML contains expected content")
            
            # Test CSS generation
            css_content = (output_path / "styles.css").read_text(encoding='utf-8')
            assert ".article-card" in css_content
            assert "@media" in css_content  # Responsive design
            assert "var(--primary-color)" in css_content  # CSS variables
            print("✅ CSS includes responsive design and styling")
            
            # Test JavaScript generation
            js_content = (output_path / "script.js").read_text(encoding='utf-8')
            assert "DashboardController" in js_content
            assert "switchPersona" in js_content
            assert "applyFilters" in js_content
            print("✅ JavaScript includes interactive functionality")
            
            # Test RSS feed
            rss_content = (output_path / "feed.xml").read_text(encoding='utf-8')
            assert "<?xml" in rss_content
            assert "<rss" in rss_content
            assert "<channel>" in rss_content
            assert articles[0].title in rss_content
            print("✅ RSS feed generated with article content")
            
            # Test sitemap
            sitemap_content = (output_path / "sitemap.xml").read_text(encoding='utf-8')
            assert "<?xml" in sitemap_content
            assert "<urlset" in sitemap_content
            assert "<url>" in sitemap_content
            print("✅ XML sitemap generated")
            
            # Test persona-specific pages
            persona_results = await generator.generate_persona_specific_pages(articles)
            assert "engineer" in persona_results
            assert "business" in persona_results
            
            engineer_file = Path(persona_results["engineer"])
            business_file = Path(persona_results["business"])
            assert engineer_file.exists()
            assert business_file.exists()
            print("✅ Persona-specific pages generated")
            
        print("✅ Static Site Generator: All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Static Site Generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integration():
    """Test integration between HTML and static site generators."""
    print("\n🔗 Testing Generator Integration...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.output_dir = temp_dir
            
            # Test complete workflow
            html_generator = HTMLGenerator(settings)
            site_generator = StaticSiteGenerator(settings)
            articles = create_test_articles()
            
            # Generate site
            result = await site_generator.generate_complete_site(
                articles,
                persona="engineer",
                include_interactive=True,
                optimize=True,
                secure=True
            )
            
            # Verify integration works
            assert result["status"] == "success"
            
            # Check that HTML generator output is used in site
            output_path = Path(temp_dir)
            index_content = (output_path / "index.html").read_text(encoding='utf-8')
            
            # Should contain persona-specific content
            assert "persona-engineer" in index_content or "engineer" in index_content.lower()
            
            # Should contain security features
            assert "content-security-policy" in index_content.lower()
            
            # Should be optimized (minified)
            lines = index_content.split('\n')
            empty_lines = sum(1 for line in lines if not line.strip())
            assert empty_lines < len(lines) * 0.1  # Less than 10% empty lines
            
            print("✅ Integration produces optimized, secure output")
            
            # Test archive generation
            archive_results = await site_generator.generate_archive_pages(
                articles, 
                group_by="tier"
            )
            assert "tier" in archive_results
            print("✅ Archive pages generation works")
            
        print("✅ Generator Integration: All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_performance():
    """Test performance with larger datasets."""
    print("\n⚡ Testing Performance...")
    
    try:
        # Create larger dataset
        large_articles = []
        for i in range(50):  # 50 articles
            article = Article(
                id=f"perf-test-{i:03d}",
                title=f"Performance Test Article {i+1}: AI Technology Update",
                url=f"https://example.com/article-{i+1}",
                source=f"Source{i % 5 + 1}",
                source_tier=(i % 2) + 1,
                content=f"This is performance test content for article {i+1}. " * 20
            )
            article.evaluation = {
                "engineer": {"total_score": 0.5 + (i % 5) * 0.1},
                "business": {"total_score": 0.4 + (i % 6) * 0.1}
            }
            large_articles.append(article)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.output_dir = temp_dir
            
            generator = StaticSiteGenerator(settings)
            
            # Measure generation time
            import time
            start_time = time.time()
            
            result = await generator.generate_complete_site(large_articles)
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Performance assertions
            assert generation_time < 10  # Should complete within 10 seconds
            assert result["status"] == "success"
            
            # Check file sizes are reasonable
            output_path = Path(temp_dir)
            index_size = (output_path / "index.html").stat().st_size
            assert index_size < 1_000_000  # Less than 1MB
            
            css_size = (output_path / "styles.css").stat().st_size
            assert css_size < 100_000  # Less than 100KB
            
            js_size = (output_path / "script.js").stat().st_size
            assert js_size < 50_000  # Less than 50KB
            
            print(f"✅ Generated 50 articles in {generation_time:.2f}s")
            print(f"✅ File sizes: HTML {index_size:,}B, CSS {css_size:,}B, JS {js_size:,}B")
            
        print("✅ Performance: All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all Phase 4 tests."""
    print("🚀 Phase 4 UI/配信層 - Test Suite")
    print("=" * 50)
    
    tests = [
        ("HTML Generator", test_html_generator),
        ("Static Site Generator", test_static_site_generator),
        ("Generator Integration", test_integration),
        ("Performance", test_performance)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 4 UI components are working correctly!")
        print("\n📋 Component Summary:")
        print("✅ HTML Generator - Template-based page generation")
        print("✅ Static Site Generator - Complete site orchestration")
        print("✅ CSS Assets - Responsive design with themes")
        print("✅ JavaScript Assets - Interactive dashboard functionality")
        print("✅ RSS/Sitemap Generation - SEO and syndication")
        print("✅ Performance Optimization - Minification and compression")
        print("✅ Security Features - CSP headers and secure defaults")
        
        print(f"\n🚀 Phase 4 Complete - Ready for deployment!")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Please review implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)