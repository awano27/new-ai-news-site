#!/usr/bin/env python3
"""Test demo site generation to verify everything works."""

import sys
import asyncio
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print("🔍 Testing imports...")
try:
    from src.config.settings import Settings
    from src.models.article import Article
    from src.generators.static_site_generator import StaticSiteGenerator
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_generation():
    """Test generating a minimal demo site."""
    print("\n🚀 Testing demo site generation...")
    
    try:
        # Create settings
        settings = Settings()
        settings.output_dir = "docs"
        
        # Create minimal test article
        article = Article(
            id="test-001",
            title="Test Article: AI News Platform Working",
            url="https://example.com/test",
            source="Test Source",
            source_tier=1,
            content="This is a test article to verify the Daily AI News platform is working correctly."
        )
        article.evaluation = {
            "engineer": {"total_score": 0.85},
            "business": {"total_score": 0.75}
        }
        
        # Initialize generator
        generator = StaticSiteGenerator(settings)
        print("✅ Generator initialized")
        
        # Generate site (without actual file writing for test)
        print("📝 Testing site generation logic...")
        
        # Test CSS generation
        css_content = generator.assets.generate_css()
        assert len(css_content) > 1000, "CSS content too short"
        print(f"✅ CSS generated: {len(css_content)} characters")
        
        # Test JS generation
        js_content = generator.assets.generate_javascript()
        assert len(js_content) > 1000, "JS content too short"
        print(f"✅ JavaScript generated: {len(js_content)} characters")
        
        # Test HTML generation
        html_content = generator.html_generator.generate([article], persona="engineer")
        assert html_content is not None, "HTML generation failed"
        print("✅ HTML generation successful")
        
        print("\n🎉 All tests passed! Ready to generate full demo site.")
        print("\n📋 To generate the actual demo site, run:")
        print("   python generate_demo_site.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_generation())
    if success:
        print("\n✅ Demo generation test successful!")
    else:
        print("\n❌ Demo generation test failed")
    sys.exit(0 if success else 1)