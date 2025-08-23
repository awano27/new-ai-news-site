"""Static Site Generator - Orchestrates complete site generation."""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import shutil
from dataclasses import asdict

from src.config.settings import Settings
from src.models.article import Article
from src.generators.html_generator import HTMLGenerator


class StaticSiteAssets:
    """Manages static assets for the site."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.assets_dir = Path(__file__).parent / "assets"
    
    def generate_css(self, theme: str = "professional") -> str:
        """Generate CSS based on theme."""
        base_css = """
        :root {
            --primary-color: #2563eb;
            --secondary-color: #64748b;
            --accent-color: #f59e0b;
            --background-color: #ffffff;
            --surface-color: #f8fafc;
            --text-color: #1e293b;
            --text-light: #64748b;
            --border-color: #e2e8f0;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--background-color);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        .header {
            background: linear-gradient(135deg, var(--primary-color) 0%, #1e40af 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.125rem;
            opacity: 0.9;
        }
        
        .persona-toggle {
            display: flex;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 0.5rem;
            padding: 0.25rem;
            margin-top: 1rem;
        }
        
        .persona-toggle button {
            flex: 1;
            padding: 0.5rem 1rem;
            border: none;
            background: transparent;
            color: white;
            border-radius: 0.25rem;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .persona-toggle button.active {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .filters {
            background: var(--surface-color);
            padding: 1.5rem;
            border-radius: 0.75rem;
            margin-bottom: 2rem;
            border: 1px solid var(--border-color);
        }
        
        .filter-row {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .filter-group label {
            font-weight: 600;
            color: var(--text-color);
        }
        
        .filter-group select,
        .filter-group input {
            padding: 0.5rem;
            border: 1px solid var(--border-color);
            border-radius: 0.375rem;
            font-size: 0.875rem;
        }
        
        .search-box {
            flex: 1;
            min-width: 250px;
        }
        
        .search-box input {
            width: 100%;
            padding: 0.75rem;
            font-size: 1rem;
            border: 2px solid var(--border-color);
            border-radius: 0.5rem;
            transition: border-color 0.3s;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: var(--primary-color);
        }
        
        .articles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }
        
        .article-card {
            background: white;
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-color);
            transition: all 0.3s;
            position: relative;
        }
        
        .article-card:hover {
            box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.15);
            transform: translateY(-1px);
        }
        
        .article-card .source-tier {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: var(--accent-color);
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 1rem;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .article-card .source-tier.tier-1 {
            background: var(--success-color);
        }
        
        .article-card h3 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            line-height: 1.4;
        }
        
        .article-card h3 a {
            color: var(--text-color);
            text-decoration: none;
            transition: color 0.3s;
        }
        
        .article-card h3 a:hover {
            color: var(--primary-color);
        }
        
        .article-meta {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
            font-size: 0.875rem;
            color: var(--text-light);
        }
        
        .article-content {
            color: var(--text-light);
            margin-bottom: 1rem;
            line-height: 1.6;
        }
        
        .evaluation-scores {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .score-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
        }
        
        .score-bar {
            width: 60px;
            height: 4px;
            background: var(--border-color);
            border-radius: 2px;
            overflow: hidden;
        }
        
        .score-fill {
            height: 100%;
            background: linear-gradient(to right, var(--error-color) 0%, var(--warning-color) 50%, var(--success-color) 100%);
            transition: width 0.3s;
        }
        
        .tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .tag {
            background: var(--surface-color);
            color: var(--text-color);
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.75rem;
            border: 1px solid var(--border-color);
        }
        
        .summary-stats {
            background: var(--surface-color);
            padding: 2rem;
            border-radius: 0.75rem;
            margin-bottom: 2rem;
            border: 1px solid var(--border-color);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-item .value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }
        
        .stat-item .label {
            color: var(--text-light);
            font-size: 0.875rem;
        }
        
        .footer {
            background: var(--surface-color);
            padding: 2rem 0;
            text-align: center;
            color: var(--text-light);
            border-top: 1px solid var(--border-color);
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .filter-row {
                flex-direction: column;
                align-items: stretch;
            }
            
            .search-box {
                min-width: unset;
            }
            
            .articles-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 0 0.5rem;
            }
            
            .article-card {
                padding: 1rem;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* Dark theme overrides */
        [data-theme="dark"] {
            --background-color: #0f172a;
            --surface-color: #1e293b;
            --text-color: #f1f5f9;
            --text-light: #94a3b8;
            --border-color: #334155;
        }
        
        [data-theme="dark"] .article-card {
            background: var(--surface-color);
        }
        
        /* Engineer persona styling */
        .persona-engineer .article-card {
            border-left: 4px solid var(--primary-color);
        }
        
        .persona-engineer .evaluation-scores .engineer {
            font-weight: 600;
            color: var(--primary-color);
        }
        
        /* Business persona styling */
        .persona-business .article-card {
            border-left: 4px solid var(--success-color);
        }
        
        .persona-business .evaluation-scores .business {
            font-weight: 600;
            color: var(--success-color);
        }
        """
        
        if theme == "dark":
            base_css += """
            :root {
                --background-color: #0f172a;
                --surface-color: #1e293b;
                --text-color: #f1f5f9;
                --text-light: #94a3b8;
                --border-color: #334155;
            }
            """
        
        return base_css
    
    def generate_javascript(self) -> str:
        """Generate JavaScript for interactivity."""
        return """
        class DashboardController {
            constructor() {
                this.currentPersona = 'engineer';
                this.articles = [];
                this.filteredArticles = [];
                this.init();
            }
            
            init() {
                this.setupPersonaToggle();
                this.setupFilters();
                this.setupSearch();
                this.loadArticles();
            }
            
            setupPersonaToggle() {
                const toggles = document.querySelectorAll('.persona-toggle button');
                toggles.forEach(toggle => {
                    toggle.addEventListener('click', (e) => {
                        const persona = e.target.dataset.persona;
                        this.switchPersona(persona);
                    });
                });
            }
            
            setupFilters() {
                const filterSelects = document.querySelectorAll('.filter-group select');
                filterSelects.forEach(select => {
                    select.addEventListener('change', () => this.applyFilters());
                });
                
                const scoreInputs = document.querySelectorAll('.filter-group input[type="range"]');
                scoreInputs.forEach(input => {
                    input.addEventListener('input', () => this.applyFilters());
                });
            }
            
            setupSearch() {
                const searchInput = document.querySelector('#search-input');
                if (searchInput) {
                    searchInput.addEventListener('input', (e) => {
                        this.searchArticles(e.target.value);
                    });
                }
            }
            
            switchPersona(persona) {
                this.currentPersona = persona;
                
                // Update active button
                document.querySelectorAll('.persona-toggle button').forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.persona === persona);
                });
                
                // Update body class
                document.body.className = `persona-${persona}`;
                
                // Re-render articles with new persona
                this.renderArticles();
            }
            
            loadArticles() {
                // Get articles data from embedded JSON or API
                const articleData = document.querySelector('#articles-data');
                if (articleData) {
                    this.articles = JSON.parse(articleData.textContent);
                    this.filteredArticles = [...this.articles];
                    this.renderArticles();
                    this.updateSummaryStats();
                }
            }
            
            applyFilters() {
                const sourceTier = document.querySelector('#source-tier-filter')?.value;
                const minScore = parseFloat(document.querySelector('#min-score-filter')?.value || 0);
                const difficultyLevel = document.querySelector('#difficulty-filter')?.value;
                
                this.filteredArticles = this.articles.filter(article => {
                    // Source tier filter
                    if (sourceTier && sourceTier !== 'all' && article.source_tier !== parseInt(sourceTier)) {
                        return false;
                    }
                    
                    // Minimum score filter
                    const score = this.getPersonaScore(article);
                    if (score < minScore) {
                        return false;
                    }
                    
                    // Difficulty filter
                    if (difficultyLevel && difficultyLevel !== 'all' && article.difficulty_level !== difficultyLevel) {
                        return false;
                    }
                    
                    return true;
                });
                
                this.renderArticles();
                this.updateSummaryStats();
            }
            
            searchArticles(query) {
                if (!query.trim()) {
                    this.applyFilters();
                    return;
                }
                
                const lowQuery = query.toLowerCase();
                this.filteredArticles = this.filteredArticles.filter(article => {
                    return article.title.toLowerCase().includes(lowQuery) ||
                           article.content.toLowerCase().includes(lowQuery) ||
                           article.source.toLowerCase().includes(lowQuery) ||
                           (article.tags && article.tags.some(tag => tag.toLowerCase().includes(lowQuery)));
                });
                
                this.renderArticles();
                this.updateSummaryStats();
            }
            
            getPersonaScore(article) {
                if (!article.evaluation) return 0;
                const evaluation = article.evaluation[this.currentPersona];
                return evaluation ? evaluation.total_score : 0;
            }
            
            renderArticles() {
                const container = document.querySelector('.articles-grid');
                if (!container) return;
                
                container.innerHTML = '';
                
                this.filteredArticles
                    .sort((a, b) => this.getPersonaScore(b) - this.getPersonaScore(a))
                    .forEach(article => {
                        container.appendChild(this.createArticleCard(article));
                    });
            }
            
            createArticleCard(article) {
                const card = document.createElement('div');
                card.className = 'article-card';
                
                const score = this.getPersonaScore(article);
                const scorePercentage = Math.round(score * 100);
                
                card.innerHTML = `
                    <div class="source-tier tier-${article.source_tier}">
                        Tier ${article.source_tier}
                    </div>
                    <h3>
                        <a href="${article.url}" target="_blank" rel="noopener noreferrer">
                            ${article.title}
                        </a>
                    </h3>
                    <div class="article-meta">
                        <span>${article.source}</span>
                        <span>•</span>
                        <span>${this.formatDate(article.published_date)}</span>
                    </div>
                    <div class="article-content">
                        ${this.truncateText(article.content, 200)}
                    </div>
                    <div class="evaluation-scores">
                        <div class="score-item ${this.currentPersona}">
                            <span>${this.currentPersona === 'engineer' ? 'Tech' : 'Business'}</span>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${scorePercentage}%"></div>
                            </div>
                            <span>${scorePercentage}%</span>
                        </div>
                    </div>
                    ${article.tags ? `
                        <div class="tags">
                            ${article.tags.slice(0, 5).map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                    ` : ''}
                `;
                
                return card;
            }
            
            formatDate(dateString) {
                if (!dateString) return 'Recent';
                const date = new Date(dateString);
                return date.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric',
                    year: date.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
                });
            }
            
            truncateText(text, maxLength) {
                if (!text || text.length <= maxLength) return text || '';
                return text.substring(0, maxLength).trim() + '...';
            }
            
            updateSummaryStats() {
                const totalElement = document.querySelector('#stat-total');
                const avgScoreElement = document.querySelector('#stat-avg-score');
                const tier1Element = document.querySelector('#stat-tier1');
                
                if (totalElement) {
                    totalElement.textContent = this.filteredArticles.length;
                }
                
                if (avgScoreElement) {
                    const avgScore = this.filteredArticles.reduce((sum, article) => {
                        return sum + this.getPersonaScore(article);
                    }, 0) / this.filteredArticles.length;
                    avgScoreElement.textContent = Math.round((avgScore || 0) * 100) + '%';
                }
                
                if (tier1Element) {
                    const tier1Count = this.filteredArticles.filter(a => a.source_tier === 1).length;
                    tier1Element.textContent = tier1Count;
                }
            }
        }
        
        // Initialize dashboard when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            new DashboardController();
        });
        
        // Theme switching functionality
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }
        
        // Load saved theme
        document.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        });
        """


class StaticSiteGenerator:
    """Orchestrates complete static site generation."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        # Ensure output_dir is a Path object
        self.output_dir = Path(settings.output_dir) if not isinstance(settings.output_dir, Path) else settings.output_dir
        
        # Make sure HTML generator uses the same output directory
        self.settings.output_dir = self.output_dir
        self.html_generator = HTMLGenerator(settings)
        self.assets = StaticSiteAssets(settings)
    
    async def generate_complete_site(
        self,
        articles: List[Article],
        persona: str = "engineer",
        include_interactive: bool = True,
        include_rss: bool = False,
        include_sitemap: bool = False,
        optimize: bool = False,
        secure: bool = False
    ) -> Dict[str, Any]:
        """Generate complete static site with all components."""
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate main HTML
        # HTMLGenerator already writes to file and returns the path
        html_path = self.html_generator.generate(articles, persona)
        
        # No need to copy since the file is already written
        index_file = self.output_dir / "index.html"
        
        # Generate CSS
        css_content = self.assets.generate_css(
            theme=getattr(self.settings, 'ui_theme', 'professional')
        )
        (self.output_dir / "styles.css").write_text(css_content, encoding='utf-8')
        
        # Generate JavaScript if interactive
        if include_interactive:
            js_content = self.assets.generate_javascript()
            (self.output_dir / "script.js").write_text(js_content, encoding='utf-8')
        
        # Generate RSS feed if requested
        if include_rss:
            await self._generate_rss_feed(articles)
        
        # Generate sitemap if requested
        if include_sitemap:
            await self._generate_sitemap()
        
        # Optimize files if requested
        if optimize:
            await self._optimize_site()
        
        # Add security headers if requested
        if secure:
            await self._add_security_features()
        
        return {
            "status": "success",
            "output_dir": str(self.output_dir),
            "files_generated": self._get_generated_files(),
            "total_articles": len(articles),
            "generation_time": datetime.now().isoformat()
        }
    
    async def _generate_rss_feed(self, articles: List[Article]) -> None:
        """Generate RSS feed."""
        rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>Daily AI News</title>
        <description>Curated AI news and insights for technical and business professionals</description>
        <link>{getattr(self.settings, 'base_url', 'https://example.com')}</link>
        <atom:link href="{getattr(self.settings, 'base_url', 'https://example.com')}/feed.xml" rel="self" type="application/rss+xml"/>
        <language>en-us</language>
        <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate>
        <generator>Daily AI News Generator</generator>
"""
        
        for article in articles[:20]:  # Latest 20 articles
            rss_content += f"""
        <item>
            <title><![CDATA[{article.title}]]></title>
            <description><![CDATA[{article.content[:500]}...]]></description>
            <link>{article.url}</link>
            <guid>{article.url}</guid>
            <pubDate>{article.published_date.strftime('%a, %d %b %Y %H:%M:%S %z') if article.published_date else ''}</pubDate>
            <source url="{article.url}">{article.source}</source>
        </item>"""
        
        rss_content += """
    </channel>
</rss>"""
        
        (self.output_dir / "feed.xml").write_text(rss_content, encoding='utf-8')
    
    async def _generate_sitemap(self) -> None:
        """Generate XML sitemap."""
        base_url = getattr(self.settings, 'base_url', 'https://example.com')
        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{base_url}/</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
        
        (self.output_dir / "sitemap.xml").write_text(sitemap_content, encoding='utf-8')
    
    async def _optimize_site(self) -> None:
        """Optimize generated files for performance."""
        # Minify HTML
        index_file = self.output_dir / "index.html"
        if index_file.exists():
            content = index_file.read_text(encoding='utf-8')
            # Basic minification - remove extra whitespace
            import re
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r'>\s+<', '><', content)
            index_file.write_text(content, encoding='utf-8')
        
        # Minify CSS
        css_file = self.output_dir / "styles.css"
        if css_file.exists():
            content = css_file.read_text(encoding='utf-8')
            # Basic CSS minification
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r';\s*}', '}', content)
            content = re.sub(r'{\s*', '{', content)
            css_file.write_text(content, encoding='utf-8')
    
    async def _add_security_features(self) -> None:
        """Add security features to the site."""
        index_file = self.output_dir / "index.html"
        if index_file.exists():
            content = index_file.read_text(encoding='utf-8')
            
            # Add CSP meta tag if not present
            if 'content-security-policy' not in content.lower():
                csp_meta = '''<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;">'''
                content = content.replace('<head>', f'<head>\n    {csp_meta}')
                index_file.write_text(content, encoding='utf-8')
    
    def _get_generated_files(self) -> List[str]:
        """Get list of generated files."""
        files = []
        for file_path in self.output_dir.rglob('*'):
            if file_path.is_file():
                files.append(str(file_path.relative_to(self.output_dir)))
        return sorted(files)
    
    async def generate_persona_specific_pages(
        self,
        articles: List[Article],
        personas: List[str] = ["engineer", "business"]
    ) -> Dict[str, str]:
        """Generate persona-specific pages."""
        results = {}
        
        for persona in personas:
            # Generate persona-specific content
            html_content = self.html_generator.generate(articles, persona)
            
            # Save to persona-specific file
            filename = f"{persona}.html"
            file_path = self.output_dir / filename
            
            if isinstance(html_content, Path):
                shutil.copy2(html_content, file_path)
            else:
                file_path.write_text(html_content, encoding='utf-8')
            
            results[persona] = str(file_path)
        
        return results
    
    async def generate_archive_pages(
        self,
        articles: List[Article],
        group_by: str = "date"  # "date", "source", "tier"
    ) -> Dict[str, List[str]]:
        """Generate archive pages grouped by specified criteria."""
        from collections import defaultdict
        
        archives = defaultdict(list)
        
        # Group articles
        for article in articles:
            if group_by == "date" and article.published_date:
                key = article.published_date.strftime("%Y-%m")
            elif group_by == "source":
                key = article.source
            elif group_by == "tier":
                key = f"tier-{article.source_tier}"
            else:
                key = "general"
            
            archives[key].append(article)
        
        # Generate pages for each group
        results = {}
        archive_dir = self.output_dir / "archives"
        archive_dir.mkdir(exist_ok=True)
        
        for group_key, group_articles in archives.items():
            html_content = self.html_generator.generate(group_articles)
            filename = f"{group_by}-{group_key}.html"
            file_path = archive_dir / filename
            
            if isinstance(html_content, Path):
                shutil.copy2(html_content, file_path)
            else:
                file_path.write_text(html_content, encoding='utf-8')
            
            if group_by not in results:
                results[group_by] = []
            results[group_by].append(str(file_path))
        
        return results