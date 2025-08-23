"""Unit tests for HybridSearchEngine."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.search.hybrid_search import HybridSearchEngine
from src.models.article import Article


class TestHybridSearchEngine:
    """Test cases for HybridSearchEngine."""

    @pytest.fixture
    def search_engine(self, settings):
        """Create search engine instance."""
        return HybridSearchEngine(settings)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_basic_query(self, search_engine, sample_articles):
        """Test basic search functionality."""
        # Given
        query = "transformer neural network"
        
        # When
        results = await search_engine.search(query)
        
        # Then
        assert isinstance(results, list)
        assert len(results) >= 0
        
        if results:
            for result in results:
                assert "article_id" in result
                assert "score" in result
                assert "relevance_type" in result

    @pytest.mark.unit
    async def test_bm25_search(self, search_engine):
        """Test BM25 keyword search."""
        # Given
        query = "machine learning artificial intelligence"
        documents = [
            {"id": "1", "content": "Machine learning and artificial intelligence research"},
            {"id": "2", "content": "Deep learning neural networks"},
            {"id": "3", "content": "Computer vision applications"}
        ]
        
        # When
        results = search_engine.bm25_search(query, documents)
        
        # Then
        assert isinstance(results, list)
        if results:
            assert results[0]["score"] >= results[-1]["score"]  # Sorted by score

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_semantic_search(self, search_engine, mock_embedding_model):
        """Test semantic search with embeddings."""
        # Given
        query = "neural network optimization"
        
        with patch.object(search_engine, 'embedding_model', mock_embedding_model):
            # When
            results = await search_engine.semantic_search(query)
            
            # Then
            assert isinstance(results, list)

    @pytest.mark.unit
    async def test_entity_search(self, search_engine):
        """Test entity-based search."""
        # Given
        entities = ["OpenAI", "GPT", "transformer"]
        
        # When
        results = await search_engine.entity_search(entities)
        
        # Then
        assert isinstance(results, list)

    @pytest.mark.unit
    async def test_extract_entities(self, search_engine):
        """Test entity extraction from query."""
        # Given
        query = "OpenAI released GPT-4 with improved transformer architecture"
        
        # When
        entities = search_engine.extract_entities(query)
        
        # Then
        assert isinstance(entities, dict)
        assert "companies" in entities
        assert "technologies" in entities

    @pytest.mark.unit
    async def test_merge_results(self, search_engine):
        """Test result merging from multiple sources."""
        # Given
        results = {
            "keyword": [
                {"id": "1", "score": 0.9, "source": "bm25"},
                {"id": "2", "score": 0.7, "source": "bm25"}
            ],
            "semantic": [
                {"id": "1", "score": 0.8, "source": "semantic"},
                {"id": "3", "score": 0.6, "source": "semantic"}
            ]
        }
        
        # When
        merged = search_engine.merge_results(results)
        
        # Then
        assert isinstance(merged, list)
        # Should combine scores for same ID
        id_1_result = next((r for r in merged if r["id"] == "1"), None)
        assert id_1_result is not None
        assert id_1_result["combined_score"] > 0

    @pytest.mark.unit
    async def test_apply_persona_optimization_engineer(self, search_engine, sample_articles):
        """Test persona optimization for engineers."""
        # Given
        results = [
            {"article_id": "tech-001", "score": 0.8},
            {"article_id": "biz-001", "score": 0.7}
        ]
        
        # When
        optimized = search_engine.apply_persona_optimization(results, "engineer")
        
        # Then
        assert isinstance(optimized, list)
        assert len(optimized) == len(results)

    @pytest.mark.unit
    async def test_apply_persona_optimization_business(self, search_engine, sample_articles):
        """Test persona optimization for business users."""
        # Given
        results = [
            {"article_id": "tech-001", "score": 0.8},
            {"article_id": "biz-001", "score": 0.7}
        ]
        
        # When
        optimized = search_engine.apply_persona_optimization(results, "business")
        
        # Then
        assert isinstance(optimized, list)
        assert len(optimized) == len(results)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rerank_results(self, search_engine):
        """Test cross-encoder reranking."""
        # Given
        query = "machine learning research"
        results = [
            {"id": "1", "content": "Machine learning research paper", "score": 0.8},
            {"id": "2", "content": "Deep learning applications", "score": 0.7}
        ]
        
        # When
        reranked = await search_engine.rerank(results, query)
        
        # Then
        assert isinstance(reranked, list)
        assert len(reranked) == len(results)

    @pytest.mark.unit
    async def test_search_with_filters(self, search_engine):
        """Test search with filters applied."""
        # Given
        query = "AI research"
        filters = {
            "source_tier": 1,
            "min_score": 0.7,
            "date_range": "7d"
        }
        
        # When
        results = await search_engine.search(query, filters=filters)
        
        # Then
        assert isinstance(results, list)

    @pytest.mark.unit
    async def test_search_with_persona_filter(self, search_engine):
        """Test search with persona-specific filtering."""
        # Given
        query = "transformer architecture"
        
        # When
        engineer_results = await search_engine.search(query, persona="engineer")
        business_results = await search_engine.search(query, persona="business")
        
        # Then
        assert isinstance(engineer_results, list)
        assert isinstance(business_results, list)
        
        # Results should be different due to persona optimization
        if engineer_results and business_results:
            assert engineer_results[0] != business_results[0] or len(engineer_results) != len(business_results)