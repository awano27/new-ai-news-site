"""Unit tests for MultiLayerEvaluator."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.evaluators.multi_layer_evaluator import MultiLayerEvaluator
from src.models.article import Article


class TestMultiLayerEvaluator:
    """Test cases for MultiLayerEvaluator."""

    @pytest.fixture
    def evaluator(self, settings):
        """Create evaluator instance."""
        return MultiLayerEvaluator(settings)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_evaluate_engineer_persona(self, evaluator, sample_article):
        """Test evaluation for engineer persona."""
        # When
        result = await evaluator.evaluate(sample_article, persona="engineer")
        
        # Then
        assert result is not None
        assert "total_score" in result
        assert "breakdown" in result
        assert result["total_score"] >= 0.0
        assert result["total_score"] <= 1.0
        
        # Check breakdown components
        breakdown = result["breakdown"]
        assert "technical_depth" in breakdown
        assert "implementation" in breakdown
        assert "novelty" in breakdown
        assert "reproducibility" in breakdown
        assert "community_impact" in breakdown

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_evaluate_business_persona(self, evaluator, sample_article):
        """Test evaluation for business persona."""
        # When
        result = await evaluator.evaluate(sample_article, persona="business")
        
        # Then
        assert result is not None
        assert "total_score" in result
        assert "breakdown" in result
        assert result["total_score"] >= 0.0
        assert result["total_score"] <= 1.0
        
        # Check breakdown components
        breakdown = result["breakdown"]
        assert "business_impact" in breakdown
        assert "roi_potential" in breakdown
        assert "market_validation" in breakdown
        assert "implementation_ease" in breakdown
        assert "strategic_value" in breakdown

    @pytest.mark.unit
    async def test_assess_quality(self, evaluator, sample_article):
        """Test content quality assessment."""
        # When
        quality_score = evaluator.assess_quality(sample_article)
        
        # Then
        assert isinstance(quality_score, float)
        assert 0.0 <= quality_score <= 1.0

    @pytest.mark.unit
    async def test_calculate_relevance_engineer(self, evaluator, sample_article):
        """Test relevance calculation for engineers."""
        # When
        relevance_score = evaluator.calculate_relevance(sample_article, "engineer")
        
        # Then
        assert isinstance(relevance_score, float)
        assert 0.0 <= relevance_score <= 1.0

    @pytest.mark.unit
    async def test_calculate_relevance_business(self, evaluator, sample_article):
        """Test relevance calculation for business users."""
        # When
        relevance_score = evaluator.calculate_relevance(sample_article, "business")
        
        # Then
        assert isinstance(relevance_score, float)
        assert 0.0 <= relevance_score <= 1.0

    @pytest.mark.unit
    async def test_calculate_temporal_value(self, evaluator, sample_article):
        """Test temporal value calculation."""
        # When
        temporal_score = evaluator.calculate_temporal_value(sample_article)
        
        # Then
        assert isinstance(temporal_score, float)
        assert 0.0 <= temporal_score <= 1.0

    @pytest.mark.unit
    async def test_calculate_trust_score(self, evaluator, sample_article):
        """Test trust score calculation."""
        # When
        trust_score = evaluator.calculate_trust_score(sample_article)
        
        # Then
        assert isinstance(trust_score, float)
        assert 0.0 <= trust_score <= 1.0

    @pytest.mark.unit
    async def test_calculate_actionability(self, evaluator, sample_article):
        """Test actionability score calculation."""
        # When
        action_score = evaluator.calculate_actionability(sample_article, "engineer")
        
        # Then
        assert isinstance(action_score, float)
        assert 0.0 <= action_score <= 1.0

    @pytest.mark.unit
    async def test_invalid_persona_raises_error(self, evaluator, sample_article):
        """Test that invalid persona raises ValueError."""
        # When/Then
        with pytest.raises(ValueError, match="Unknown persona"):
            await evaluator.evaluate(sample_article, persona="invalid")

    @pytest.mark.unit
    async def test_weighted_sum_calculation(self, evaluator):
        """Test weighted sum calculation."""
        # Given
        scores = [0.8, 0.6, 0.9, 0.7, 0.5]
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]
        
        # When
        result = evaluator.weighted_sum(scores, weights)
        
        # Then
        expected = sum(s * w for s, w in zip(scores, weights))
        assert abs(result - expected) < 1e-6

    @pytest.mark.unit
    async def test_generate_recommendation(self, evaluator):
        """Test recommendation generation."""
        # Given
        scores = {
            "total_score": 0.85,
            "breakdown": {
                "quality": 0.9,
                "relevance": 0.8,
                "temporal": 0.7,
                "trust": 0.9,
                "actionability": 0.8
            }
        }
        
        # When
        recommendation = evaluator.generate_recommendation(scores)
        
        # Then
        assert isinstance(recommendation, str)
        assert len(recommendation) > 0
        assert recommendation in ["highly_recommended", "recommended", "consider", "skip"]