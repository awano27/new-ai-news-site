#!/usr/bin/env python3
"""Complete AI news collection from ALL sources specified in requirements."""

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


class CompleteDataCollector:
    """Complete AI news collector with ALL sources from requirements."""
    
    def __init__(self):
        self.sources = {
            # ========================================
            # Tier 1: 最重要ソース（必須）
            # ========================================
            
            # 研究・技術系
            "arxiv_ai": {
                "url": "http://export.arxiv.org/rss/cs.AI/recent",
                "tier": 1,
                "source_name": "ArXiv AI",
                "category": "research"
            },
            "arxiv_ml": {
                "url": "http://export.arxiv.org/rss/cs.LG/recent", 
                "tier": 1,
                "source_name": "ArXiv ML",
                "category": "research"
            },
            "arxiv_cv": {
                "url": "http://export.arxiv.org/rss/cs.CV/recent",
                "tier": 1,
                "source_name": "ArXiv CV",
                "category": "research"
            },
            "arxiv_cl": {
                "url": "http://export.arxiv.org/rss/cs.CL/recent",
                "tier": 1,
                "source_name": "ArXiv NLP",
                "category": "research"
            },
            "papers_with_code": {
                "url": "https://paperswithcode.com/feed.xml",
                "tier": 1,
                "source_name": "Papers with Code",
                "category": "research"
            },
            "google_ai_blog": {
                "url": "https://ai.googleblog.com/feeds/posts/default",
                "tier": 1,
                "source_name": "Google AI Blog",
                "category": "research"
            },
            "openai_blog": {
                "url": "https://openai.com/blog/rss.xml",
                "tier": 1,
                "source_name": "OpenAI Blog",
                "category": "research"
            },
            "anthropic_news": {
                "url": "https://www.anthropic.com/news/rss.xml",
                "tier": 1,
                "source_name": "Anthropic News",
                "category": "research"
            },
            "deepmind_blog": {
                "url": "https://deepmind.google/blog/rss.xml",
                "tier": 1,
                "source_name": "DeepMind Blog",
                "category": "research"
            },
            "meta_ai_research": {
                "url": "https://ai.meta.com/blog/rss/",
                "tier": 1,
                "source_name": "Meta AI Research",
                "category": "research"
            },
            "microsoft_research": {
                "url": "https://www.microsoft.com/en-us/research/feed/",
                "tier": 1,
                "source_name": "Microsoft Research",
                "category": "research"
            },
            "huggingface_blog": {
                "url": "https://huggingface.co/blog/rss.xml",
                "tier": 1,
                "source_name": "Hugging Face Blog",
                "category": "research"
            },
            
            # ビジネス・戦略系
            "mit_tech_review": {
                "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
                "tier": 1,
                "source_name": "MIT Technology Review",
                "category": "business"
            },
            "venturebeat_ai": {
                "url": "https://venturebeat.com/ai/feed/",
                "tier": 1,
                "source_name": "VentureBeat AI",
                "category": "business"
            },
            "the_information": {
                "url": "https://www.theinformation.com/feed",
                "tier": 1,
                "source_name": "The Information",
                "category": "business"
            },
            "cb_insights": {
                "url": "https://www.cbinsights.com/research/rss/",
                "tier": 1,
                "source_name": "CB Insights",
                "category": "business"
            },
            "mckinsey_insights": {
                "url": "https://www.mckinsey.com/featured-insights/rss",
                "tier": 1,
                "source_name": "McKinsey Insights",
                "category": "business"
            },
            "gartner": {
                "url": "https://www.gartner.com/en/newsroom/rss-feeds",
                "tier": 1,
                "source_name": "Gartner",
                "category": "business"
            },
            
            # 日本語専門メディア
            "ai_scholar": {
                "url": "https://ai-scholar.tech/feed/",
                "tier": 1,
                "source_name": "AI-SCHOLAR",
                "category": "japanese"
            },
            "ledge_ai": {
                "url": "https://ledge.ai/feed/",
                "tier": 1,
                "source_name": "Ledge.ai",
                "category": "japanese"
            },
            "aismiley": {
                "url": "https://ai-smiley.co.jp/feed/",
                "tier": 1,
                "source_name": "AIsmiley",
                "category": "japanese"
            },
            "nikkei_xtech": {
                "url": "https://xtech.nikkei.com/rss/nx_ai.rdf",
                "tier": 1,
                "source_name": "日経xTECH AI",
                "category": "japanese"
            },
            
            # ========================================
            # Tier 2: 重要ソース
            # ========================================
            
            # 開発者コミュニティ
            "github_trending": {
                "url": "https://mshibanami.github.io/GitHubTrendingRSS/weekly/python.xml",
                "tier": 2,
                "source_name": "GitHub Trending Python",
                "category": "community"
            },
            "towards_data_science": {
                "url": "https://towardsdatascience.com/feed/tagged/artificial-intelligence",
                "tier": 2,
                "source_name": "Towards Data Science",
                "category": "tutorial"
            },
            "ml_mastery": {
                "url": "https://machinelearningmastery.com/feed/",
                "tier": 2,
                "source_name": "ML Mastery",
                "category": "tutorial"
            },
            "pyimagesearch": {
                "url": "https://pyimagesearch.com/feed/",
                "tier": 2,
                "source_name": "PyImageSearch",
                "category": "tutorial"
            },
            "reddit_ml": {
                "url": "https://www.reddit.com/r/MachineLearning/.rss",
                "tier": 2,
                "source_name": "Reddit ML",
                "category": "community"
            },
            "reddit_ai": {
                "url": "https://www.reddit.com/r/artificial/.rss",
                "tier": 2,
                "source_name": "Reddit AI",
                "category": "community"
            },
            
            # テック系メディア
            "techcrunch_ai": {
                "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
                "tier": 2,
                "source_name": "TechCrunch AI",
                "category": "news"
            },
            "the_verge_ai": {
                "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
                "tier": 2,
                "source_name": "The Verge AI",
                "category": "news"
            },
            "wired_ai": {
                "url": "https://www.wired.com/feed/tag/ai/latest/rss",
                "tier": 2,
                "source_name": "Wired AI",
                "category": "news"
            },
            "ars_technica": {
                "url": "http://feeds.arstechnica.com/arstechnica/technology-lab",
                "tier": 2,
                "source_name": "Ars Technica",
                "category": "news"
            },
            
            # 学術・研究機関
            "stanford_hai": {
                "url": "https://hai.stanford.edu/news/rss",
                "tier": 2,
                "source_name": "Stanford HAI",
                "category": "academic"
            },
            "mit_csail": {
                "url": "https://www.csail.mit.edu/news/rss.xml",
                "tier": 2,
                "source_name": "MIT CSAIL",
                "category": "academic"
            },
            "berkeley_ai": {
                "url": "https://bair.berkeley.edu/blog/feed.xml",
                "tier": 2,
                "source_name": "Berkeley AI Research",
                "category": "academic"
            },
            "cmu_ml": {
                "url": "https://blog.ml.cmu.edu/feed/",
                "tier": 2,
                "source_name": "CMU ML Blog",
                "category": "academic"
            },
            
            # 技術系専門メディア
            "ieee_spectrum": {
                "url": "https://spectrum.ieee.org/rss/artificial-intelligence/fulltext",
                "tier": 2,
                "source_name": "IEEE Spectrum AI",
                "category": "technical"
            },
            "acm_news": {
                "url": "https://technews.acm.org/rss.cfm",
                "tier": 2,
                "source_name": "ACM TechNews",
                "category": "technical"
            },
            
            # コミュニティ・フォーラム
            "hackernews_ai": {
                "url": "https://hnrss.org/newest?q=AI+OR+artificial+intelligence+OR+machine+learning+OR+neural+network+OR+deep+learning",
                "tier": 2,
                "source_name": "Hacker News AI",
                "category": "community"
            },
            "lobsters_ai": {
                "url": "https://lobste.rs/rss?tags=ai",
                "tier": 2,
                "source_name": "Lobsters AI",
                "category": "community"
            },
            
            # 企業・スタートアップ
            "ai_business": {
                "url": "https://aibusiness.com/rss.xml",
                "tier": 2,
                "source_name": "AI Business",
                "category": "business"
            },
            "analytics_insight": {
                "url": "https://www.analyticsinsight.net/feed/",
                "tier": 2,
                "source_name": "Analytics Insight",
                "category": "business"
            },
            
            # 追加の研究・開発系
            "distill_pub": {
                "url": "https://distill.pub/rss.xml",
                "tier": 1,
                "source_name": "Distill",
                "category": "research"
            },
            "openreview": {
                "url": "https://openreview.net/rss",
                "tier": 1,
                "source_name": "OpenReview",
                "category": "research"
            }
        }
        
        # Alternative URLs for failed sources
        self.alternative_urls = {
            "google_ai_blog": "https://blog.research.google/feeds/posts/default",
            "anthropic_news": "https://anthropic.com/news",
            "meta_ai_research": "https://ai.facebook.com/blog/rss/",
            "the_information": "https://theinformation.com/rss",
            "cb_insights": "https://cbinsights.com/research-artificial-intelligence",
            "mckinsey_insights": "https://mckinsey.com/capabilities/quantumblack/our-insights",
            "gartner": "https://gartner.com/en/newsroom",
            "papers_with_code": "https://paperswithcode.com/latest",
            "huggingface_blog": "https://huggingface.co/blog",
            "towards_data_science": "https://medium.com/towards-data-science/tagged/artificial-intelligence/feed",
            "the_verge_ai": "https://theverge.com/ai",
            "ars_technica": "https://arstechnica.com/tag/artificial-intelligence/feed/"
        }
    
    def get_working_url(self, source_key: str, original_url: str) -> str:
        """Get working URL, trying alternatives if original fails."""
        # Try original first
        try:
            response = requests.head(original_url, timeout=5)
            if response.status_code == 200:
                return original_url
        except:
            pass
        
        # Try alternative if available
        if source_key in self.alternative_urls:
            alt_url = self.alternative_urls[source_key]
            try:
                response = requests.head(alt_url, timeout=5)
                if response.status_code == 200:
                    return alt_url
            except:
                pass
        
        return original_url  # Return original if no working alternative found
    
    def collect_from_feed(self, feed_config: Dict, max_articles: int = 2) -> List[Article]:
        """Collect articles from a single RSS feed with error handling."""
        articles = []
        
        try:
            print(f"📡 Collecting from {feed_config['source_name']} ({feed_config['category']})...")
            
            # Get working URL
            working_url = self.get_working_url(feed_config['source_name'].lower().replace(' ', '_'), feed_config['url'])
            
            headers = {
                'User-Agent': 'DailyAINews/1.0 (Educational Project; +https://github.com/user/daily-ai-news)',
                'Accept': 'application/rss+xml, application/xml, text/xml, application/atom+xml',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate'
            }
            
            response = requests.get(working_url, headers=headers, timeout=20, allow_redirects=True)
            
            if response.status_code == 403:
                print(f"⚠️ Access forbidden (403) for {feed_config['source_name']} - may require authentication")
                return articles
            elif response.status_code == 404:
                print(f"⚠️ Feed not found (404) for {feed_config['source_name']}")
                return articles
            elif response.status_code != 200:
                print(f"⚠️ HTTP {response.status_code} for {feed_config['source_name']}")
                return articles
            
            # Parse feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo and feed.bozo_exception:
                print(f"⚠️ Feed parsing warning for {feed_config['source_name']}: {str(feed.bozo_exception)[:100]}")
            
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                print(f"⚠️ No entries found in feed for {feed_config['source_name']}")
                return articles
            
            processed_count = 0
            for entry in feed.entries:
                if processed_count >= max_articles:
                    break
                    
                try:
                    # Parse publication date
                    pub_date = None
                    for date_field in ['published_parsed', 'updated_parsed', 'created_parsed']:
                        if hasattr(entry, date_field) and getattr(entry, date_field):
                            try:
                                pub_date = datetime(*getattr(entry, date_field)[:6])
                                break
                            except (ValueError, TypeError):
                                continue
                    
                    if not pub_date:
                        pub_date = datetime.now()
                    
                    # Skip very old articles (older than 90 days)
                    if pub_date < datetime.now() - timedelta(days=90):
                        continue
                    
                    # Get title
                    title = ""
                    if hasattr(entry, 'title'):
                        title = entry.title.strip()
                    elif hasattr(entry, 'title_detail') and entry.title_detail:
                        title = entry.title_detail.value.strip()
                    
                    if not title or len(title) < 10:
                        continue
                    
                    # Get content
                    content = ""
                    content_sources = ['summary', 'description', 'content']
                    
                    for source in content_sources:
                        if hasattr(entry, source):
                            attr = getattr(entry, source)
                            if isinstance(attr, str):
                                content = attr
                                break
                            elif isinstance(attr, list) and len(attr) > 0:
                                if hasattr(attr[0], 'value'):
                                    content = attr[0].value
                                else:
                                    content = str(attr[0])
                                break
                            elif hasattr(attr, 'value'):
                                content = attr.value
                                break
                    
                    # Clean HTML tags and normalize whitespace
                    content = re.sub(r'<[^>]+>', '', content)
                    content = re.sub(r'\s+', ' ', content).strip()
                    content = re.sub(r'&[a-zA-Z0-9#]+;', '', content)  # Remove HTML entities
                    
                    # Skip if content is too short
                    if len(content) < 50:
                        continue
                    
                    # Get URL
                    url = ""
                    if hasattr(entry, 'link'):
                        url = entry.link
                    elif hasattr(entry, 'id'):
                        url = entry.id
                    
                    # Create unique ID
                    id_source = url if url else (title + feed_config['source_name'])
                    article_id = f"{feed_config['source_name'].lower().replace(' ', '_')}_{abs(hash(id_source)) % 100000}"
                    
                    # Create article
                    article = Article(
                        id=article_id,
                        title=title,
                        url=url,
                        source=feed_config['source_name'],
                        source_tier=feed_config['tier'],
                        published_date=pub_date,
                        content=content[:2000],  # Limit content length
                        tags=[feed_config['category']]
                    )
                    
                    articles.append(article)
                    processed_count += 1
                    
                except Exception as e:
                    print(f"⚠️ Error processing entry from {feed_config['source_name']}: {str(e)[:100]}")
                    continue
            
            if len(articles) > 0:
                print(f"✅ Collected {len(articles)} articles from {feed_config['source_name']}")
            else:
                print(f"📭 No valid articles collected from {feed_config['source_name']}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout collecting from {feed_config['source_name']}")
        except requests.exceptions.ConnectionError:
            print(f"🔌 Connection error for {feed_config['source_name']}")
        except requests.exceptions.RequestException as e:
            print(f"📡 Network error for {feed_config['source_name']}: {str(e)[:100]}")
        except Exception as e:
            print(f"❌ Unexpected error for {feed_config['source_name']}: {str(e)[:100]}")
        
        return articles
    
    def collect_all(self, max_per_source: int = 2) -> List[Article]:
        """Collect from all sources with comprehensive error handling."""
        all_articles = []
        collection_stats = {
            "tier_1": {"attempted": 0, "successful": 0, "articles": 0},
            "tier_2": {"attempted": 0, "successful": 0, "articles": 0},
            "categories": {},
            "failed_sources": []
        }
        
        print(f"🚀 Starting collection from {len(self.sources)} sources...")
        print(f"📊 Max articles per source: {max_per_source}")
        print("-" * 60)
        
        # Collect from each source with detailed tracking
        for source_key, feed_config in self.sources.items():
            tier = feed_config["tier"]
            category = feed_config["category"]
            
            # Update attempt counters
            if tier == 1:
                collection_stats["tier_1"]["attempted"] += 1
            else:
                collection_stats["tier_2"]["attempted"] += 1
            
            # Collect articles
            articles = self.collect_from_feed(feed_config, max_per_source)
            
            # Update success counters
            if len(articles) > 0:
                all_articles.extend(articles)
                if tier == 1:
                    collection_stats["tier_1"]["successful"] += 1
                    collection_stats["tier_1"]["articles"] += len(articles)
                else:
                    collection_stats["tier_2"]["successful"] += 1
                    collection_stats["tier_2"]["articles"] += len(articles)
                
                # Category tracking
                if category not in collection_stats["categories"]:
                    collection_stats["categories"][category] = {"sources": 0, "articles": 0}
                collection_stats["categories"][category]["sources"] += 1
                collection_stats["categories"][category]["articles"] += len(articles)
            else:
                collection_stats["failed_sources"].append(feed_config["source_name"])
            
            # Rate limiting - be respectful
            time.sleep(1.5)
        
        # Remove duplicates
        print("\n🔍 Removing duplicates...")
        unique_articles = self._remove_duplicates(all_articles)
        
        # Print comprehensive summary
        self._print_collection_summary(collection_stats, len(all_articles), len(unique_articles))
        
        return unique_articles
    
    def _remove_duplicates(self, articles: List[Article]) -> List[Article]:
        """Advanced duplicate removal."""
        unique_articles = []
        seen_titles = set()
        seen_urls = set()
        
        # Sort by source tier and date to prioritize better sources
        articles.sort(key=lambda x: (x.source_tier, -(x.published_date.timestamp() if x.published_date else 0)))
        
        for article in articles:
            # Normalize title for comparison
            title_key = re.sub(r'[^\w\s]', '', article.title.lower()).replace(' ', '')[:60]
            url_key = article.url.lower() if article.url else ""
            
            # Skip if we've seen this title or URL
            title_similar = any(self._similarity_score(title_key, seen_title) > 0.8 for seen_title in seen_titles)
            url_duplicate = url_key and url_key in seen_urls
            
            if title_similar or url_duplicate:
                continue
            
            seen_titles.add(title_key)
            if url_key:
                seen_urls.add(url_key)
            unique_articles.append(article)
        
        return unique_articles
    
    def _similarity_score(self, s1: str, s2: str) -> float:
        """Calculate simple similarity score between two strings."""
        if not s1 or not s2:
            return 0.0
        
        # Simple character-based similarity
        set1, set2 = set(s1), set(s2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _print_collection_summary(self, stats: Dict, total_articles: int, unique_articles: int):
        """Print comprehensive collection summary."""
        print(f"\n📊 COMPLETE COLLECTION SUMMARY")
        print("=" * 60)
        
        # Tier summary
        tier1 = stats["tier_1"]
        tier2 = stats["tier_2"]
        
        print(f"🔴 Tier 1: {tier1['successful']}/{tier1['attempted']} sources successful ({tier1['articles']} articles)")
        print(f"🟡 Tier 2: {tier2['successful']}/{tier2['attempted']} sources successful ({tier2['articles']} articles)")
        
        # Category breakdown
        print(f"\n📂 By Category:")
        for category, data in sorted(stats["categories"].items()):
            print(f"   {category.title()}: {data['sources']} sources, {data['articles']} articles")
        
        # Deduplication results
        print(f"\n🔍 Deduplication:")
        print(f"   Raw articles: {total_articles}")
        print(f"   Unique articles: {unique_articles}")
        print(f"   Duplicates removed: {total_articles - unique_articles}")
        
        # Failed sources (if any)
        if stats["failed_sources"]:
            print(f"\n⚠️ Failed Sources ({len(stats['failed_sources'])}):")
            for source in stats["failed_sources"][:10]:  # Show first 10
                print(f"   - {source}")
            if len(stats["failed_sources"]) > 10:
                print(f"   ... and {len(stats['failed_sources']) - 10} more")


class EnhancedEvaluator:
    """Enhanced evaluator for complete source coverage."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def evaluate_article(self, article: Article, persona: str) -> Dict[str, Any]:
        """Comprehensive evaluation with category-specific enhancements."""
        content_lower = (article.title + " " + article.content).lower()
        
        # Enhanced keyword detection
        tech_keywords = {
            'core_ai': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 'ai', 'ml', 'dl'],
            'algorithms': ['algorithm', 'model', 'transformer', 'cnn', 'rnn', 'lstm', 'bert', 'gpt', 'llm'],
            'implementation': ['python', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'code', 'github', 'api'],
            'research': ['paper', 'arxiv', 'research', 'study', 'experiment', 'dataset', 'benchmark'],
            'advanced': ['attention', 'embedding', 'tokenization', 'fine-tuning', 'reinforcement', 'generative']
        }
        
        business_keywords = {
            'financial': ['revenue', 'roi', 'profit', 'cost', 'savings', 'investment', 'funding', 'valuation', 'billion'],
            'market': ['market', 'industry', 'customer', 'adoption', 'growth', 'scale', 'enterprise', 'commercial'],
            'strategy': ['strategy', 'competitive', 'advantage', 'disruption', 'innovation', 'partnership', 'acquisition'],
            'impact': ['productivity', 'efficiency', 'automation', 'transformation', 'optimization', 'performance']
        }
        
        # Calculate category-weighted scores
        tech_score = self._calculate_weighted_keywords(content_lower, tech_keywords)
        business_score = self._calculate_weighted_keywords(content_lower, business_keywords)
        
        # Source tier bonus (enhanced)
        tier_bonus = {1: 0.30, 2: 0.20, 3: 0.10}.get(article.source_tier, 0.0)
        
        # Category-specific bonuses
        category = article.tags[0] if article.tags else "general"
        category_bonus = self._get_category_bonus(category, persona)
        
        # Japanese content bonus
        japanese_bonus = 0.1 if category == "japanese" else 0.0
        
        # Recency bonus
        recency_bonus = self._calculate_recency_bonus(article.published_date)
        
        # Length bonus (substantial content)
        length_bonus = min(0.1, len(article.content) / 10000) if len(article.content) > 500 else 0.0
        
        # Calculate final score
        if persona == "engineer":
            base_score = min(0.75, (tech_score * 0.03) + 0.30)
            total_score = min(1.0, base_score + tier_bonus + category_bonus + recency_bonus + length_bonus)
        else:  # business
            base_score = min(0.75, (business_score * 0.03) + 0.30)
            total_score = min(1.0, base_score + tier_bonus + category_bonus + recency_bonus + length_bonus + japanese_bonus)
        
        # Add controlled diversity
        hash_seed = abs(hash(article.id + persona)) % 100
        diversity_factor = (hash_seed % 60) / 1000  # 0-0.059
        total_score = min(1.0, total_score + diversity_factor)
        
        return {
            "total_score": round(total_score, 3),
            "breakdown": {
                "base_score": round(base_score, 3),
                "tier_bonus": round(tier_bonus, 3),
                "category_bonus": round(category_bonus, 3),
                "recency_bonus": round(recency_bonus, 3),
                "length_bonus": round(length_bonus, 3),
                "japanese_bonus": round(japanese_bonus, 3) if persona == "business" else 0.0,
                "keyword_matches": tech_score if persona == "engineer" else business_score
            }
        }
    
    def _calculate_weighted_keywords(self, content: str, keyword_dict: Dict[str, List[str]]) -> float:
        """Calculate weighted keyword score."""
        total_score = 0.0
        weights = {'core_ai': 1.0, 'algorithms': 1.2, 'implementation': 1.1, 'research': 0.9, 'advanced': 0.8,
                  'financial': 1.2, 'market': 1.0, 'strategy': 0.9, 'impact': 1.1}
        
        for category, keywords in keyword_dict.items():
            matches = sum(1 for keyword in keywords if keyword in content)
            weight = weights.get(category, 1.0)
            total_score += matches * weight
        
        return total_score
    
    def _get_category_bonus(self, category: str, persona: str) -> float:
        """Get category-specific bonus."""
        if persona == "engineer":
            bonuses = {
                'research': 0.15, 'academic': 0.12, 'tutorial': 0.10, 
                'technical': 0.14, 'community': 0.08, 'news': 0.05,
                'japanese': 0.06, 'business': 0.04
            }
        else:  # business
            bonuses = {
                'business': 0.16, 'news': 0.12, 'research': 0.10,
                'academic': 0.08, 'japanese': 0.14, 'community': 0.06,
                'technical': 0.07, 'tutorial': 0.05
            }
        
        return bonuses.get(category, 0.05)
    
    def _calculate_recency_bonus(self, pub_date: datetime) -> float:
        """Calculate recency bonus."""
        if not pub_date:
            return 0.0
        
        days_ago = (datetime.now() - pub_date).days
        if days_ago < 3:
            return 0.08
        elif days_ago < 7:
            return 0.05
        elif days_ago < 30:
            return 0.02
        else:
            return 0.0


async def evaluate_articles(articles: List[Article], settings: Settings) -> List[Article]:
    """Comprehensive article evaluation."""
    print(f"\n🔍 Starting comprehensive evaluation for {len(articles)} articles...")
    
    evaluator = EnhancedEvaluator(settings)
    evaluated_articles = []
    
    for i, article in enumerate(articles, 1):
        print(f"\n📊 Evaluating article {i:2}/{len(articles)}: {article.title[:50]}...")
        
        try:
            # Evaluate for both personas
            engineer_eval = await evaluator.evaluate_article(article, persona="engineer")
            business_eval = await evaluator.evaluate_article(article, persona="business")
            
            article.evaluation = {
                "engineer": engineer_eval,
                "business": business_eval
            }
            
            print(f"  ✅ Engineer: {engineer_eval.get('total_score', 0):.3f} | Business: {business_eval.get('total_score', 0):.3f}")
            print(f"  📂 {article.source} ({article.tags[0] if article.tags else 'general'})")
            
            # Enhanced metadata
            content_lower = (article.title + " " + article.content).lower()
            
            # Technical metadata
            has_code = any(term in content_lower for term in ['github', 'code', 'python', 'tensorflow', 'pytorch'])
            has_research = any(term in content_lower for term in ['arxiv', 'paper', 'research', 'study', 'experiment'])
            
            article.technical = TechnicalMetadata(
                implementation_ready=has_code and 'tutorial' in article.tags,
                code_available=has_code,
                dependencies=[],
                reproducibility_score=0.9 if has_research else 0.7 if has_code else 0.5
            )
            
            # Business metadata
            has_business = any(term in content_lower for term in ['enterprise', 'commercial', 'business', 'roi'])
            complexity_indicators = ['complex', 'advanced', 'research', 'experimental']
            is_complex = any(term in content_lower for term in complexity_indicators)
            
            article.business = BusinessMetadata(
                market_size="Unknown",
                growth_rate=business_eval.get('total_score', 0.5) * 100,
                implementation_cost=ImplementationCost.HIGH if is_complex else 
                                  ImplementationCost.LOW if 'tutorial' in article.tags else 
                                  ImplementationCost.MEDIUM
            )
            
            evaluated_articles.append(article)
            
        except Exception as e:
            print(f"  ⚠️ Evaluation failed: {str(e)[:100]}")
            # Add with basic evaluation
            article.evaluation = {
                "engineer": {"total_score": 0.5},
                "business": {"total_score": 0.5}
            }
            evaluated_articles.append(article)
    
    return evaluated_articles


async def main():
    """Main execution with complete source coverage."""
    print("🚀 COMPLETE AI News Collection & Evaluation")
    print("All sources from requirements specification")
    print("=" * 80)
    
    # Initialize
    settings = Settings()
    collector = CompleteDataCollector()
    
    # Collect from ALL sources
    articles = collector.collect_all(max_per_source=2)
    
    if not articles:
        print("❌ No articles collected from any source.")
        return False
    
    # Evaluate all articles
    evaluated_articles = await evaluate_articles(articles, settings)
    
    # Sort by combined score
    def get_combined_score(article):
        eng = article.evaluation.get("engineer", {}).get("total_score", 0)
        bus = article.evaluation.get("business", {}).get("total_score", 0)
        return (eng + bus) / 2
    
    evaluated_articles.sort(key=get_combined_score, reverse=True)
    
    # Generate comprehensive site
    print(f"\n🏗️ Generating COMPLETE site with {len(evaluated_articles)} articles...")
    
    try:
        generator = StaticSiteGenerator(settings)
        docs_dir = Path("docs")
        
        # Generate assets
        css_content = generator.assets.generate_css()
        (docs_dir / "styles.css").write_text(css_content, encoding='utf-8')
        
        js_content = generator.assets.generate_javascript()
        (docs_dir / "script.js").write_text(js_content, encoding='utf-8')
        
        # Generate comprehensive HTML
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
            title=f"Daily AI News - Complete Analysis ({len(evaluated_articles)} articles)",
            description=f"Complete AI news analysis from {len(set(a.source for a in evaluated_articles))} sources across all major categories",
            persona="engineer"
        )
        
        # Embed comprehensive data
        categories = {}
        sources = {}
        for article in evaluated_articles:
            cat = article.tags[0] if article.tags else 'general'
            categories[cat] = categories.get(cat, 0) + 1
            sources[article.source] = sources.get(article.source, 0) + 1
        
        articles_data = {
            "articles": [{
                "id": a.id,
                "title": a.title,
                "url": a.url,
                "source": a.source,
                "source_tier": a.source_tier,
                "published_date": a.published_date.isoformat() if a.published_date else None,
                "content": a.content[:400] + "..." if len(a.content) > 400 else a.content,
                "evaluation": a.evaluation,
                "tags": a.tags or [],
                "category": a.tags[0] if a.tags else "general"
            } for a in evaluated_articles],
            "metadata": {
                "total_sources": len(sources),
                "total_articles": len(evaluated_articles),
                "categories": categories,
                "sources": sources,
                "generation_time": datetime.now().isoformat(),
                "score_range": {
                    "min": round(min(get_combined_score(a) for a in evaluated_articles), 3),
                    "max": round(max(get_combined_score(a) for a in evaluated_articles), 3)
                },
                "tier_distribution": {
                    "tier_1": len([a for a in evaluated_articles if a.source_tier == 1]),
                    "tier_2": len([a for a in evaluated_articles if a.source_tier == 2])
                }
            }
        }
        
        # Embed data and write HTML
        articles_json = f'<script id="articles-data" type="application/json">{json.dumps(articles_data, ensure_ascii=False)}</script>'
        page_content = page_content.replace('</body>', f'{articles_json}\n</body>')
        
        index_file = docs_dir / "index.html"
        index_file.write_text(page_content, encoding='utf-8')
        
        print(f"✅ COMPLETE site generated successfully!")
        print(f"📁 Output: {docs_dir.absolute()}")
        
        # Show top results
        print(f"\n🏆 TOP 15 Articles (Complete Analysis):")
        for i, article in enumerate(evaluated_articles[:15], 1):
            eng = article.evaluation.get("engineer", {}).get("total_score", 0)
            bus = article.evaluation.get("business", {}).get("total_score", 0)
            combined = (eng + bus) / 2
            category = article.tags[0] if article.tags else "general"
            
            print(f"{i:2}. {article.title[:60]}...")
            print(f"    📊 {combined:.3f} (E:{eng:.3f}, B:{bus:.3f}) | {article.source} | {category}")
            print()
        
        # Final statistics
        print(f"📊 FINAL STATISTICS:")
        print(f"   🎯 Total articles: {len(evaluated_articles)}")
        print(f"   📡 Sources covered: {len(sources)}")
        print(f"   📂 Categories: {len(categories)}")
        print(f"   🔴 Tier 1: {articles_data['metadata']['tier_distribution']['tier_1']} articles")
        print(f"   🟡 Tier 2: {articles_data['metadata']['tier_distribution']['tier_2']} articles")
        print(f"   📈 Score range: {articles_data['metadata']['score_range']['min']:.3f} - {articles_data['metadata']['score_range']['max']:.3f}")
        
        print(f"\n🌐 Open docs/index.html to view the COMPLETE AI news dashboard!")
        
        return True
        
    except Exception as e:
        print(f"❌ Site generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 COMPLETE AI news collection system successfully implemented!")
        print("🚀 All sources from requirements specification are now integrated!")
    else:
        print("\n❌ Process failed. Check error messages above.")
    
    sys.exit(0 if success else 1)