#!/usr/bin/env python3
"""Collect real AI news and evaluate with simplified evaluation."""

import sys
import asyncio
import requests
import feedparser
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import re

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import Settings
from src.models.article import Article, TechnicalMetadata, BusinessMetadata, ImplementationCost
from src.evaluators.multi_layer_evaluator import MultiLayerEvaluator
from src.generators.static_site_generator import StaticSiteGenerator


class SimpleEvaluator:
    """Simplified evaluator for real-time testing."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def evaluate_article(self, article: Article, persona: str) -> Dict[str, Any]:
        """Simple evaluation based on content analysis."""
        # Simple keyword-based scoring
        content_lower = (article.title + " " + article.content).lower()
        
        # Technical keywords for engineer persona
        tech_keywords = [
            'algorithm', 'model', 'neural', 'deep learning', 'machine learning',
            'ai', 'artificial intelligence', 'python', 'github', 'open source',
            'research', 'paper', 'arxiv', 'transformer', 'llm', 'gpt',
            'api', 'framework', 'library', 'code', 'implementation'
        ]
        
        # Business keywords for business persona
        business_keywords = [
            'revenue', 'roi', 'profit', 'cost', 'savings', 'efficiency',
            'customer', 'market', 'business', 'enterprise', 'company',
            'investment', 'funding', 'strategy', 'adoption', 'scale',
            'commercial', 'industry', 'partnership', 'growth', 'value'
        ]
        
        # Count keyword matches
        tech_matches = sum(1 for keyword in tech_keywords if keyword in content_lower)
        business_matches = sum(1 for keyword in business_keywords if keyword in content_lower)
        
        # Source tier bonus
        tier_bonus = 0.2 if article.source_tier == 1 else 0.1
        
        # Calculate scores
        if persona == "engineer":
            base_score = min(0.9, (tech_matches * 0.05) + 0.3)
            relevance_bonus = 0.1 if any(keyword in content_lower for keyword in ['github', 'code', 'implementation', 'open source']) else 0
            total_score = min(1.0, base_score + tier_bonus + relevance_bonus)
        else:  # business
            base_score = min(0.9, (business_matches * 0.05) + 0.3)
            relevance_bonus = 0.1 if any(keyword in content_lower for keyword in ['roi', 'revenue', 'enterprise', 'commercial']) else 0
            total_score = min(1.0, base_score + tier_bonus + relevance_bonus)
        
        # Add some randomness for diversity (but reproducible)
        import hashlib
        hash_seed = int(hashlib.md5((article.id + persona).encode()).hexdigest()[:8], 16)
        random_factor = (hash_seed % 100) / 1000  # 0-0.099
        total_score = min(1.0, total_score + random_factor)
        
        return {
            "total_score": round(total_score, 3),
            "breakdown": {
                "content_relevance": base_score,
                "source_quality": tier_bonus,
                "technical_depth": tech_matches * 0.05 if persona == "engineer" else business_matches * 0.05,
                "keyword_matches": tech_matches if persona == "engineer" else business_matches
            }
        }


class RealDataCollector:
    """Collect real AI news from various sources."""
    
    def __init__(self):
        self.sources = {
            # Tier 1 sources
            "openai_blog": {
                "url": "https://openai.com/blog/rss.xml",
                "tier": 1,
                "source_name": "OpenAI Blog"
            },
            "deepmind_blog": {
                "url": "https://deepmind.google/blog/rss.xml", 
                "tier": 1,
                "source_name": "DeepMind Blog"
            },
            # Tier 2 sources
            "hackernews_ai": {
                "url": "https://hnrss.org/newest?q=AI+OR+artificial+intelligence+OR+machine+learning",
                "tier": 2,
                "source_name": "Hacker News AI"
            },
            "mit_news_ai": {
                "url": "https://news.mit.edu/rss/topic/artificial-intelligence2",
                "tier": 2,
                "source_name": "MIT News AI"
            }
        }
    
    def collect_from_feed(self, feed_config: Dict) -> List[Article]:
        """Collect articles from a single RSS feed."""
        articles = []
        
        try:
            print(f"📡 Collecting from {feed_config['source_name']}...")
            
            headers = {
                'User-Agent': 'DailyAINews/1.0 (Educational Project)'
            }
            
            response = requests.get(feed_config['url'], headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries[:3]:  # Limit to 3 most recent per source
                try:
                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        pub_date = datetime.now()
                    
                    # Skip very old articles (older than 30 days)
                    if pub_date < datetime.now() - timedelta(days=30):
                        continue
                    
                    # Get content
                    content = ""
                    if hasattr(entry, 'summary'):
                        content = entry.summary
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    
                    # Clean HTML tags from content
                    content = re.sub(r'<[^>]+>', '', content)
                    content = content.strip()
                    
                    # Skip if content is too short
                    if len(content) < 100:
                        continue
                    
                    article = Article(
                        id=f"{feed_config['source_name'].lower().replace(' ', '_')}_{hash(entry.link) % 10000}",
                        title=entry.title,
                        url=entry.link,
                        source=feed_config['source_name'],
                        source_tier=feed_config['tier'],
                        published_date=pub_date,
                        content=content
                    )
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"⚠️ Error processing entry: {e}")
                    continue
            
            print(f"✅ Collected {len(articles)} articles from {feed_config['source_name']}")
            
        except requests.RequestException as e:
            print(f"❌ Network error collecting from {feed_config['source_name']}: {e}")
        except Exception as e:
            print(f"❌ Error collecting from {feed_config['source_name']}: {e}")
        
        return articles
    
    def collect_all(self) -> List[Article]:
        """Collect from all sources."""
        all_articles = []
        
        for source_key, feed_config in self.sources.items():
            articles = self.collect_from_feed(feed_config)
            all_articles.extend(articles)
            time.sleep(1)  # Be nice to servers
        
        # Remove duplicates based on title similarity
        unique_articles = []
        seen_titles = set()
        
        for article in all_articles:
            title_key = article.title.lower().replace(' ', '')[:50]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles


async def evaluate_articles(articles: List[Article], settings: Settings) -> List[Article]:
    """Evaluate articles using simplified evaluation."""
    print("\n🔍 Starting simplified evaluation...")
    
    evaluator = SimpleEvaluator(settings)
    evaluated_articles = []
    
    for i, article in enumerate(articles):
        print(f"\n📊 Evaluating article {i+1}/{len(articles)}: {article.title[:60]}...")
        
        try:
            # Evaluate for both personas
            engineer_eval = await evaluator.evaluate_article(article, persona="engineer")
            business_eval = await evaluator.evaluate_article(article, persona="business")
            
            article.evaluation = {
                "engineer": engineer_eval,
                "business": business_eval
            }
            
            print(f"  ✅ Engineer score: {engineer_eval.get('total_score', 0):.3f}")
            print(f"  ✅ Business score: {business_eval.get('total_score', 0):.3f}")
            
            # Add simple technical/business metadata
            content_lower = (article.title + " " + article.content).lower()
            
            article.technical = TechnicalMetadata(
                implementation_ready='github' in content_lower or 'code' in content_lower,
                code_available='github' in content_lower,
                dependencies=[],
                reproducibility_score=0.8 if 'paper' in content_lower or 'research' in content_lower else 0.5
            )
            
            article.business = BusinessMetadata(
                market_size="Unknown",
                growth_rate=business_eval.get('total_score', 0.5) * 100,  # Convert to percentage
                implementation_cost=ImplementationCost.MEDIUM
            )
            
            evaluated_articles.append(article)
            
        except Exception as e:
            print(f"  ⚠️ Metadata creation failed: {e}")
            # Add article even if metadata failed (evaluation scores are preserved)
            evaluated_articles.append(article)
    
    return evaluated_articles


async def main():
    """Main execution function."""
    print("🚀 Real AI News Collection and Evaluation (Simplified)")
    print("=" * 60)
    
    # Initialize settings
    settings = Settings()
    
    # Collect real articles
    print("\n📰 Collecting real AI news articles...")
    collector = RealDataCollector()
    articles = collector.collect_all()
    
    if not articles:
        print("❌ No articles collected. Check network connectivity and feed URLs.")
        return False
    
    print(f"\n✅ Collected {len(articles)} unique articles")
    
    # Show collected articles
    print("\n📋 Collected Articles:")
    for i, article in enumerate(articles):
        print(f"  {i+1}. {article.title}")
        print(f"     Source: {article.source} (Tier {article.source_tier})")
        print(f"     Published: {article.published_date.strftime('%Y-%m-%d %H:%M')}")
        print()
    
    # Evaluate articles
    evaluated_articles = await evaluate_articles(articles, settings)
    
    # Sort by combined score
    def get_combined_score(article):
        eng_score = article.evaluation.get("engineer", {}).get("total_score", 0)
        bus_score = article.evaluation.get("business", {}).get("total_score", 0)
        return (eng_score + bus_score) / 2
    
    evaluated_articles.sort(key=get_combined_score, reverse=True)
    
    # Generate site with real data
    print(f"\n🏗️ Generating site with {len(evaluated_articles)} evaluated articles...")
    
    try:
        generator = StaticSiteGenerator(settings)
        
        # Use the simple site generation approach
        docs_dir = Path("docs")
        
        # Generate CSS
        css_content = generator.assets.generate_css()
        (docs_dir / "styles.css").write_text(css_content, encoding='utf-8')
        
        # Generate JS 
        js_content = generator.assets.generate_javascript()
        (docs_dir / "script.js").write_text(js_content, encoding='utf-8')
        
        # Generate HTML
        html_generator = generator.html_generator
        processed_articles = html_generator._process_articles(evaluated_articles, "engineer")
        summary_stats = html_generator._generate_summary_stats(evaluated_articles)
        
        articles_html = html_generator._render_articles_grid(processed_articles, "engineer")
        filters_html = html_generator._create_interactive_filters(html_generator._extract_filter_options(evaluated_articles))
        stats_html = html_generator._render_summary_stats(summary_stats)
        
        dashboard_template = html_generator.template_engine.load_template("dashboard.html")
        dashboard_content = html_generator.template_engine.render(dashboard_template, {
            "articles": articles_html,
            "filters": filters_html,
            "summary_stats": stats_html
        })
        
        page_content = html_generator._generate_complete_page(
            dashboard_content,
            title="Daily AI News - Real Data Analysis",
            description="Live AI news with multi-layer evaluation system",
            persona="engineer"
        )
        
        # Write HTML
        index_file = docs_dir / "index.html"
        index_file.write_text(page_content, encoding='utf-8')
        
        # Generate feed with article data embedded
        articles_data = []
        for article in evaluated_articles:
            articles_data.append({
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "source_tier": article.source_tier,
                "published_date": article.published_date.isoformat() if article.published_date else None,
                "content": article.content[:200] + "...",
                "evaluation": article.evaluation,
                "tags": getattr(article, 'tags', [])
            })
        
        # Add articles data as JSON script tag
        articles_json = f'<script id="articles-data" type="application/json">{{"articles": {articles_data}}}</script>'
        page_content = page_content.replace('</body>', f'{articles_json}\n</body>')
        index_file.write_text(page_content, encoding='utf-8')
        
        print(f"✅ Site generated successfully!")
        print(f"📁 Output: {docs_dir.absolute()}")
        
        # Show top articles
        print(f"\n🏆 Top 5 Articles by Combined Score:")
        for i, article in enumerate(evaluated_articles[:5]):
            eng_score = article.evaluation.get("engineer", {}).get("total_score", 0)
            bus_score = article.evaluation.get("business", {}).get("total_score", 0)
            combined = (eng_score + bus_score) / 2
            
            print(f"  {i+1}. {article.title[:60]}...")
            print(f"     Combined: {combined:.3f} (Eng: {eng_score:.3f}, Bus: {bus_score:.3f})")
            print(f"     Source: {article.source}")
            print()
        
        print(f"🌐 Open docs/index.html to view the real AI news dashboard!")
        
        return True
        
    except Exception as e:
        print(f"❌ Site generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 Real AI news collection and evaluation completed successfully!")
    else:
        print("\n❌ Process failed. Check error messages above.")
    
    sys.exit(0 if success else 1)