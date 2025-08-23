#!/usr/bin/env python3
"""Simplified Phase 4 Test - Basic functionality verification."""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import Settings
from src.models.article import Article
from src.generators.html_generator import HTMLGenerator, TemplateEngine
from src.generators.static_site_generator import StaticSiteGenerator, StaticSiteAssets


def test_html_generator():
    """Test basic HTML generator functionality."""
    print("🎨 Testing HTML Generator...")
    
    try:
        settings = Settings()
        generator = HTMLGenerator(settings)
        
        # Create test article
        article = Article(
            id="test-001",
            title="Test AI Article",
            url="https://example.com/test",
            source="Test Source",
            source_tier=1,
            content="This is a test article about AI technology."
        )
        article.evaluation = {
            "engineer": {"total_score": 0.85},
            "business": {"total_score": 0.75}
        }
        
        # Test article card rendering
        card_html = generator._render_article_card(article, persona="engineer")
        assert isinstance(card_html, str)
        assert len(card_html) > 100
        assert "Test AI Article" in card_html
        print("✅ Article card rendering works")
        
        # Test template engine
        template_engine = TemplateEngine(settings)
        template = "<h1>{{title}}</h1>"
        rendered = template_engine.render(template, {"title": "Test Title"})
        assert "Test Title" in rendered
        print("✅ Template engine works")
        
        print("✅ HTML Generator: Basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ HTML Generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_static_site_assets():
    """Test static site assets generation."""
    print("\n🎨 Testing Static Site Assets...")
    
    try:
        settings = Settings()
        assets = StaticSiteAssets(settings)
        
        # Test CSS generation
        css_content = assets.generate_css()
        assert isinstance(css_content, str)
        assert len(css_content) > 1000
        assert ".article-card" in css_content
        assert "@media" in css_content  # Responsive design
        print("✅ CSS generation works")
        
        # Test JavaScript generation  
        js_content = assets.generate_javascript()
        assert isinstance(js_content, str)
        assert len(js_content) > 1000
        assert "DashboardController" in js_content
        assert "switchPersona" in js_content
        print("✅ JavaScript generation works")
        
        print("✅ Static Site Assets: Basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Static Site Assets test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test basic integration."""
    print("\n🔗 Testing Basic Integration...")
    
    try:
        settings = Settings()
        
        # Test that all components can be instantiated
        html_generator = HTMLGenerator(settings)
        site_generator = StaticSiteGenerator(settings)
        assets = StaticSiteAssets(settings)
        
        assert html_generator is not None
        assert site_generator is not None  
        assert assets is not None
        print("✅ All components instantiate correctly")
        
        # Test that site generator has HTML generator
        assert site_generator.html_generator is not None
        assert site_generator.assets is not None
        print("✅ Site generator composition works")
        
        print("✅ Basic Integration: All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Basic Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run simplified Phase 4 tests."""
    print("🚀 Phase 4 Simplified Test Suite")
    print("=" * 40)
    
    tests = [
        ("HTML Generator", test_html_generator),
        ("Static Site Assets", test_static_site_assets), 
        ("Basic Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 4 components are working!")
        print("\n📋 Verified Components:")
        print("✅ HTML Generator - Template rendering")
        print("✅ Static Site Assets - CSS/JS generation")
        print("✅ Component Integration - Composition works")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)