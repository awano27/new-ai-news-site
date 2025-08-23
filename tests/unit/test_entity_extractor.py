"""Unit tests for EntityExtractor."""

import pytest
from unittest.mock import Mock, patch
from src.processors.entity_extractor import EntityExtractor
from src.models.article import Article, Entities


class TestEntityExtractor:
    """Test cases for EntityExtractor."""

    @pytest.fixture
    def entity_extractor(self, settings):
        """Create entity extractor instance."""
        return EntityExtractor(settings)

    @pytest.mark.unit
    async def test_extract_entities_from_text(self, entity_extractor):
        """Test entity extraction from raw text."""
        # Given
        text = """
        OpenAI announced GPT-4, a new transformer-based language model.
        The model was developed by Sam Altman's team using PyTorch and 
        shows improvements in natural language processing tasks.
        Microsoft has invested heavily in this technology.
        """
        
        # When
        entities = await entity_extractor.extract_entities(text)
        
        # Then
        assert isinstance(entities, Entities)
        assert len(entities.companies) >= 2  # OpenAI, Microsoft
        assert len(entities.technologies) >= 2  # GPT-4, PyTorch
        assert len(entities.people) >= 1  # Sam Altman

    @pytest.mark.unit
    async def test_extract_entities_from_article(self, entity_extractor, sample_article):
        """Test entity extraction from article object."""
        # When
        entities = await entity_extractor.extract_from_article(sample_article)
        
        # Then
        assert isinstance(entities, Entities)
        assert len(entities.companies) > 0
        assert len(entities.technologies) > 0

    @pytest.mark.unit
    async def test_extract_companies(self, entity_extractor):
        """Test company entity extraction."""
        # Given
        text = "Google, Microsoft, and Meta are leading AI research companies."
        
        # When
        companies = entity_extractor.extract_companies(text)
        
        # Then
        assert isinstance(companies, list)
        assert len(companies) >= 3
        assert "Google" in companies
        assert "Microsoft" in companies
        assert "Meta" in companies

    @pytest.mark.unit
    async def test_extract_technologies(self, entity_extractor):
        """Test technology entity extraction."""
        # Given
        text = "The system uses TensorFlow, PyTorch, and CUDA for training transformer models."
        
        # When
        technologies = entity_extractor.extract_technologies(text)
        
        # Then
        assert isinstance(technologies, list)
        assert len(technologies) >= 3
        assert "TensorFlow" in technologies
        assert "PyTorch" in technologies
        assert "CUDA" in technologies

    @pytest.mark.unit
    async def test_extract_people(self, entity_extractor):
        """Test person entity extraction."""
        # Given
        text = "Yoshua Bengio and Geoffrey Hinton are pioneers in deep learning research."
        
        # When
        people = entity_extractor.extract_people(text)
        
        # Then
        assert isinstance(people, list)
        assert len(people) >= 2
        assert any("Bengio" in person for person in people)
        assert any("Hinton" in person for person in people)

    @pytest.mark.unit
    async def test_extract_concepts(self, entity_extractor):
        """Test concept entity extraction."""
        # Given
        text = "Machine learning, neural networks, and reinforcement learning are key AI concepts."
        
        # When
        concepts = entity_extractor.extract_concepts(text)
        
        # Then
        assert isinstance(concepts, list)
        assert len(concepts) >= 2
        assert any("machine learning" in concept.lower() for concept in concepts)
        assert any("neural network" in concept.lower() for concept in concepts)

    @pytest.mark.unit
    async def test_extract_products(self, entity_extractor):
        """Test product entity extraction."""
        # Given
        text = "ChatGPT, Claude, and Bard are popular AI chatbot products."
        
        # When
        products = entity_extractor.extract_products(text)
        
        # Then
        assert isinstance(products, list)
        assert len(products) >= 2
        assert "ChatGPT" in products
        assert "Claude" in products

    @pytest.mark.unit
    async def test_normalize_entities(self, entity_extractor):
        """Test entity normalization."""
        # Given
        entities = ["OpenAI", "openai", "Open AI", "OPENAI"]
        
        # When
        normalized = entity_extractor.normalize_entities(entities)
        
        # Then
        assert isinstance(normalized, list)
        assert len(normalized) < len(entities)  # Should deduplicate
        assert "OpenAI" in normalized

    @pytest.mark.unit
    async def test_filter_entities_by_confidence(self, entity_extractor):
        """Test entity filtering by confidence score."""
        # Given
        entities_with_confidence = [
            {"text": "OpenAI", "confidence": 0.95},
            {"text": "AI", "confidence": 0.6},
            {"text": "Microsoft", "confidence": 0.9},
            {"text": "tech", "confidence": 0.3}
        ]
        threshold = 0.7
        
        # When
        filtered = entity_extractor.filter_by_confidence(entities_with_confidence, threshold)
        
        # Then
        assert isinstance(filtered, list)
        assert len(filtered) == 2  # Only high-confidence entities
        assert all(e["confidence"] >= threshold for e in filtered)

    @pytest.mark.unit
    async def test_empty_text_returns_empty_entities(self, entity_extractor):
        """Test that empty text returns empty entities."""
        # Given
        text = ""
        
        # When
        entities = await entity_extractor.extract_entities(text)
        
        # Then
        assert isinstance(entities, Entities)
        assert len(entities.companies) == 0
        assert len(entities.technologies) == 0
        assert len(entities.people) == 0
        assert len(entities.concepts) == 0
        assert len(entities.products) == 0

    @pytest.mark.unit
    async def test_extract_with_custom_patterns(self, entity_extractor):
        """Test extraction with custom regex patterns."""
        # Given
        text = "Model achieved 95.2% accuracy on GLUE benchmark with 175B parameters."
        
        # When
        entities = await entity_extractor.extract_entities(text)
        
        # Then
        # Should extract benchmarks and model specs
        assert len(entities.concepts) > 0