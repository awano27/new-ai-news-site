# Daily AI News - GitHub Pages

This directory contains the generated static site for Daily AI News.

## Site Structure

- `index.html` - Main dashboard page
- `styles.css` - Responsive CSS styling  
- `script.js` - Interactive JavaScript functionality
- `feed.xml` - RSS feed for syndication
- `sitemap.xml` - XML sitemap for SEO

## Features

- **Persona-based Optimization**: Switch between Engineer and Business perspectives
- **Interactive Dashboard**: Search, filter, and sort articles
- **Responsive Design**: Optimized for desktop, tablet, and mobile
- **RSS Feed**: Subscribe to daily AI news updates
- **Performance Optimized**: Minified assets and fast loading

## Deployment

This site is automatically deployed via GitHub Actions:
- **Trigger**: Push to main branch or daily schedule (6 AM UTC)
- **Process**: Generate sample articles → Build site → Deploy to Pages
- **URL**: Available at GitHub Pages URL

## Development

To regenerate the site locally:

```bash
python -c "
import asyncio
from src.generators.static_site_generator import StaticSiteGenerator
from src.config.settings import Settings

async def generate():
    settings = Settings()
    settings.output_dir = 'docs'
    generator = StaticSiteGenerator(settings)
    # Add your articles here
    await generator.generate_complete_site(articles)

asyncio.run(generate())
"
```