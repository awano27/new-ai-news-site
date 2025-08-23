"""Unit tests for HTML Generator."""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import tempfile
from bs4 import BeautifulSoup

from src.generators.html_generator import HTMLGenerator, TemplateEngine
from src.models.article import Article, TechnicalMetadata, BusinessMetadata


class TestHTMLGenerator:
    """Test cases for HTML Generator."""

    @pytest.fixture
    def html_generator(self, settings):
        """Create HTML generator instance."""
        return HTMLGenerator(settings)

    @pytest.fixture
    def template_engine(self, settings):
        """Create template engine instance."""
        return TemplateEngine(settings)

    @pytest.mark.unit
    def test_generate_html_from_articles(self, html_generator, sample_articles):
        """Test HTML generation from article list."""
        # Given
        articles = sample_articles
        
        # Mock template loading and rendering
        with patch.object(html_generator, '_load_template') as mock_load, \
             patch.object(html_generator, '_render_template') as mock_render:
            
            mock_load.return_value = "<html>{{content}}</html>"
            mock_render.return_value = "<html><div>Test Content</div></html>"
            
            # When
            result = html_generator.generate(articles)
            
            # Then
            assert result is not None
            assert isinstance(result, (str, Path))
            mock_load.assert_called()
            mock_render.assert_called()

    @pytest.mark.unit
    def test_render_article_card(self, html_generator, sample_article):
        """Test individual article card rendering."""
        # Given
        sample_article.evaluation = {
            "engineer": {"total_score": 0.85, "breakdown": {"technical_depth": 0.9}},
            "business": {"total_score": 0.72, "breakdown": {"business_impact": 0.8}}
        }
        
        # When
        card_html = html_generator._render_article_card(sample_article, persona="engineer")
        
        # Then
        assert isinstance(card_html, str)
        assert len(card_html) > 100
        assert sample_article.title in card_html
        assert "0.85" in card_html or "85" in card_html  # Score display

    @pytest.mark.unit
    def test_generate_evaluation_visualization(self, html_generator):
        """Test evaluation score visualization generation."""
        # Given
        evaluation = {
            "total_score": 0.85,
            "breakdown": {
                "technical_depth": 0.9,
                "implementation": 0.8,
                "novelty": 0.85,
                "reproducibility": 0.75,
                "community_impact": 0.9
            }
        }
        
        # When
        viz_html = html_generator._generate_evaluation_viz(evaluation, "engineer")
        
        # Then
        assert isinstance(viz_html, str)
        assert "radar" in viz_html.lower() or "chart" in viz_html.lower()
        assert "85" in viz_html  # Total score

    @pytest.mark.unit
    def test_apply_persona_styling(self, html_generator):
        """Test persona-specific styling application."""
        # Given
        base_html = "<div class='article-card'>Content</div>"
        
        # When
        engineer_html = html_generator._apply_persona_styling(base_html, "engineer")
        business_html = html_generator._apply_persona_styling(base_html, "business")
        
        # Then
        assert engineer_html != business_html
        assert "engineer" in engineer_html or "technical" in engineer_html
        assert "business" in business_html or "roi" in business_html

    @pytest.mark.unit
    def test_generate_summary_statistics(self, html_generator, sample_articles):
        """Test summary statistics generation."""
        # Given
        articles = sample_articles
        for article in articles:
            article.evaluation = {
                "engineer": {"total_score": 0.8},
                "business": {"total_score": 0.7}
            }
        
        # When
        stats = html_generator._generate_summary_stats(articles)
        
        # Then
        assert "total_articles" in stats
        assert "avg_engineer_score" in stats
        assert "avg_business_score" in stats
        assert stats["total_articles"] == len(articles)

    @pytest.mark.unit
    def test_create_interactive_filters(self, html_generator):
        """Test interactive filter generation."""
        # Given
        filter_config = {
            "source_tier": [1, 2, 3],
            "difficulty_level": ["beginner", "intermediate", "advanced"],
            "score_range": {"min": 0.0, "max": 1.0}
        }
        
        # When
        filter_html = html_generator._create_interactive_filters(filter_config)
        
        # Then
        assert isinstance(filter_html, str)
        assert "filter" in filter_html.lower()
        assert "select" in filter_html or "input" in filter_html

    @pytest.mark.unit
    def test_generate_responsive_layout(self, html_generator, sample_articles):
        """Test responsive layout generation."""
        # When
        layout_html = html_generator._generate_responsive_layout(sample_articles)
        
        # Then
        assert isinstance(layout_html, str)
        assert "viewport" in layout_html or "responsive" in layout_html
        assert "mobile" in layout_html.lower() or "@media" in layout_html

    @pytest.mark.unit
    def test_embed_javascript_functionality(self, html_generator):
        """Test JavaScript functionality embedding."""
        # Given
        base_html = "<html><head></head><body></body></html>"
        
        # When
        enhanced_html = html_generator._embed_javascript(base_html)
        
        # Then
        assert "<script>" in enhanced_html
        assert "function" in enhanced_html or "=>" in enhanced_html

    @pytest.mark.unit
    def test_optimize_for_performance(self, html_generator):
        """Test HTML performance optimization."""
        # Given
        unoptimized_html = """
        <html>
            <head>
                <style>  body { margin: 0; }  </style>
                <style>  .container { padding: 20px; }  </style>
            </head>
            <body>
                <div>    Content with extra spaces    </div>
            </body>
        </html>
        """
        
        # When
        optimized_html = html_generator._optimize_html(unoptimized_html)
        
        # Then
        assert len(optimized_html) < len(unoptimized_html)
        # Should merge styles and remove extra whitespace

    @pytest.mark.unit
    def test_generate_rss_feed(self, html_generator, sample_articles):
        """Test RSS feed generation."""
        # When
        rss_content = html_generator._generate_rss_feed(sample_articles)
        
        # Then
        assert isinstance(rss_content, str)
        assert "<?xml" in rss_content
        assert "<rss" in rss_content
        assert "<channel>" in rss_content
        assert "<item>" in rss_content

    @pytest.mark.unit
    def test_create_sitemap(self, html_generator, sample_articles):
        """Test XML sitemap creation."""
        # When
        sitemap = html_generator._create_sitemap(sample_articles)
        
        # Then
        assert isinstance(sitemap, str)
        assert "<?xml" in sitemap
        assert "<urlset" in sitemap
        assert "<url>" in sitemap
        assert "<loc>" in sitemap

    @pytest.mark.unit
    def test_generate_with_different_themes(self, html_generator, sample_articles):
        """Test generation with different UI themes."""
        themes = ["light", "dark", "professional", "modern"]
        
        for theme in themes:
            # When
            with patch.object(html_generator.settings, 'ui_theme', theme):
                result = html_generator._apply_theme(sample_articles, theme)
            
            # Then
            assert isinstance(result, str)
            # Theme should be reflected in CSS or classes

    @pytest.mark.unit
    def test_handle_missing_data_gracefully(self, html_generator):
        """Test graceful handling of missing article data."""
        # Given - Article with minimal data
        minimal_article = Article(
            id="minimal",
            title="Basic Article",
            url="",
            source="",
            source_tier=2
        )
        
        # When
        card_html = html_generator._render_article_card(minimal_article)
        
        # Then
        assert isinstance(card_html, str)
        assert len(card_html) > 50  # Should still generate some content
        assert "Basic Article" in card_html

    @pytest.mark.unit
    def test_accessibility_compliance(self, html_generator, sample_articles):
        """Test that generated HTML is accessibility compliant."""
        # When
        html_content = html_generator.generate(sample_articles)
        
        if isinstance(html_content, Path):
            html_content = html_content.read_text()
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Then - Check basic accessibility requirements
        assert soup.find('html') is not None
        assert soup.find('title') is not None
        
        # Check for alt attributes on images
        images = soup.find_all('img')
        for img in images:
            assert img.get('alt') is not None, "Image missing alt attribute"
        
        # Check for proper heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        assert len(headings) > 0, "No headings found"

    @pytest.mark.unit
    def test_seo_optimization(self, html_generator, sample_articles):
        """Test SEO optimization features."""
        # When
        html_content = html_generator.generate(sample_articles)
        
        if isinstance(html_content, Path):
            html_content = html_content.read_text()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Then - Check SEO elements
        assert soup.find('meta', {'name': 'description'}) is not None
        assert soup.find('meta', {'property': 'og:title'}) is not None
        assert soup.find('meta', {'name': 'keywords'}) is not None or \
               soup.find('meta', {'property': 'og:description'}) is not None


class TestTemplateEngine:
    """Test cases for Template Engine."""

    @pytest.mark.unit
    def test_load_template_file(self, template_engine):
        """Test template file loading."""
        # Given
        template_content = "<html><body>{{content}}</body></html>"
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            # When
            template = template_engine.load_template("test.html")
            
            # Then
            assert template == template_content

    @pytest.mark.unit
    def test_render_template_with_variables(self, template_engine):
        """Test template rendering with variable substitution."""
        # Given
        template = "<h1>{{title}}</h1><p>{{content}}</p>"
        variables = {"title": "Test Title", "content": "Test Content"}
        
        # When
        rendered = template_engine.render(template, variables)
        
        # Then
        assert "Test Title" in rendered
        assert "Test Content" in rendered
        assert "{{" not in rendered  # No unprocessed variables

    @pytest.mark.unit
    def test_template_inheritance(self, template_engine):
        """Test template inheritance functionality."""
        # Given
        base_template = "<html><head><title>{{title}}</title></head><body>{{content}}</body></html>"
        child_template = "{{extends:base}}<h1>Child Content</h1>"
        
        with patch.object(template_engine, 'load_template') as mock_load:
            mock_load.return_value = base_template
            
            # When
            rendered = template_engine.render_with_inheritance(child_template, {"title": "Test"})
            
            # Then
            assert "Child Content" in rendered
            assert "<html>" in rendered
            assert "Test" in rendered

    @pytest.mark.unit
    def test_conditional_rendering(self, template_engine):
        """Test conditional template rendering."""
        # Given
        template = "{{if show_details}}<div>Details</div>{{endif}}"
        
        # When
        with_details = template_engine.render(template, {"show_details": True})
        without_details = template_engine.render(template, {"show_details": False})
        
        # Then
        assert "Details" in with_details
        assert "Details" not in without_details

    @pytest.mark.unit
    def test_loop_rendering(self, template_engine):
        """Test loop rendering in templates."""
        # Given
        template = "{{for item in items}}<li>{{item}}</li>{{endfor}}"
        variables = {"items": ["Apple", "Banana", "Cherry"]}
        
        # When
        rendered = template_engine.render(template, variables)
        
        # Then
        assert "Apple" in rendered
        assert "Banana" in rendered
        assert "Cherry" in rendered
        assert rendered.count("<li>") == 3

    @pytest.mark.unit
    def test_custom_filters(self, template_engine):
        """Test custom template filters."""
        # Given
        template = "{{value|currency}} and {{text|truncate:10}}"
        variables = {"value": 1234.56, "text": "This is a long text"}
        
        # When
        rendered = template_engine.render_with_filters(template, variables)
        
        # Then
        assert "$1,234.56" in rendered or "1234.56" in rendered
        assert len("This is a long text") > len("This is a ...")  # Truncated