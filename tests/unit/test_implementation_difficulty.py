"""Unit tests for Implementation Difficulty Indicator."""

import pytest
from unittest.mock import Mock, patch
from src.features.implementation_difficulty import ImplementationDifficultyAnalyzer
from src.models.article import Article, TechnicalMetadata, ComputeRequirements


class TestImplementationDifficultyAnalyzer:
    """Test cases for Implementation Difficulty Analyzer."""

    @pytest.fixture
    def difficulty_analyzer(self, settings):
        """Create difficulty analyzer instance."""
        return ImplementationDifficultyAnalyzer(settings)

    @pytest.mark.unit
    def test_analyze_beginner_level_article(self, difficulty_analyzer, sample_article):
        """Test analysis of beginner-level technical article."""
        # Given - Article with basic implementation
        sample_article.technical.implementation_ready = True
        sample_article.technical.code_available = True
        sample_article.technical.dependencies = ["requests", "json"]
        sample_article.content = "Simple REST API tutorial using Python requests library."
        
        # When
        result = difficulty_analyzer.analyze(sample_article)
        
        # Then
        assert result is not None
        assert "difficulty_level" in result
        assert "skill_requirements" in result
        assert "time_estimate" in result
        assert "resource_requirements" in result
        assert "implementation_steps" in result
        
        assert result["difficulty_level"] in ["beginner", "intermediate", "advanced", "research"]
        assert isinstance(result["skill_requirements"], list)
        assert isinstance(result["time_estimate"], dict)

    @pytest.mark.unit
    def test_analyze_advanced_research_article(self, difficulty_analyzer, sample_article):
        """Test analysis of advanced research article."""
        # Given - Complex research paper
        sample_article.technical.implementation_ready = False
        sample_article.technical.code_available = False
        sample_article.technical.paper_link = "https://arxiv.org/abs/2024.0001"
        sample_article.technical.dependencies = ["torch", "transformers", "accelerate", "deepspeed"]
        sample_article.technical.compute_requirements = ComputeRequirements(
            gpu="8x A100",
            memory="80GB per GPU",
            training_time="2 weeks"
        )
        sample_article.content = "Novel transformer architecture with sparse attention mechanisms..."
        
        # When
        result = difficulty_analyzer.analyze(sample_article)
        
        # Then
        assert result["difficulty_level"] in ["advanced", "research"]
        assert len(result["skill_requirements"]) >= 5
        assert "deep learning" in [skill.lower() for skill in result["skill_requirements"]]
        assert result["time_estimate"]["min_hours"] >= 40

    @pytest.mark.unit
    def test_calculate_complexity_score(self, difficulty_analyzer):
        """Test complexity score calculation."""
        # Given
        factors = {
            "dependencies_count": 10,
            "has_paper": True,
            "code_available": False,
            "gpu_required": True,
            "novel_architecture": True
        }
        
        # When
        score = difficulty_analyzer._calculate_complexity_score(factors)
        
        # Then
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    @pytest.mark.unit
    def test_estimate_time_requirements(self, difficulty_analyzer):
        """Test time estimation for implementation."""
        # Given
        difficulty_level = "intermediate"
        complexity_factors = {
            "code_available": True,
            "dependencies_complex": False,
            "novel_concepts": 2
        }
        
        # When
        time_estimate = difficulty_analyzer._estimate_time_requirements(
            difficulty_level, complexity_factors
        )
        
        # Then
        assert "min_hours" in time_estimate
        assert "max_hours" in time_estimate
        assert "phases" in time_estimate
        assert time_estimate["min_hours"] <= time_estimate["max_hours"]

    @pytest.mark.unit
    def test_identify_skill_requirements(self, difficulty_analyzer, sample_article):
        """Test skill requirement identification."""
        # Given
        sample_article.content = """
        This paper introduces a novel attention mechanism for transformers.
        Implementation requires PyTorch, CUDA programming, and distributed training.
        Mathematical background in linear algebra and optimization is essential.
        """
        
        # When
        skills = difficulty_analyzer._identify_skill_requirements(sample_article)
        
        # Then
        assert isinstance(skills, list)
        assert len(skills) > 0
        assert any("pytorch" in skill.lower() for skill in skills)

    @pytest.mark.unit
    def test_generate_implementation_roadmap(self, difficulty_analyzer):
        """Test implementation roadmap generation."""
        # Given
        analysis_result = {
            "difficulty_level": "intermediate",
            "skill_requirements": ["Python", "PyTorch", "Machine Learning"],
            "time_estimate": {"min_hours": 20, "max_hours": 40}
        }
        
        # When
        roadmap = difficulty_analyzer._generate_implementation_roadmap(analysis_result)
        
        # Then
        assert isinstance(roadmap, list)
        assert len(roadmap) >= 3  # Should have multiple phases
        for phase in roadmap:
            assert "phase" in phase
            assert "description" in phase
            assert "estimated_hours" in phase

    @pytest.mark.unit
    def test_assess_resource_requirements(self, difficulty_analyzer, sample_article):
        """Test resource requirement assessment."""
        # Given
        sample_article.technical.compute_requirements = ComputeRequirements(
            gpu="RTX 4090",
            memory="24GB VRAM",
            training_time="1 day"
        )
        
        # When
        resources = difficulty_analyzer._assess_resource_requirements(sample_article)
        
        # Then
        assert "compute" in resources
        assert "storage" in resources
        assert "network" in resources
        assert "estimated_cost" in resources

    @pytest.mark.unit
    def test_difficulty_progression_consistency(self, difficulty_analyzer):
        """Test that difficulty levels are consistent."""
        # Given - Articles with increasing complexity
        simple_article = Article(
            id="simple", title="Hello World Tutorial", url="", source="", source_tier=1,
            content="print('Hello World')",
            technical=TechnicalMetadata(implementation_ready=True, code_available=True)
        )
        
        complex_article = Article(
            id="complex", title="Novel Transformer Architecture", url="", source="", source_tier=1,
            content="We propose a new sparse attention mechanism...",
            technical=TechnicalMetadata(
                implementation_ready=False,
                code_available=False,
                dependencies=["torch", "transformers", "accelerate", "deepspeed"],
                compute_requirements=ComputeRequirements(gpu="8x A100", memory="640GB", training_time="1 month")
            )
        )
        
        # When
        simple_result = difficulty_analyzer.analyze(simple_article)
        complex_result = difficulty_analyzer.analyze(complex_article)
        
        # Then
        difficulty_order = ["beginner", "intermediate", "advanced", "research"]
        simple_idx = difficulty_order.index(simple_result["difficulty_level"])
        complex_idx = difficulty_order.index(complex_result["difficulty_level"])
        
        assert simple_idx <= complex_idx  # Simple should not be more difficult than complex

    @pytest.mark.unit
    def test_handle_missing_technical_metadata(self, difficulty_analyzer):
        """Test handling of articles with minimal technical metadata."""
        # Given
        minimal_article = Article(
            id="minimal", title="AI News", url="", source="", source_tier=2,
            content="Brief mention of AI advancement.",
            technical=TechnicalMetadata()  # Empty technical metadata
        )
        
        # When
        result = difficulty_analyzer.analyze(minimal_article)
        
        # Then
        assert result is not None
        assert result["difficulty_level"] == "beginner"  # Default for minimal info
        assert len(result["skill_requirements"]) >= 1  # Should have at least basic skills

    @pytest.mark.unit
    def test_cost_estimation_accuracy(self, difficulty_analyzer):
        """Test cost estimation for different resource requirements."""
        # Given
        test_cases = [
            {
                "gpu": "CPU only",
                "expected_cost_range": (0, 50)
            },
            {
                "gpu": "RTX 4090",
                "expected_cost_range": (50, 500)
            },
            {
                "gpu": "8x A100",
                "expected_cost_range": (1000, 10000)
            }
        ]
        
        for test_case in test_cases:
            # When
            cost = difficulty_analyzer._estimate_implementation_cost(
                compute_requirement=test_case["gpu"]
            )
            
            # Then
            min_cost, max_cost = test_case["expected_cost_range"]
            assert min_cost <= cost <= max_cost, f"Cost {cost} not in range {test_case['expected_cost_range']} for {test_case['gpu']}"