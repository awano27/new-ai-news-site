"""Feed collector for RSS and API sources."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

import aiohttp
import feedparser
from bs4 import BeautifulSoup

from src.config.settings import Settings
from src.models.article import Article

logger = logging.getLogger(__name__)


@dataclass
class FeedSource:
    """Representation of a feed source."""
    name: str
    url: str
    tier: int
    source_type: str = "rss"  # rss, api, web
    api_key: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)


class FeedCollector:
    """Collects articles from various feed sources."""
    
    # Tier 1 source configurations
    TIER1_FEEDS = {
        "arxiv": FeedSource(
            name="arXiv",
            url="https://export.arxiv.org/rss/cs.AI",
            tier=1
        ),
        "openai": FeedSource(
            name="OpenAI Blog",
            url="https://openai.com/blog/rss.xml",
            tier=1
        ),
        "anthropic": FeedSource(
            name="Anthropic News",
            url="https://www.anthropic.com/rss.xml",
            tier=1
        ),
        "deepmind": FeedSource(
            name="DeepMind Blog",
            url="https://deepmind.com/blog/feed.xml",
            tier=1
        ),
        "papers-with-code": FeedSource(
            name="Papers with Code",
            url="https://paperswithcode.com/rss",
            tier=1
        ),
        "google-ai": FeedSource(
            name="Google AI Blog",
            url="https://ai.googleblog.com/feeds/posts/default",
            tier=1
        ),
        "meta-ai": FeedSource(
            name="Meta AI Research",
            url="https://ai.meta.com/feed/",
            tier=1
        ),
        "microsoft-research": FeedSource(
            name="Microsoft Research",
            url="https://www.microsoft.com/en-us/research/feed/",
            tier=1
        ),
        "hugging-face": FeedSource(
            name="Hugging Face Blog",
            url="https://huggingface.co/blog/feed.xml",
            tier=1
        ),
    }
    
    # Tier 2 source configurations
    TIER2_FEEDS = {
        "towards-data-science": FeedSource(
            name="Towards Data Science",
            url="https://towardsdatascience.com/feed",
            tier=2
        ),
        "techcrunch": FeedSource(
            name="TechCrunch AI",
            url="https://techcrunch.com/category/artificial-intelligence/feed/",
            tier=2
        ),
        "venturebeat": FeedSource(
            name="VentureBeat AI",
            url="https://venturebeat.com/ai/feed/",
            tier=2
        ),
        "reddit-ml": FeedSource(
            name="Reddit Machine Learning",
            url="https://www.reddit.com/r/MachineLearning/.rss",
            tier=2
        ),
        "hackernews": FeedSource(
            name="Hacker News AI",
            url="https://hnrss.org/newest?q=AI+OR+ML+OR+machine+learning",
            tier=2
        ),
    }
    
    def __init__(self, settings: Settings):
        """Initialize the feed collector."""
        self.settings = settings
        self.session: Optional[aiohttp.ClientSession] = None
        self.sources = self._initialize_sources()
    
    def _initialize_sources(self) -> Dict[str, FeedSource]:
        """Initialize all feed sources based on settings."""
        sources = {}
        
        # Add Tier 1 sources
        for key in self.settings.tier1_sources:
            if key in self.TIER1_FEEDS:
                sources[key] = self.TIER1_FEEDS[key]
        
        # Add Tier 2 sources
        for key in self.settings.tier2_sources:
            if key in self.TIER2_FEEDS:
                sources[key] = self.TIER2_FEEDS[key]
        
        return sources
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def collect_all(self, tier1_only: bool = False) -> List[Article]:
        """Collect articles from all configured sources."""
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Filter sources by tier if needed
            sources_to_collect = [
                source for source in self.sources.values()
                if not tier1_only or source.tier == 1
            ]
            
            # Collect from all sources in parallel
            tasks = [
                self._collect_from_source(source)
                for source in sources_to_collect
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Flatten results and filter out errors
            all_articles = []
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Collection error: {result}")
            
            # Filter by time window
            cutoff_time = datetime.now() - timedelta(hours=self.settings.hours_lookback)
            filtered_articles = [
                article for article in all_articles
                if article.published_date and article.published_date > cutoff_time
            ]
            
            logger.info(f"Collected {len(filtered_articles)} articles within time window")
            return filtered_articles
    
    async def _collect_from_source(self, source: FeedSource) -> List[Article]:
        """Collect articles from a single source."""
        try:
            if source.source_type == "rss":
                return await self._collect_rss(source)
            elif source.source_type == "api":
                return await self._collect_api(source)
            else:
                logger.warning(f"Unsupported source type: {source.source_type}")
                return []
        except Exception as e:
            logger.error(f"Error collecting from {source.name}: {e}")
            return []
    
    async def _collect_rss(self, source: FeedSource) -> List[Article]:
        """Collect articles from an RSS feed."""
        try:
            async with self.session.get(source.url, headers=source.headers) as response:
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries[:self.settings.max_items_per_category]:
                    article = self._parse_rss_entry(entry, source)
                    if article:
                        articles.append(article)
                
                logger.info(f"Collected {len(articles)} articles from {source.name}")
                return articles
                
        except Exception as e:
            logger.error(f"RSS collection error for {source.name}: {e}")
            return []
    
    async def _collect_api(self, source: FeedSource) -> List[Article]:
        """Collect articles from an API endpoint."""
        # Placeholder for API collection logic
        # Will be implemented based on specific API requirements
        return []
    
    def _parse_rss_entry(self, entry: Any, source: FeedSource) -> Optional[Article]:
        """Parse an RSS feed entry into an Article object."""
        try:
            # Extract basic fields
            title = entry.get("title", "")
            url = entry.get("link", "")
            
            # Parse published date
            published_date = None
            if hasattr(entry, "published_parsed"):
                published_date = datetime.fromtimestamp(
                    feedparser._parse_date(entry.published).timestamp()
                )
            
            # Extract content
            content = ""
            if hasattr(entry, "content"):
                content = entry.content[0].value
            elif hasattr(entry, "summary"):
                content = entry.summary
            
            # Clean HTML from content
            if content:
                soup = BeautifulSoup(content, "html.parser")
                content = soup.get_text(strip=True)
            
            # Create article object
            return Article(
                id=self._generate_article_id(url),
                title=title,
                url=url,
                source=source.name,
                source_tier=source.tier,
                published_date=published_date,
                crawled_date=datetime.now(),
                content=content[:5000],  # Limit content length
                tags=entry.get("tags", []),
            )
            
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None
    
    def _generate_article_id(self, url: str) -> str:
        """Generate a unique ID for an article."""
        import hashlib
        return hashlib.sha256(url.encode()).hexdigest()[:16]