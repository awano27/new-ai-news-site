"""HTML Generator for creating rich, interactive web interfaces."""

import re
import json
import math
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import hashlib

from src.config.settings import Settings
from src.models.article import Article


class TemplateEngine:
    """Lightweight template engine for HTML generation."""
    
    def __init__(self, settings: Settings):
        """Initialize template engine."""
        self.settings = settings
        self.template_cache = {}
    
    def load_template(self, template_name: str) -> str:
        """Load template from file or return default."""
        # Ensure template_dir exists
        if hasattr(self.settings, 'template_dir') and self.settings.template_dir:
            template_path = self.settings.template_dir / template_name
            
            if template_path.exists():
                if template_name not in self.template_cache:
                    self.template_cache[template_name] = template_path.read_text(encoding='utf-8')
                return self.template_cache[template_name]
        
        # Return default template if file not found or template_dir not set
        return self._get_default_template(template_name)
    
    def _get_default_template(self, template_name: str) -> str:
        """Get default template if file not found."""
        templates = {
            "base.html": """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <meta name="description" content="{{description}}">
    <meta property="og:title" content="{{title}}">
    <meta property="og:description" content="{{description}}">
    <style>{{styles}}</style>
</head>
<body>
    <div id="app">{{content}}</div>
    <script>{{scripts}}</script>
</body>
</html>""",
            
            "article_card.html": """<article class="article-card {{persona}}-focused" data-score="{{total_score}}">
    <header class="article-header">
        <h2 class="article-title">{{title}}</h2>
        <div class="article-meta">
            <span class="source tier-{{source_tier}}">{{source}}</span>
            <time class="publish-date">{{publish_date}}</time>
        </div>
    </header>
    
    <div class="evaluation-display">
        <div class="score-card">
            <div class="total-score">{{total_score}}</div>
            <div class="score-label">総合スコア</div>
        </div>
        <div class="breakdown-viz">{{score_breakdown}}</div>
    </div>
    
    <div class="article-content">
        <p class="article-summary">{{summary}}</p>
        {{feature_highlights}}
    </div>
    
    <footer class="article-actions">
        <a href="{{url}}" class="read-more" target="_blank">詳細を読む</a>
        <div class="article-tools">
            {{action_buttons}}
        </div>
    </footer>
</article>""",
            
            "dashboard.html": """<div class="dashboard">
    <header class="dashboard-header">
        <h1>Daily AI News Dashboard</h1>
        <div class="persona-toggle">
            <button class="toggle-btn active" data-persona="engineer">エンジニア</button>
            <button class="toggle-btn" data-persona="business">ビジネス</button>
        </div>
    </header>
    
    <div class="dashboard-stats">{{summary_stats}}</div>
    
    <div class="dashboard-controls">
        <div class="search-box">
            <input type="search" id="search" placeholder="記事を検索...">
        </div>
        <div class="filters">{{filters}}</div>
    </div>
    
    <main class="articles-container">
        <div class="articles-grid">{{articles}}</div>
    </main>
</div>"""
        }
        
        return templates.get(template_name, "<div>Template not found: {{content}}</div>")
    
    def render(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template with variables."""
        rendered = template
        
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            elif value is None:
                value = ""
            else:
                value = str(value)
            
            rendered = rendered.replace(placeholder, value)
        
        return rendered
    
    def render_with_inheritance(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template with inheritance support."""
        # Simple inheritance: {{extends:template_name}}
        extends_match = re.search(r'\{\{extends:(\w+)\}\}', template)
        if extends_match:
            base_template_name = extends_match.group(1) + ".html"
            base_template = self.load_template(base_template_name)
            
            # Replace content block
            content = template.replace(extends_match.group(0), "")
            variables["content"] = content
            
            return self.render(base_template, variables)
        
        return self.render(template, variables)
    
    def render_with_filters(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template with custom filters."""
        # Simple filter support: {{value|filter_name}}
        def apply_filters(text: str) -> str:
            filter_pattern = r'\{\{([^|]+)\|([^}]+)\}\}'
            
            def filter_replacer(match):
                var_name = match.group(1).strip()
                filter_name = match.group(2).strip()
                
                if var_name in variables:
                    value = variables[var_name]
                    return self._apply_filter(value, filter_name)
                return match.group(0)
            
            return re.sub(filter_pattern, filter_replacer, text)
        
        filtered_template = apply_filters(template)
        return self.render(filtered_template, variables)
    
    def _apply_filter(self, value: Any, filter_name: str) -> str:
        """Apply custom filter to value."""
        if filter_name == "currency":
            return f"${value:,.2f}" if isinstance(value, (int, float)) else str(value)
        elif filter_name.startswith("truncate:"):
            length = int(filter_name.split(":")[1])
            text = str(value)
            return text[:length] + "..." if len(text) > length else text
        elif filter_name == "percentage":
            return f"{value:.1%}" if isinstance(value, (int, float)) else str(value)
        elif filter_name == "date":
            if isinstance(value, datetime):
                return value.strftime("%Y年%m月%d日")
        
        return str(value)


class HTMLGenerator:
    """Generate rich HTML interfaces for Daily AI News."""
    
    def __init__(self, settings: Settings):
        """Initialize HTML generator."""
        self.settings = settings
        self.template_engine = TemplateEngine(settings)
        
        # Theme configuration
        self.themes = {
            "light": {
                "primary": "#0f172a",
                "accent": "#3b82f6", 
                "background": "#ffffff",
                "text": "#1f2937"
            },
            "dark": {
                "primary": "#f8fafc",
                "accent": "#60a5fa",
                "background": "#0f172a", 
                "text": "#f8fafc"
            },
            "professional": {
                "primary": "#1e293b",
                "accent": "#0ea5e9",
                "background": "#f8fafc",
                "text": "#334155"
            }
        }
    
    def generate(self, articles: List[Article], persona: str = "engineer") -> Path:
        """Generate complete HTML dashboard."""
        # Prepare data
        processed_articles = self._process_articles(articles, persona)
        summary_stats = self._generate_summary_stats(articles)
        
        # Generate components
        articles_html = self._render_articles_grid(processed_articles, persona)
        filters_html = self._create_interactive_filters(self._extract_filter_options(articles))
        stats_html = self._render_summary_stats(summary_stats)
        
        # Load and render main template
        dashboard_template = self.template_engine.load_template("dashboard.html")
        
        dashboard_content = self.template_engine.render(dashboard_template, {
            "articles": articles_html,
            "filters": filters_html,
            "summary_stats": stats_html
        })
        
        # Generate complete page
        page_content = self._generate_complete_page(
            dashboard_content,
            title="Daily AI News - AI情報の質的評価プラットフォーム",
            description="AIエンジニアとビジネスマン向けに厳選されたAI情報を、独自の多層評価システムで分析・提供",
            persona=persona,
            articles=articles
        )
        
        # Write to output file
        # Ensure output_dir is a Path object
        output_dir = Path(self.settings.output_dir) if not isinstance(self.settings.output_dir, Path) else self.settings.output_dir
        output_path = output_dir / "index.html"
        output_path.write_text(page_content, encoding='utf-8')
        
        # Generate additional files
        self._generate_static_assets()
        
        return output_path
    
    def _process_articles(self, articles: List[Article], persona: str) -> List[Dict[str, Any]]:
        """Process articles for display."""
        processed = []
        
        for article in articles:
            # Get evaluation data
            evaluation = getattr(article, 'evaluation', {})
            persona_eval = evaluation.get(persona, {})
            
            processed_article = {
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "source_tier": article.source_tier,
                "publish_date": article.published_date.strftime("%Y/%m/%d") if article.published_date else "日付不明",
                "summary": article.content[:200] + "..." if len(article.content) > 200 else article.content,
                "total_score": persona_eval.get('total_score', 0.0),
                "breakdown": persona_eval.get('breakdown', {}),
                "recommendation": persona_eval.get('recommendation', 'consider'),
                
                # Advanced features integration
                "difficulty_analysis": self._extract_difficulty_info(article),
                "roi_analysis": self._extract_roi_info(article),
                "bias_analysis": self._extract_bias_info(article),
                
                # Metadata
                "personas": persona,
                "tags": getattr(article, 'tags', []),
                "entities": {
                    "companies": article.entities.companies[:3] if article.entities.companies else [],
                    "technologies": article.entities.technologies[:3] if article.entities.technologies else []
                }
            }
            
            processed.append(processed_article)
        
        # Sort by total score (descending)
        processed.sort(key=lambda x: x['total_score'], reverse=True)
        return processed
    
    def _render_article_card(self, article: Union[Article, Dict], persona: str = "engineer") -> str:
        """Render individual article card."""
        if isinstance(article, Article):
            article_data = self._process_articles([article], persona)[0]
        else:
            article_data = article
        
        # Generate evaluation visualization
        score_breakdown = self._generate_evaluation_viz(article_data['breakdown'], persona)
        
        # Generate feature highlights
        feature_highlights = self._generate_feature_highlights(article_data, persona)
        
        # Generate action buttons
        action_buttons = self._generate_action_buttons(article_data, persona)
        
        # Load and render template
        card_template = self.template_engine.load_template("article_card.html")
        
        variables = {
            **article_data,
            "persona": persona,
            "score_breakdown": score_breakdown,
            "feature_highlights": feature_highlights,
            "action_buttons": action_buttons,
            "total_score": f"{article_data['total_score']:.2f}"
        }
        
        return self.template_engine.render(card_template, variables)
    
    def _generate_evaluation_viz(self, breakdown: Dict[str, float], persona: str) -> str:
        """Generate evaluation score visualization."""
        if not breakdown:
            return "<div class='no-evaluation'>評価データなし</div>"
        
        # Create radar chart data
        labels = []
        values = []
        
        if persona == "engineer":
            mapping = {
                "technical_depth": "技術的深度",
                "implementation": "実装可能性", 
                "novelty": "新規性",
                "reproducibility": "再現性",
                "community_impact": "コミュニティ影響"
            }
        else:
            mapping = {
                "business_impact": "ビジネス影響",
                "roi_potential": "ROI可能性",
                "market_validation": "市場検証",
                "implementation_ease": "導入容易性",
                "strategic_value": "戦略的価値"
            }
        
        for key, label in mapping.items():
            if key in breakdown:
                labels.append(label)
                values.append(breakdown[key])
        
        # Generate simple bar visualization (can be enhanced with Chart.js)
        viz_html = "<div class='score-breakdown'>"
        
        for i, (label, value) in enumerate(zip(labels, values)):
            percentage = int(value * 100)
            viz_html += f"""
            <div class='score-item'>
                <span class='score-label'>{label}</span>
                <div class='score-bar'>
                    <div class='score-fill' style='width: {percentage}%'></div>
                    <span class='score-value'>{percentage}%</span>
                </div>
            </div>
            """
        
        viz_html += "</div>"
        return viz_html
    
    def _generate_feature_highlights(self, article_data: Dict, persona: str) -> str:
        """Generate feature-specific highlights."""
        highlights = []
        
        # Difficulty analysis highlights
        difficulty = article_data.get('difficulty_analysis', {})
        if difficulty.get('difficulty_level'):
            level = difficulty['difficulty_level']
            level_ja = {"beginner": "初級", "intermediate": "中級", "advanced": "上級", "research": "研究レベル"}
            highlights.append(f"<span class='difficulty-badge {level}'>実装難易度: {level_ja.get(level, level)}</span>")
        
        # ROI analysis highlights
        roi = article_data.get('roi_analysis', {})
        if roi.get('confidence_score', 0) > 0.7:
            highlights.append("<span class='roi-badge high'>高ROI期待値</span>")
        
        # Bias analysis highlights
        bias = article_data.get('bias_analysis', {})
        if bias.get('neutrality_score', 0) > 0.8:
            highlights.append("<span class='quality-badge high'>高品質コンテンツ</span>")
        
        # Technology highlights
        if article_data['entities']['technologies']:
            tech_tags = ", ".join(article_data['entities']['technologies'])
            highlights.append(f"<span class='tech-tags'>技術: {tech_tags}</span>")
        
        return "<div class='feature-highlights'>" + " ".join(highlights) + "</div>"
    
    def _generate_action_buttons(self, article_data: Dict, persona: str) -> str:
        """Generate action buttons for article."""
        buttons = []
        
        # Bookmark button
        buttons.append(f"<button class='action-btn bookmark' data-article='{article_data['id']}'>ブックマーク</button>")
        
        # Share button
        buttons.append(f"<button class='action-btn share' data-url='{article_data['url']}'>共有</button>")
        
        # Persona-specific actions
        if persona == "engineer" and article_data.get('difficulty_analysis', {}).get('github_repo'):
            buttons.append("<button class='action-btn github'>GitHub</button>")
        
        if persona == "business" and article_data.get('roi_analysis', {}).get('confidence_score', 0) > 0.6:
            buttons.append("<button class='action-btn roi-calc'>ROI計算</button>")
        
        return " ".join(buttons)
    
    def _render_articles_grid(self, articles: List[Dict], persona: str) -> str:
        """Render grid of article cards."""
        cards = []
        
        for article in articles[:20]:  # Limit to top 20 articles
            card_html = self._render_article_card(article, persona)
            cards.append(card_html)
        
        return "\n".join(cards)
    
    def _generate_summary_stats(self, articles: List[Article]) -> Dict[str, Any]:
        """Generate summary statistics."""
        if not articles:
            return {"total_articles": 0, "avg_engineer_score": 0, "avg_business_score": 0}
        
        total = len(articles)
        engineer_scores = []
        business_scores = []
        
        for article in articles:
            evaluation = getattr(article, 'evaluation', {})
            if 'engineer' in evaluation and 'total_score' in evaluation['engineer']:
                engineer_scores.append(evaluation['engineer']['total_score'])
            if 'business' in evaluation and 'total_score' in evaluation['business']:
                business_scores.append(evaluation['business']['total_score'])
        
        return {
            "total_articles": total,
            "avg_engineer_score": sum(engineer_scores) / len(engineer_scores) if engineer_scores else 0,
            "avg_business_score": sum(business_scores) / len(business_scores) if business_scores else 0,
            "high_quality_count": sum(1 for s in engineer_scores + business_scores if s > 0.8),
            "sources_count": len(set(article.source for article in articles if article.source))
        }
    
    def _render_summary_stats(self, stats: Dict[str, Any]) -> str:
        """Render summary statistics display."""
        return f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats['total_articles']}</div>
                <div class="stat-label">総記事数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['avg_engineer_score']:.2f}</div>
                <div class="stat-label">エンジニア平均スコア</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['avg_business_score']:.2f}</div>
                <div class="stat-label">ビジネス平均スコア</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['high_quality_count']}</div>
                <div class="stat-label">高品質記事数</div>
            </div>
        </div>
        """
    
    def _create_interactive_filters(self, filter_options: Dict[str, Any]) -> str:
        """Create interactive filter controls."""
        filters_html = []
        
        # Source tier filter
        if 'source_tiers' in filter_options:
            tiers = filter_options['source_tiers']
            options = "".join(f"<option value='{tier}'>Tier {tier}</option>" for tier in tiers)
            filters_html.append(f"""
            <div class="filter-group">
                <label for="tier-filter">情報源ティア</label>
                <select id="tier-filter" class="filter-select">
                    <option value="">すべて</option>
                    {options}
                </select>
            </div>
            """)
        
        # Score range filter
        filters_html.append(f"""
        <div class="filter-group">
            <label for="score-filter">最小スコア</label>
            <input type="range" id="score-filter" class="filter-range" 
                   min="0" max="1" step="0.1" value="0">
            <span class="range-value">0.0</span>
        </div>
        """)
        
        # Difficulty filter (for engineers)
        if 'difficulty_levels' in filter_options:
            levels = filter_options['difficulty_levels']
            options = "".join(f"<option value='{level}'>{level}</option>" for level in levels)
            filters_html.append(f"""
            <div class="filter-group engineer-only">
                <label for="difficulty-filter">実装難易度</label>
                <select id="difficulty-filter" class="filter-select">
                    <option value="">すべて</option>
                    {options}
                </select>
            </div>
            """)
        
        return "<div class='filters-container'>" + "".join(filters_html) + "</div>"
    
    def _extract_filter_options(self, articles: List[Article]) -> Dict[str, Any]:
        """Extract available filter options from articles."""
        options = {
            "source_tiers": sorted(set(article.source_tier for article in articles if article.source_tier)),
            "sources": sorted(set(article.source for article in articles if article.source)),
            "difficulty_levels": ["beginner", "intermediate", "advanced", "research"]
        }
        return options
    
    def _generate_complete_page(self, content: str, title: str, description: str, persona: str = "engineer", articles: List[Article] = None) -> str:
        """Generate complete HTML page."""
        # Load base template
        base_template = self.template_engine.load_template("base.html")
        
        # Generate CSS
        styles = self._generate_css(persona)
        
        # Generate JavaScript
        scripts = self._generate_javascript(persona)
        
        # Add articles data as JSON for JavaScript consumption
        articles_json = ""
        if articles:
            processed_articles = self._process_articles(articles, persona)
            articles_json = f'<script id="articles-data" type="application/json">{json.dumps(processed_articles, ensure_ascii=False, indent=2)}</script>'
        
        # Embed articles JSON data before content
        full_content = articles_json + content
        
        # Render complete page
        return self.template_engine.render(base_template, {
            "title": title,
            "description": description,
            "content": full_content,
            "styles": styles,
            "scripts": scripts
        })
    
    def _generate_css(self, persona: str = "engineer") -> str:
        """Generate CSS styles."""
        theme = self.themes.get("professional", self.themes["light"])
        persona_accent = "#3b82f6" if persona == "engineer" else "#10b981"
        
        return f"""
        :root {{
            --primary: {theme['primary']};
            --accent: {persona_accent};
            --background: {theme['background']};
            --text: {theme['text']};
            --border: #e2e8f0;
            --shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--background);
            color: var(--text);
            line-height: 1.6;
        }}
        
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .dashboard-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--border);
        }}
        
        .dashboard-header h1 {{
            font-size: 2rem;
            color: var(--primary);
        }}
        
        .persona-toggle {{
            display: flex;
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .toggle-btn {{
            background: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .toggle-btn.active {{
            background: var(--accent);
            color: white;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: var(--shadow);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--accent);
        }}
        
        .dashboard-controls {{
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        
        .search-box input {{
            padding: 12px 16px;
            border: 1px solid var(--border);
            border-radius: 8px;
            width: 300px;
            font-size: 16px;
        }}
        
        .filters-container {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        
        .filter-select, .filter-range {{
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
        }}
        
        .articles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 25px;
        }}
        
        .article-card {{
            background: white;
            border-radius: 12px;
            box-shadow: var(--shadow);
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .article-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .article-header {{
            padding: 20px 20px 15px;
        }}
        
        .article-title {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 10px;
            line-height: 1.4;
        }}
        
        .article-meta {{
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            color: #6b7280;
        }}
        
        .source {{
            background: var(--accent);
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
        }}
        
        .evaluation-display {{
            display: flex;
            align-items: center;
            padding: 15px 20px;
            background: #f8f9fa;
        }}
        
        .score-card {{
            text-align: center;
            margin-right: 20px;
        }}
        
        .total-score {{
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--accent);
        }}
        
        .score-label {{
            font-size: 0.8rem;
            color: #6b7280;
        }}
        
        .score-breakdown {{
            flex: 1;
        }}
        
        .score-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 5px;
        }}
        
        .score-label {{
            min-width: 80px;
            font-size: 0.8rem;
        }}
        
        .score-bar {{
            flex: 1;
            height: 6px;
            background: #e5e7eb;
            border-radius: 3px;
            position: relative;
        }}
        
        .score-fill {{
            height: 100%;
            background: var(--accent);
            border-radius: 3px;
            transition: width 0.3s;
        }}
        
        .score-value {{
            font-size: 0.8rem;
            color: #6b7280;
            min-width: 35px;
        }}
        
        .article-content {{
            padding: 15px 20px;
        }}
        
        .article-summary {{
            margin-bottom: 15px;
            color: #4b5563;
            line-height: 1.5;
        }}
        
        .feature-highlights {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }}
        
        .difficulty-badge, .roi-badge, .quality-badge, .tech-tags {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .difficulty-badge.beginner {{ background: #dcfce7; color: #16a34a; }}
        .difficulty-badge.intermediate {{ background: #fef3c7; color: #d97706; }}
        .difficulty-badge.advanced {{ background: #fee2e2; color: #dc2626; }}
        .difficulty-badge.research {{ background: #f3e8ff; color: #9333ea; }}
        
        .roi-badge.high {{ background: #dcfce7; color: #16a34a; }}
        .quality-badge.high {{ background: #dbeafe; color: #2563eb; }}
        .tech-tags {{ background: #f1f5f9; color: #475569; }}
        
        .article-actions {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            border-top: 1px solid var(--border);
        }}
        
        .read-more {{
            background: var(--accent);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: opacity 0.2s;
        }}
        
        .read-more:hover {{
            opacity: 0.9;
        }}
        
        .article-tools {{
            display: flex;
            gap: 8px;
        }}
        
        .action-btn {{
            background: none;
            border: 1px solid var(--border);
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.2s;
        }}
        
        .action-btn:hover {{
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }}
        
        @media (max-width: 768px) {{
            .dashboard {{
                padding: 10px;
            }}
            
            .dashboard-header {{
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }}
            
            .dashboard-controls {{
                flex-direction: column;
            }}
            
            .search-box input {{
                width: 100%;
            }}
            
            .articles-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        """
    
    def _generate_javascript(self, persona: str = "engineer") -> str:
        """Generate JavaScript functionality."""
        return """
        // Article filtering and search functionality
        class DashboardController {
            constructor() {
                this.currentPersona = '""" + persona + """';
                this.articles = [];
                this.filteredArticles = [];
                this.init();
            }
            
            init() {
                this.bindEvents();
                this.loadArticles();
            }
            
            bindEvents() {
                // Persona toggle
                document.querySelectorAll('.toggle-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => this.switchPersona(e.target.dataset.persona));
                });
                
                // Search
                const searchInput = document.getElementById('search');
                if (searchInput) {
                    searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
                }
                
                // Filters
                document.querySelectorAll('.filter-select, .filter-range').forEach(filter => {
                    filter.addEventListener('change', () => this.applyFilters());
                });
                
                // Action buttons
                document.addEventListener('click', (e) => {
                    if (e.target.classList.contains('bookmark')) {
                        this.bookmarkArticle(e.target.dataset.article);
                    } else if (e.target.classList.contains('share')) {
                        this.shareArticle(e.target.dataset.url);
                    }
                });
            }
            
            loadArticles() {
                // Extract article data from DOM
                this.articles = Array.from(document.querySelectorAll('.article-card')).map(card => ({
                    element: card,
                    id: card.dataset.id || '',
                    score: parseFloat(card.dataset.score) || 0,
                    title: card.querySelector('.article-title')?.textContent || '',
                    source: card.querySelector('.source')?.textContent || '',
                    tier: parseInt(card.querySelector('.source').className.match(/tier-(\\d)/)?.[1]) || 3
                }));
                
                this.filteredArticles = [...this.articles];
            }
            
            switchPersona(persona) {
                if (persona === this.currentPersona) return;
                
                this.currentPersona = persona;
                
                // Update UI
                document.querySelectorAll('.toggle-btn').forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.persona === persona);
                });
                
                // Show/hide persona-specific elements
                document.querySelectorAll('.engineer-only').forEach(el => {
                    el.style.display = persona === 'engineer' ? 'block' : 'none';
                });
                
                document.querySelectorAll('.business-only').forEach(el => {
                    el.style.display = persona === 'business' ? 'block' : 'none';
                });
                
                // Re-apply filters
                this.applyFilters();
            }
            
            handleSearch(query) {
                const searchTerm = query.toLowerCase().trim();
                
                this.filteredArticles = this.articles.filter(article => {
                    return article.title.toLowerCase().includes(searchTerm);
                });
                
                this.updateDisplay();
            }
            
            applyFilters() {
                let filtered = [...this.articles];
                
                // Score filter
                const scoreFilter = document.getElementById('score-filter');
                if (scoreFilter) {
                    const minScore = parseFloat(scoreFilter.value);
                    filtered = filtered.filter(article => article.score >= minScore);
                    
                    // Update range display
                    const rangeValue = scoreFilter.parentNode.querySelector('.range-value');
                    if (rangeValue) {
                        rangeValue.textContent = minScore.toFixed(1);
                    }
                }
                
                // Tier filter
                const tierFilter = document.getElementById('tier-filter');
                if (tierFilter && tierFilter.value) {
                    const selectedTier = parseInt(tierFilter.value);
                    filtered = filtered.filter(article => article.tier === selectedTier);
                }
                
                // Difficulty filter (engineer only)
                const difficultyFilter = document.getElementById('difficulty-filter');
                if (difficultyFilter && difficultyFilter.value && this.currentPersona === 'engineer') {
                    const selectedDifficulty = difficultyFilter.value;
                    filtered = filtered.filter(article => {
                        const badge = article.element.querySelector('.difficulty-badge');
                        return badge && badge.classList.contains(selectedDifficulty);
                    });
                }
                
                this.filteredArticles = filtered;
                this.updateDisplay();
            }
            
            updateDisplay() {
                // Show/hide articles based on filter
                this.articles.forEach(article => {
                    const shouldShow = this.filteredArticles.includes(article);
                    article.element.style.display = shouldShow ? 'block' : 'none';
                });
                
                // Update count display
                const totalCount = this.filteredArticles.length;
                const countDisplay = document.querySelector('.results-count');
                if (countDisplay) {
                    countDisplay.textContent = `${totalCount}件の記事`;
                }
            }
            
            bookmarkArticle(articleId) {
                // Save to localStorage
                const bookmarks = JSON.parse(localStorage.getItem('bookmarks') || '[]');
                if (!bookmarks.includes(articleId)) {
                    bookmarks.push(articleId);
                    localStorage.setItem('bookmarks', JSON.stringify(bookmarks));
                    
                    // Update UI
                    const btn = document.querySelector(`[data-article="${articleId}"]`);
                    if (btn) {
                        btn.textContent = 'ブックマーク済み';
                        btn.classList.add('bookmarked');
                    }
                }
            }
            
            shareArticle(url) {
                if (navigator.share) {
                    navigator.share({
                        title: 'Daily AI News',
                        url: url
                    });
                } else {
                    // Fallback: copy to clipboard
                    navigator.clipboard.writeText(url).then(() => {
                        alert('URLをコピーしました');
                    });
                }
            }
        }
        
        // Initialize when DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {
            new DashboardController();
        });
        """
    
    def _generate_static_assets(self) -> None:
        """Generate additional static assets."""
        # Ensure output_dir is a Path object
        output_dir = Path(self.settings.output_dir) if not isinstance(self.settings.output_dir, Path) else self.settings.output_dir
        
        # Generate separate CSS file
        css_content = self._generate_css()
        css_path = output_dir / "styles.css"
        css_path.write_text(css_content, encoding='utf-8')
        
        # Generate separate JS file
        js_content = self._generate_javascript()
        js_path = output_dir / "script.js"
        js_path.write_text(js_content, encoding='utf-8')
        
        # Generate manifest.json for PWA
        manifest = {
            "name": "Daily AI News",
            "short_name": "AI News",
            "description": "AI情報の質的評価プラットフォーム",
            "start_url": "./",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#3b82f6",
            "icons": [
                {
                    "src": "icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                }
            ]
        }
        
        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def _generate_rss_feed(self, articles: List[Article]) -> str:
        """Generate RSS feed."""
        items = []
        for article in articles[:20]:  # Latest 20 articles
            pub_date = article.published_date.strftime("%a, %d %b %Y %H:%M:%S +0000") if article.published_date else ""
            description = article.content[:500] + "..." if len(article.content) > 500 else article.content
            
            item = f"""
            <item>
                <title><![CDATA[{article.title}]]></title>
                <link>{article.url}</link>
                <description><![CDATA[{description}]]></description>
                <pubDate>{pub_date}</pubDate>
                <guid isPermaLink="true">{article.url}</guid>
                <source><![CDATA[{article.source}]]></source>
            </item>
            """
            items.append(item)
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Daily AI News</title>
        <link>https://your-domain.github.io/daily-ai-news</link>
        <description>AIエンジニアとビジネスマン向けの厳選AI情報</description>
        <language>ja</language>
        <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
        {"".join(items)}
    </channel>
</rss>"""
    
    def _create_sitemap(self, articles: List[Article]) -> str:
        """Create XML sitemap."""
        urls = [
            f"""
            <url>
                <loc>https://your-domain.github.io/daily-ai-news/</loc>
                <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
                <priority>1.0</priority>
            </url>
            """
        ]
        
        for article in articles:
            if article.url and article.published_date:
                lastmod = article.published_date.strftime("%Y-%m-%d")
                urls.append(f"""
                <url>
                    <loc>{article.url}</loc>
                    <lastmod>{lastmod}</lastmod>
                    <priority>0.8</priority>
                </url>
                """)
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {"".join(urls)}
</urlset>"""
    
    def _optimize_html(self, html: str) -> str:
        """Optimize HTML for performance."""
        # Remove extra whitespace
        html = re.sub(r'\s+', ' ', html)
        html = re.sub(r'>\s+<', '><', html)
        
        # Merge style blocks
        styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
        if len(styles) > 1:
            merged_styles = " ".join(styles)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
            html = html.replace('</head>', f'<style>{merged_styles}</style></head>')
        
        return html
    
    def _apply_persona_styling(self, html: str, persona: str) -> str:
        """Apply persona-specific styling."""
        if persona == "engineer":
            html = html.replace("{{persona_class}}", "engineer-focused")
            html = html.replace("{{accent_color}}", "#3b82f6")
        else:
            html = html.replace("{{persona_class}}", "business-focused") 
            html = html.replace("{{accent_color}}", "#10b981")
        
        return html
    
    def _apply_theme(self, articles: List[Article], theme: str) -> str:
        """Apply visual theme to generated content."""
        # This would modify the CSS variables and classes
        # based on the selected theme
        return f"<!-- Theme: {theme} applied -->"
    
    def _embed_javascript(self, html: str) -> str:
        """Embed JavaScript functionality."""
        if "<script>" not in html:
            js_code = self._generate_javascript()
            html = html.replace("</body>", f"<script>{js_code}</script></body>")
        return html
    
    # Helper methods for advanced features integration
    def _extract_difficulty_info(self, article: Article) -> Dict[str, Any]:
        """Extract difficulty analysis info if available."""
        return {
            "difficulty_level": "intermediate",  # Default or from analysis
            "implementation_ready": getattr(article.technical, 'implementation_ready', False),
            "github_repo": getattr(article.technical, 'github_repo', None)
        }
    
    def _extract_roi_info(self, article: Article) -> Dict[str, Any]:
        """Extract ROI analysis info if available."""
        return {
            "confidence_score": 0.7,  # Default or from ROI analysis
            "payback_months": 12,
            "roi_percentage": 150
        }
    
    def _extract_bias_info(self, article: Article) -> Dict[str, Any]:
        """Extract bias analysis info if available."""
        return {
            "neutrality_score": 0.8,  # Default or from bias analysis
            "bias_count": 2,
            "quality_score": 0.85
        }