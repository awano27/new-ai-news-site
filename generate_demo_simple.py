#!/usr/bin/env python3
"""Simple demo site generation with error handling."""

import sys
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import Settings
from src.models.article import Article
from src.generators.static_site_generator import StaticSiteGenerator


async def create_simple_articles():
    """Create simple demo articles."""
    articles = []
    
    # Article 1
    article1 = Article(
        id="demo-001",
        title="OpenAI GPT-4 Turbo Released with Enhanced Capabilities",
        url="https://openai.com/blog/gpt-4-turbo-preview",
        source="OpenAI",
        source_tier=1,
        published_date=datetime.now(),
        content="OpenAI has released GPT-4 Turbo with improved instruction following and reduced costs."
    )
    article1.evaluation = {
        "engineer": {"total_score": 0.92},
        "business": {"total_score": 0.88}
    }
    articles.append(article1)
    
    # Article 2
    article2 = Article(
        id="demo-002",
        title="AI Implementation Delivers $50M Cost Savings",
        url="https://example.com/ai-roi-case-study",
        source="TechCorp",
        source_tier=2,
        published_date=datetime.now(),
        content="Enterprise AI implementation shows significant ROI in recent case study."
    )
    article2.evaluation = {
        "engineer": {"total_score": 0.75},
        "business": {"total_score": 0.94}
    }
    articles.append(article2)
    
    return articles


async def main():
    """Generate simple demo site."""
    print("🚀 Generating Simple Demo Site...")
    
    try:
        # Create settings with safe output directory
        settings = Settings()
        
        # Clear any existing files in docs directory first
        docs_dir = Path("docs")
        if docs_dir.exists():
            for file in docs_dir.glob("*.html"):
                if file.exists():
                    try:
                        file.unlink()
                    except PermissionError:
                        print(f"⚠️ Could not remove {file}, continuing...")
        
        settings.output_dir = docs_dir
        
        # Create articles
        articles = await create_simple_articles()
        print(f"📰 Created {len(articles)} demo articles")
        
        # Create generator and generate site
        generator = StaticSiteGenerator(settings)
        
        print("🏗️ Generating site components...")
        
        # Generate CSS manually first
        css_content = generator.assets.generate_css()
        (docs_dir / "styles.css").write_text(css_content, encoding='utf-8')
        print("✅ CSS generated")
        
        # Generate JS manually
        js_content = generator.assets.generate_javascript()
        (docs_dir / "script.js").write_text(js_content, encoding='utf-8')
        print("✅ JavaScript generated")
        
        # Generate HTML directly without file conflicts
        html_generator = generator.html_generator
        
        # Generate the HTML content as string instead of writing to file
        processed_articles = html_generator._process_articles(articles, "engineer")
        summary_stats = html_generator._generate_summary_stats(articles)
        
        articles_html = html_generator._render_articles_grid(processed_articles, "engineer")
        filters_html = html_generator._create_interactive_filters(html_generator._extract_filter_options(articles))
        stats_html = html_generator._render_summary_stats(summary_stats)
        
        dashboard_template = html_generator.template_engine.load_template("dashboard.html")
        dashboard_content = html_generator.template_engine.render(dashboard_template, {
            "articles": articles_html,
            "filters": filters_html,
            "summary_stats": stats_html
        })
        
        page_content = html_generator._generate_complete_page(
            dashboard_content,
            title="Daily AI News - Demo Site",
            description="AI News Demo with Advanced Analytics",
            persona="engineer"
        )
        
        # Write HTML directly
        index_file = docs_dir / "index.html"
        index_file.write_text(page_content, encoding='utf-8')
        print("✅ HTML generated")
        
        # Generate RSS feed
        rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Daily AI News Demo</title>
        <description>Demo AI news feed</description>
        <link>https://example.com</link>
        <item>
            <title>{articles[0].title}</title>
            <description>{articles[0].content[:200]}...</description>
            <link>{articles[0].url}</link>
        </item>
    </channel>
</rss>"""
        (docs_dir / "feed.xml").write_text(rss_content, encoding='utf-8')
        print("✅ RSS feed generated")
        
        # Generate sitemap
        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    </url>
</urlset>"""
        (docs_dir / "sitemap.xml").write_text(sitemap_content, encoding='utf-8')
        print("✅ Sitemap generated")
        
        # List generated files
        generated_files = list(docs_dir.glob("*"))
        print(f"\n📋 Generated {len(generated_files)} files:")
        for file in generated_files:
            size = file.stat().st_size
            print(f"  - {file.name} ({size:,} bytes)")
        
        print(f"\n🎉 Demo site generated successfully!")
        print(f"📁 Files saved to: {docs_dir.absolute()}")
        print(f"🌐 Open docs/index.html in your browser to view the site")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)