"""Basic tests to verify test setup."""

import pytest
from datetime import datetime


def test_basic_functionality():
    """Test basic Python functionality."""
    assert 1 + 1 == 2
    assert "hello" == "hello"
    assert len([1, 2, 3]) == 3


def test_datetime_functionality():
    """Test datetime functionality."""
    now = datetime.now()
    assert isinstance(now, datetime)
    
    specific_date = datetime(2024, 1, 15, 10, 0, 0)
    assert specific_date.year == 2024
    assert specific_date.month == 1
    assert specific_date.day == 15


def test_fixture_usage(sample_article_data):
    """Test fixture usage."""
    assert "title" in sample_article_data
    assert "url" in sample_article_data
    assert sample_article_data["source_tier"] == 1


def test_mock_feed_response(mock_feed_response):
    """Test mock feed response fixture."""
    assert "<?xml version=" in mock_feed_response
    assert "Test AI News" in mock_feed_response
    assert "Test Article 1" in mock_feed_response


@pytest.mark.asyncio
async def test_async_functionality():
    """Test async functionality."""
    
    async def async_function():
        return "async result"
    
    result = await async_function()
    assert result == "async result"