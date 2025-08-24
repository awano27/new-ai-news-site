"""Pytest configuration and fixtures."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, List, Any


@pytest.fixture
def sample_article_data():
    """Create sample article data for testing."""
    return {
        "id": "test-article-001",
        "title": "Revolutionary AI Breakthrough: GPT-5 Achieves AGI",
        "url": "https://example.com/ai-breakthrough",
        "source": "OpenAI Blog",
        "source_tier": 1,
        "published_date": datetime(2024, 1, 15, 10, 0, 0),
        "crawled_date": datetime(2024, 1, 15, 10, 5, 0),
        "content": """
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
        """
    }


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
def test_data_dir():
    """Get test data directory."""
    return Path(__file__).parent / "data"


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