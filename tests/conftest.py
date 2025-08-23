"""Pytest configuration and fixtures."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, List, Any

from src.config.settings import Settings
from src.models.article import Article, TechnicalMetadata, BusinessMetadata


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings()


@pytest.fixture
def sample_article():
    """Create a sample article for testing."""
    return Article(
        id="test-article-001",
        title="Revolutionary AI Breakthrough: GPT-5 Achieves AGI",
        url="https://example.com/ai-breakthrough",
        source="OpenAI Blog",
        source_tier=1,
        published_date=datetime(2024, 1, 15, 10, 0, 0),
        crawled_date=datetime(2024, 1, 15, 10, 5, 0),
        content="""
        OpenAI has announced a groundbreaking achievement in artificial intelligence 
        with the release of GPT-5, which demonstrates capabilities consistent with 
        Artificial General Intelligence (AGI). The model shows unprecedented performance 
        across multiple domains including reasoning, creativity, and problem-solving.
        
        Key improvements include:
        - 10x improvement in reasoning tasks
        - Native multimodal capabilities 
        - Reduced hallucination rates by 95%
        - Energy efficiency improvements of 50%
        
        The model was trained on a new architecture that combines transformer 
        mechanisms with novel attention patterns, resulting in better understanding 
        of context and improved logical reasoning.
        """,
        technical=TechnicalMetadata(
            implementation_ready=True,
            code_available=False,
            paper_link="https://arxiv.org/abs/2024.0001",
            reproducibility_score=0.7
        ),
        business=BusinessMetadata(
            market_size="$100B",
            growth_rate=15.2,
            implementation_cost="high"
        )
    )


@pytest.fixture
def sample_articles():
    """Create multiple sample articles for testing."""
    articles = []
    
    # Technical article
    articles.append(Article(
        id="tech-001",
        title="Efficient Transformers: A New Architecture for Large Language Models",
        url="https://arxiv.org/abs/2024.0002", 
        source="arXiv",
        source_tier=1,
        content="Technical paper on transformer optimization...",
        technical=TechnicalMetadata(
            implementation_ready=True,
            code_available=True,
            github_repo="https://github.com/research/efficient-transformers"
        )
    ))
    
    # Business article
    articles.append(Article(
        id="biz-001",
        title="AI Startup Raises $100M Series B for Enterprise Solutions",
        url="https://techcrunch.com/ai-startup-funding",
        source="TechCrunch",
        source_tier=2,
        content="Enterprise AI company secures major funding round...",
        business=BusinessMetadata(
            market_size="$50B",
            growth_rate=25.0,
            implementation_cost="medium"
        )
    ))
    
    return articles


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini API client."""
    mock_client = AsyncMock()
    mock_client.extract_with_context.return_value = {
        "title": "Test Article",
        "summary": "This is a test summary",
        "technical_analysis": {
            "difficulty": "intermediate",
            "implementation_ready": True
        },
        "business_analysis": {
            "market_impact": "high",
            "roi_potential": "medium"
        }
    }
    return mock_client


@pytest.fixture
def mock_embedding_model():
    """Mock sentence transformer model."""
    mock_model = Mock()
    mock_model.encode.return_value = [[0.1, 0.2, 0.3] * 128]  # 384-dim vector
    return mock_model


@pytest.fixture
def mock_vector_db():
    """Mock vector database."""
    mock_db = AsyncMock()
    mock_db.search.return_value = [
        {"id": "similar-1", "score": 0.95},
        {"id": "similar-2", "score": 0.87},
        {"id": "similar-3", "score": 0.75}
    ]
    return mock_db


@pytest.fixture
def test_data_dir():
    """Get test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def test_output_dir(tmp_path_factory):
    """Create temporary directory for test outputs."""
    return tmp_path_factory.mktemp("test_outputs")


@pytest.fixture
def mock_feed_response():
    """Mock RSS feed response."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Test AI News</title>
            <description>Test feed for AI news</description>
            <item>
                <title>Test Article 1</title>
                <link>https://example.com/article-1</link>
                <description>Test description 1</description>
                <pubDate>Mon, 15 Jan 2024 10:00:00 GMT</pubDate>
            </item>
            <item>
                <title>Test Article 2</title>
                <link>https://example.com/article-2</link>
                <description>Test description 2</description>
                <pubDate>Mon, 15 Jan 2024 11:00:00 GMT</pubDate>
            </item>
        </channel>
    </rss>"""


# Async test markers
pytest_plugins = ("pytest_asyncio",)