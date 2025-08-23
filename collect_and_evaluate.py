#!/usr/bin/env python3
"""Collect real AI news and evaluate with the multi-layer system."""

import sys
import asyncio
import requests
import feedparser
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import Settings
from src.models.article import Article, TechnicalMetadata, BusinessMetadata
from src.collectors.feed_collector import FeedCollector
from src.evaluators.multi_layer_evaluator import MultiLayerEvaluator
from src.features.implementation_difficulty import ImplementationDifficultyAnalyzer
from src.features.roi_calculator import ROICalculator
from src.features.bias_detector import BiasDetector
from src.generators.static_site_generator import StaticSiteGenerator


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
            "anthropic_news": {
                "url": "https://www.anthropic.com/news/rss.xml",
                "tier": 1,
                "source_name": "Anthropic News"
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
            
            # Add timeout and user agent
            headers = {
                'User-Agent': 'DailyAINews/1.0 (Educational Project)'
            }
            
            response = requests.get(feed_config['url'], headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                print(f"⚠️ Feed parsing warning for {feed_config['source_name']}")
            
            for entry in feed.entries[:5]:  # Limit to 5 most recent
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
                    import re
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
                    print(f"⚠️ Error processing entry from {feed_config['source_name']}: {e}")
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
            
            # Be nice to servers
            time.sleep(1)
        
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
    """Evaluate articles using all analysis systems."""
    print("\n🔍 Starting comprehensive evaluation...")
    
    # Initialize evaluators
    evaluator = MultiLayerEvaluator(settings)
    difficulty_analyzer = ImplementationDifficultyAnalyzer(settings)
    roi_calculator = ROICalculator(settings)
    bias_detector = BiasDetector(settings)
    
    evaluated_articles = []
    
    for i, article in enumerate(articles):
        print(f"\n📊 Evaluating article {i+1}/{len(articles)}: {article.title[:60]}...")
        
        try:
            # Multi-layer evaluation for both personas
            engineer_eval = await evaluator.evaluate(article, persona="engineer")
            business_eval = await evaluator.evaluate(article, persona="business")
            
            article.evaluation = {
                "engineer": engineer_eval,
                "business": business_eval
            }
            
            print(f"  ✅ Engineer score: {engineer_eval.get('total_score', 0):.3f}")
            print(f"  ✅ Business score: {business_eval.get('total_score', 0):.3f}")
            
            # Implementation difficulty analysis
            try:
                difficulty_result = difficulty_analyzer.analyze(article)
                article.technical = TechnicalMetadata(
                    implementation_ready=difficulty_result.get('difficulty_level') != 'research',
                    code_available=bool(difficulty_result.get('resource_requirements', {}).get('code_repository')),
                    dependencies=difficulty_result.get('skill_requirements', [])[:5],
                    reproducibility_score=min(1.0, difficulty_result.get('complexity_score', 0.5))
                )
                print(f"  ✅ Difficulty: {difficulty_result.get('difficulty_level', 'unknown')}")
            except Exception as e:
                print(f"  ⚠️ Difficulty analysis failed: {e}")
            
            # ROI calculation
            try:
                roi_result = roi_calculator.analyze_article_roi(article)
                if roi_result:
                    article.business = BusinessMetadata(
                        market_size=f"Confidence: {roi_result.confidence_score:.2f}",
                        roi_potential=roi_result.confidence_score
                    )
                    print(f"  ✅ ROI confidence: {roi_result.confidence_score:.3f}")
                else:
                    print(f"  ⚠️ ROI analysis returned no result")
            except Exception as e:
                print(f"  ⚠️ ROI analysis failed: {e}")
            
            # Bias detection
            try:
                bias_result = bias_detector.analyze_article_bias(article)
                if bias_result:
                    print(f"  ✅ Bias score: {bias_result.neutrality_score:.3f} ({len(bias_result.detected_biases)} biases)")
                else:
                    print(f"  ⚠️ Bias analysis returned no result")
            except Exception as e:
                print(f"  ⚠️ Bias analysis failed: {e}")
            
            evaluated_articles.append(article)
            
        except Exception as e:
            print(f"  ❌ Evaluation failed: {e}")
            # Add article with basic evaluation
            article.evaluation = {
                "engineer": {"total_score": 0.5},
                "business": {"total_score": 0.5}
            }
            evaluated_articles.append(article)
    
    return evaluated_articles


async def main():
    """Main execution function."""
    print("🚀 Real AI News Collection and Evaluation")
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
        result = await generator.generate_complete_site(
            evaluated_articles,
            persona="engineer",
            include_interactive=True,
            include_rss=True,
            include_sitemap=True,
            optimize=True
        )
        
        print(f"✅ Site generated successfully!")
        print(f"📁 Output: {result['output_dir']}")
        print(f"📄 Files: {len(result['files_generated'])}")
        
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