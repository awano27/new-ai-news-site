#!/usr/bin/env python3
"""Comprehensive AI news collection from multiple sources."""

import sys
import asyncio
import requests
import feedparser
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import re
import json

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import Settings
from src.models.article import Article, TechnicalMetadata, BusinessMetadata, ImplementationCost
from src.generators.static_site_generator import StaticSiteGenerator


class ComprehensiveDataCollector:
    """Collect AI news from comprehensive source list."""
    
    def __init__(self):
        self.sources = {
            # Tier 1 - Primary Research & Company Blogs
            "openai_blog": {
                "url": "https://openai.com/blog/rss.xml",
                "tier": 1,
                "source_name": "OpenAI Blog",
                "category": "research"
            },
            "deepmind_blog": {
                "url": "https://deepmind.google/blog/rss.xml", 
                "tier": 1,
                "source_name": "DeepMind Blog",
                "category": "research"
            },
            "anthropic_news": {
                "url": "https://www.anthropic.com/news/rss.xml",
                "tier": 1,
                "source_name": "Anthropic News",
                "category": "research"
            },
            "google_ai_blog": {
                "url": "https://ai.googleblog.com/feeds/posts/default",
                "tier": 1,
                "source_name": "Google AI Blog",
                "category": "research"
            },
            "microsoft_research": {
                "url": "https://www.microsoft.com/en-us/research/feed/",
                "tier": 1,
                "source_name": "Microsoft Research",
                "category": "research"
            },
            "meta_ai": {
                "url": "https://ai.meta.com/blog/rss/",
                "tier": 1,
                "source_name": "Meta AI",
                "category": "research"
            },
            
            # Tier 1 - Academic Institutions
            "mit_ai_news": {
                "url": "https://news.mit.edu/rss/topic/artificial-intelligence2",
                "tier": 1,
                "source_name": "MIT AI News",
                "category": "academic"
            },
            "stanford_ai": {
                "url": "https://hai.stanford.edu/news/rss",
                "tier": 1,
                "source_name": "Stanford HAI",
                "category": "academic"
            },
            
            # Tier 2 - Tech News & Analysis
            "techcrunch_ai": {
                "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
                "tier": 2,
                "source_name": "TechCrunch AI",
                "category": "news"
            },
            "venturebeat_ai": {
                "url": "https://venturebeat.com/ai/feed/",
                "tier": 2,
                "source_name": "VentureBeat AI",
                "category": "news"
            },
            "wired_ai": {
                "url": "https://www.wired.com/feed/tag/ai/latest/rss",
                "tier": 2,
                "source_name": "Wired AI",
                "category": "news"
            },
            "ieee_spectrum": {
                "url": "https://spectrum.ieee.org/rss/artificial-intelligence/fulltext",
                "tier": 2,
                "source_name": "IEEE Spectrum AI",
                "category": "technical"
            },
            
            # Tier 2 - Community & Forums
            "hackernews_ai": {
                "url": "https://hnrss.org/newest?q=AI+OR+artificial+intelligence+OR+machine+learning+OR+neural+network",
                "tier": 2,
                "source_name": "Hacker News AI",
                "category": "community"
            },
            "reddit_ml": {
                "url": "https://www.reddit.com/r/MachineLearning/.rss",
                "tier": 2,
                "source_name": "Reddit ML",
                "category": "community"
            },
            
            # Tier 2 - Developer Focus
            "towards_data_science": {
                "url": "https://towardsdatascience.com/feed/tagged/artificial-intelligence",
                "tier": 2,
                "source_name": "Towards Data Science",
                "category": "tutorial"
            },
            "huggingface_blog": {
                "url": "https://huggingface.co/blog/rss.xml",
                "tier": 2,
                "source_name": "Hugging Face Blog",
                "category": "technical"
            },
            
            # Tier 3 - Industry & Business
            "ai_business": {
                "url": "https://aibusiness.com/rss.xml",
                "tier": 3,
                "source_name": "AI Business",
                "category": "business"
            },
            "forbes_ai": {
                "url": "https://www.forbes.com/ai/rss/",
                "tier": 3,
                "source_name": "Forbes AI",
                "category": "business"
            },
            
            # ArXiv (Academic Papers)
            "arxiv_ai": {
                "url": "http://export.arxiv.org/rss/cs.AI/recent",
                "tier": 1,
                "source_name": "ArXiv AI",
                "category": "papers"
            },
            "arxiv_ml": {
                "url": "http://export.arxiv.org/rss/cs.LG/recent",
                "tier": 1,
                "source_name": "ArXiv ML",
                "category": "papers"
            },
            "arxiv_cl": {
                "url": "http://export.arxiv.org/rss/cs.CL/recent",
                "tier": 1,
                "source_name": "ArXiv NLP",
                "category": "papers"
            }
        }
    
    def collect_from_feed(self, feed_config: Dict, max_articles: int = 3) -> List[Article]:
        """Collect articles from a single RSS feed."""
        articles = []
        
        try:
            print(f"📡 Collecting from {feed_config['source_name']} ({feed_config['category']})...")
            
            headers = {
                'User-Agent': 'DailyAINews/1.0 (Educational Project)',
                'Accept': 'application/rss+xml, application/xml, text/xml'
            }
            
            response = requests.get(feed_config['url'], headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"⚠️ HTTP {response.status_code} for {feed_config['source_name']}")
                return articles
                
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                print(f"⚠️ Feed parsing warning for {feed_config['source_name']}: {feed.bozo_exception}")
            
            processed_count = 0
            for entry in feed.entries:
                if processed_count >= max_articles:
                    break
                    
                try:
                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        pub_date = datetime.now()
                    
                    # Skip very old articles (older than 60 days)
                    if pub_date < datetime.now() - timedelta(days=60):
                        continue
                    
                    # Get content
                    content = ""
                    if hasattr(entry, 'summary'):
                        content = entry.summary
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    elif hasattr(entry, 'content'):
                        if isinstance(entry.content, list) and len(entry.content) > 0:
                            content = entry.content[0].value
                        else:
                            content = str(entry.content)
                    
                    # Clean HTML tags from content
                    content = re.sub(r'<[^>]+>', '', content)
                    content = re.sub(r'\s+', ' ', content).strip()
                    
                    # Skip if content is too short or title is missing
                    if len(content) < 50 or not hasattr(entry, 'title') or len(entry.title.strip()) < 10:
                        continue
                    
                    # Create unique ID
                    article_id = f"{feed_config['source_name'].lower().replace(' ', '_')}_{hash(entry.link if hasattr(entry, 'link') else entry.title) % 100000}"
                    
                    article = Article(
                        id=article_id,
                        title=entry.title.strip(),
                        url=entry.link if hasattr(entry, 'link') else "",
                        source=feed_config['source_name'],
                        source_tier=feed_config['tier'],
                        published_date=pub_date,
                        content=content,
                        tags=[feed_config['category']]
                    )
                    
                    articles.append(article)
                    processed_count += 1
                    
                except Exception as e:
                    print(f"⚠️ Error processing entry from {feed_config['source_name']}: {e}")
                    continue
            
            print(f"✅ Collected {len(articles)} articles from {feed_config['source_name']}")
            
        except requests.RequestException as e:
            print(f"❌ Network error for {feed_config['source_name']}: {e}")
        except Exception as e:
            print(f"❌ Error collecting from {feed_config['source_name']}: {e}")
        
        return articles
    
    def collect_all(self, max_per_source: int = 3) -> List[Article]:
        """Collect from all sources with duplicate detection."""
        all_articles = []
        collection_stats = {}
        
        # Collect from each source with rate limiting
        for source_key, feed_config in self.sources.items():
            articles = self.collect_from_feed(feed_config, max_per_source)
            all_articles.extend(articles)
            
            collection_stats[source_key] = {
                "count": len(articles),
                "tier": feed_config["tier"],
                "category": feed_config["category"]
            }
            
            # Rate limiting - be respectful to servers
            time.sleep(2)
        
        # Remove duplicates based on title similarity and URL
        unique_articles = []
        seen_titles = set()
        seen_urls = set()
        
        for article in all_articles:
            # Create normalized title key
            title_key = re.sub(r'[^\w\s]', '', article.title.lower()).replace(' ', '')[:60]
            url_key = article.url.lower() if article.url else ""
            
            # Skip if we've seen this title or URL before
            if title_key in seen_titles or (url_key and url_key in seen_urls):
                continue
                
            seen_titles.add(title_key)
            if url_key:
                seen_urls.add(url_key)
            unique_articles.append(article)
        
        # Print collection summary
        print(f"\n📊 Collection Summary:")
        print(f"Total articles collected: {len(all_articles)}")
        print(f"Unique articles after deduplication: {len(unique_articles)}")
        print(f"\nBy tier:")
        
        tier_stats = {}
        for article in unique_articles:
            tier = article.source_tier
            if tier not in tier_stats:
                tier_stats[tier] = {"count": 0, "sources": set()}
            tier_stats[tier]["count"] += 1
            tier_stats[tier]["sources"].add(article.source)
        
        for tier in sorted(tier_stats.keys()):
            print(f"  Tier {tier}: {tier_stats[tier]['count']} articles from {len(tier_stats[tier]['sources'])} sources")
        
        return unique_articles


class EnhancedEvaluator:
    """Enhanced evaluator with category-specific scoring."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def evaluate_article(self, article: Article, persona: str) -> Dict[str, Any]:
        """Enhanced evaluation with category-specific bonuses."""
        content_lower = (article.title + " " + article.content).lower()
        
        # Enhanced keyword sets
        tech_keywords = {
            'research': ['algorithm', 'model', 'neural', 'deep learning', 'machine learning', 'ai', 'artificial intelligence', 'research', 'paper', 'arxiv', 'transformer', 'llm', 'gpt'],
            'implementation': ['python', 'github', 'code', 'api', 'framework', 'library', 'implementation', 'tutorial', 'open source'],
            'advanced': ['attention', 'embedding', 'tokenization', 'fine-tuning', 'reinforcement', 'supervised', 'unsupervised', 'generative']
        }
        
        business_keywords = {
            'financial': ['revenue', 'roi', 'profit', 'cost', 'savings', 'efficiency', 'investment', 'funding', 'valuation'],
            'market': ['market', 'business', 'enterprise', 'company', 'commercial', 'industry', 'customer', 'adoption'],
            'strategy': ['strategy', 'partnership', 'growth', 'scale', 'competitive', 'advantage', 'disruption', 'innovation']
        }
        
        # Count matches by category
        tech_score = 0
        for category, keywords in tech_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            weight = {'research': 1.0, 'implementation': 1.2, 'advanced': 0.8}[category]
            tech_score += matches * weight
        
        business_score = 0
        for category, keywords in business_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            weight = {'financial': 1.2, 'market': 1.0, 'strategy': 0.9}[category]
            business_score += matches * weight
        
        # Source tier bonus (enhanced)
        tier_bonus = {1: 0.25, 2: 0.15, 3: 0.05}.get(article.source_tier, 0.0)
        
        # Category-specific bonuses
        category_bonus = 0.0
        if article.tags:
            category = article.tags[0] if article.tags else "general"
            if persona == "engineer":
                category_bonus = {
                    'research': 0.1, 'papers': 0.15, 'technical': 0.12, 
                    'tutorial': 0.08, 'academic': 0.1, 'community': 0.05
                }.get(category, 0.0)
            else:  # business
                category_bonus = {
                    'business': 0.15, 'news': 0.1, 'research': 0.08,
                    'community': 0.05, 'academic': 0.06
                }.get(category, 0.0)
        
        # Recency bonus (more recent = slight bonus)
        recency_bonus = 0.0
        if article.published_date:
            days_ago = (datetime.now() - article.published_date).days
            if days_ago < 7:
                recency_bonus = 0.05
            elif days_ago < 30:
                recency_bonus = 0.02
        
        # Calculate final scores
        if persona == "engineer":
            base_score = min(0.8, (tech_score * 0.04) + 0.25)
            total_score = min(1.0, base_score + tier_bonus + category_bonus + recency_bonus)
        else:  # business
            base_score = min(0.8, (business_score * 0.04) + 0.25)
            total_score = min(1.0, base_score + tier_bonus + category_bonus + recency_bonus)
        
        # Add controlled randomness for diversity
        import hashlib
        hash_seed = int(hashlib.md5((article.id + persona).encode()).hexdigest()[:8], 16)
        random_factor = (hash_seed % 80) / 1000  # 0-0.079
        total_score = min(1.0, total_score + random_factor)
        
        return {
            "total_score": round(total_score, 3),
            "breakdown": {
                "content_relevance": base_score,
                "source_quality": tier_bonus,
                "category_bonus": category_bonus,
                "recency_bonus": recency_bonus,
                "keyword_score": tech_score if persona == "engineer" else business_score
            }
        }


async def evaluate_articles(articles: List[Article], settings: Settings) -> List[Article]:
    """Evaluate articles with enhanced system."""
    print(f"\n🔍 Starting enhanced evaluation for {len(articles)} articles...")
    
    evaluator = EnhancedEvaluator(settings)
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
            
            print(f"  ✅ Engineer: {engineer_eval.get('total_score', 0):.3f}")
            print(f"  ✅ Business: {business_eval.get('total_score', 0):.3f}")
            print(f"  📂 Category: {article.tags[0] if article.tags else 'general'}")
            
            # Enhanced metadata
            content_lower = (article.title + " " + article.content).lower()
            
            article.technical = TechnicalMetadata(
                implementation_ready='github' in content_lower or 'code' in content_lower or 'api' in content_lower,
                code_available='github' in content_lower or 'repository' in content_lower,
                dependencies=[],
                reproducibility_score=0.9 if 'arxiv' in content_lower or 'paper' in content_lower else 
                                    0.7 if 'research' in content_lower else 0.5
            )
            
            article.business = BusinessMetadata(
                market_size="Unknown",
                growth_rate=business_eval.get('total_score', 0.5) * 100,
                implementation_cost=ImplementationCost.HIGH if 'enterprise' in content_lower else
                                  ImplementationCost.LOW if 'tutorial' in content_lower or 'simple' in content_lower else
                                  ImplementationCost.MEDIUM
            )
            
            evaluated_articles.append(article)
            
        except Exception as e:
            print(f"  ⚠️ Evaluation failed: {e}")
            # Add article with basic evaluation
            article.evaluation = {
                "engineer": {"total_score": 0.5},
                "business": {"total_score": 0.5}
            }
            evaluated_articles.append(article)
    
    return evaluated_articles


async def main():
    """Main execution function."""
    print("🚀 Comprehensive AI News Collection and Evaluation")
    print("=" * 70)
    
    # Initialize settings
    settings = Settings()
    
    # Collect from comprehensive sources
    print("\n📰 Collecting from comprehensive AI news sources...")
    collector = ComprehensiveDataCollector()
    
    # Collect more articles per source for comprehensive coverage
    articles = collector.collect_all(max_per_source=2)  # 2 per source to avoid overwhelming
    
    if not articles:
        print("❌ No articles collected. Check network connectivity.")
        return False
    
    print(f"\n✅ Final collection: {len(articles)} unique articles")
    
    # Show sample of collected articles by category
    categories = {}
    for article in articles:
        category = article.tags[0] if article.tags else 'general'
        if category not in categories:
            categories[category] = []
        categories[category].append(article)
    
    print(f"\n📋 Articles by Category:")
    for category, cat_articles in categories.items():
        print(f"  📂 {category.title()}: {len(cat_articles)} articles")
        for i, article in enumerate(cat_articles[:3]):  # Show first 3
            print(f"    {i+1}. {article.title[:50]}... ({article.source})")
    
    # Evaluate articles
    evaluated_articles = await evaluate_articles(articles, settings)
    
    # Sort by combined score
    def get_combined_score(article):
        eng_score = article.evaluation.get("engineer", {}).get("total_score", 0)
        bus_score = article.evaluation.get("business", {}).get("total_score", 0)
        return (eng_score + bus_score) / 2
    
    evaluated_articles.sort(key=get_combined_score, reverse=True)
    
    # Generate comprehensive site
    print(f"\n🏗️ Generating comprehensive site with {len(evaluated_articles)} articles...")
    
    try:
        generator = StaticSiteGenerator(settings)
        docs_dir = Path("docs")
        
        # Generate all components
        css_content = generator.assets.generate_css()
        (docs_dir / "styles.css").write_text(css_content, encoding='utf-8')
        
        js_content = generator.assets.generate_javascript()
        (docs_dir / "script.js").write_text(js_content, encoding='utf-8')
        
        # Generate HTML with enhanced data
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
            title="Daily AI News - Comprehensive Analysis",
            description=f"Comprehensive AI news analysis from {len(set(a.source for a in evaluated_articles))} sources",
            persona="engineer"
        )
        
        # Embed comprehensive article data
        articles_data = []
        for article in evaluated_articles:
            articles_data.append({
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "source_tier": article.source_tier,
                "published_date": article.published_date.isoformat() if article.published_date else None,
                "content": article.content[:300] + "..." if len(article.content) > 300 else article.content,
                "evaluation": article.evaluation,
                "tags": article.tags or [],
                "category": article.tags[0] if article.tags else "general"
            })
        
        # Enhanced JSON data with metadata
        comprehensive_data = {
            "articles": articles_data,
            "metadata": {
                "total_sources": len(set(a.source for a in evaluated_articles)),
                "total_articles": len(evaluated_articles),
                "categories": list(categories.keys()),
                "generation_time": datetime.now().isoformat(),
                "score_range": {
                    "min": min(get_combined_score(a) for a in evaluated_articles),
                    "max": max(get_combined_score(a) for a in evaluated_articles)
                }
            }
        }
        
        articles_json = f'<script id="articles-data" type="application/json">{json.dumps(comprehensive_data, ensure_ascii=False)}</script>'
        page_content = page_content.replace('</body>', f'{articles_json}\n</body>')
        
        # Write final HTML
        index_file = docs_dir / "index.html"
        index_file.write_text(page_content, encoding='utf-8')
        
        print(f"✅ Comprehensive site generated successfully!")
        print(f"📁 Output: {docs_dir.absolute()}")
        
        # Show comprehensive top articles
        print(f"\n🏆 Top 10 Articles (Comprehensive Analysis):")
        for i, article in enumerate(evaluated_articles[:10]):
            eng_score = article.evaluation.get("engineer", {}).get("total_score", 0)
            bus_score = article.evaluation.get("business", {}).get("total_score", 0)
            combined = (eng_score + bus_score) / 2
            category = article.tags[0] if article.tags else "general"
            
            print(f"  {i+1:2}. {article.title[:55]}...")
            print(f"      Score: {combined:.3f} (E:{eng_score:.3f}, B:{bus_score:.3f}) | {article.source} | {category}")
            print()
        
        # Generate RSS with comprehensive data
        rss_items = []
        for article in evaluated_articles[:20]:
            rss_items.append(f"""
        <item>
            <title><![CDATA[{article.title}]]></title>
            <description><![CDATA[{article.content[:400]}...]]></description>
            <link>{article.url}</link>
            <guid>{article.url}</guid>
            <pubDate>{article.published_date.strftime('%a, %d %b %Y %H:%M:%S GMT') if article.published_date else ''}</pubDate>
            <source url="{article.url}">{article.source}</source>
            <category>{article.tags[0] if article.tags else 'general'}</category>
        </item>""")
        
        rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>Daily AI News - Comprehensive Feed</title>
        <description>Comprehensive AI news from {len(set(a.source for a in evaluated_articles))} sources with advanced evaluation</description>
        <link>https://example.com</link>
        <atom:link href="https://example.com/feed.xml" rel="self" type="application/rss+xml"/>
        <language>en-us</language>
        <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
        <generator>Daily AI News Comprehensive Generator</generator>
        {''.join(rss_items)}
    </channel>
</rss>"""
        
        (docs_dir / "feed.xml").write_text(rss_content, encoding='utf-8')
        
        print(f"🌐 Open docs/index.html to view the comprehensive AI news dashboard!")
        print(f"📊 Comprehensive analysis complete: {len(evaluated_articles)} articles from {len(set(a.source for a in evaluated_articles))} sources")
        
        return True
        
    except Exception as e:
        print(f"❌ Site generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 Comprehensive AI news collection completed successfully!")
    else:
        print("\n❌ Process failed. Check error messages above.")
    
    sys.exit(0 if success else 1)