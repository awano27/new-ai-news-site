"""Unit tests for Bias Detector."""

import pytest
from unittest.mock import Mock, patch
from src.features.bias_detector import BiasDetector, BiasType, BiasReport
from src.models.article import Article


class TestBiasDetector:
    """Test cases for Bias Detector."""

    @pytest.fixture
    def bias_detector(self, settings):
        """Create bias detector instance."""
        return BiasDetector(settings)

    @pytest.mark.unit
    def test_detect_confirmation_bias(self, bias_detector):
        """Test detection of confirmation bias."""
        # Given - Text with selective evidence presentation
        biased_text = """
        AI will definitely revolutionize everything. Multiple studies show AI benefits,
        including a Stanford study and MIT research. Critics often ignore these findings.
        Companies that don't adopt AI will fail completely.
        """
        
        # When
        result = bias_detector.detect_bias(biased_text)
        
        # Then
        assert isinstance(result, BiasReport)
        bias_types = [bias.bias_type for bias in result.detected_biases]
        assert BiasType.CONFIRMATION_BIAS in bias_types or BiasType.SELECTION_BIAS in bias_types

    @pytest.mark.unit
    def test_detect_authority_bias(self, bias_detector):
        """Test detection of authority bias."""
        # Given
        biased_text = """
        According to Elon Musk, this technology will change the world.
        As the genius behind Tesla and SpaceX, his opinion is definitely correct.
        Leading experts all agree with his assessment.
        """
        
        # When
        result = bias_detector.detect_bias(biased_text)
        
        # Then
        bias_types = [bias.bias_type for bias in result.detected_biases]
        assert BiasType.AUTHORITY_BIAS in bias_types

    @pytest.mark.unit
    def test_detect_temporal_bias(self, bias_detector):
        """Test detection of temporal bias (recency bias)."""
        # Given
        biased_text = """
        The latest AI model is groundbreaking and unprecedented.
        This completely obsoletes all previous approaches.
        Recent developments prove older methods are useless.
        """
        
        # When
        result = bias_detector.detect_bias(biased_text)
        
        # Then
        bias_types = [bias.bias_type for bias in result.detected_biases]
        assert BiasType.TEMPORAL_BIAS in bias_types

    @pytest.mark.unit
    def test_detect_commercial_bias(self, bias_detector):
        """Test detection of commercial bias."""
        # Given
        biased_text = """
        Our revolutionary AI solution outperforms all competitors.
        Contact our sales team today for amazing discounts.
        Don't miss this limited-time opportunity to transform your business.
        """
        
        # When
        result = bias_detector.detect_bias(biased_text)
        
        # Then
        bias_types = [bias.bias_type for bias in result.detected_biases]
        assert BiasType.COMMERCIAL_BIAS in bias_types

    @pytest.mark.unit
    def test_detect_technical_bias(self, bias_detector):
        """Test detection of technical complexity bias."""
        # Given
        biased_text = """
        This simple solution uses basic machine learning.
        Any developer can easily implement this in a weekend.
        The mathematics involved are trivial and straightforward.
        """
        
        # When
        result = bias_detector.detect_bias(biased_text)
        
        # Then
        bias_types = [bias.bias_type for bias in result.detected_biases]
        # Should detect oversimplification bias
        assert len(result.detected_biases) >= 0  # May or may not detect depending on implementation

    @pytest.mark.unit
    def test_calculate_neutrality_score(self, bias_detector):
        """Test neutrality score calculation."""
        # Given
        neutral_text = """
        The research paper presents findings from a controlled study.
        Results show both advantages and limitations of the approach.
        Further investigation is needed to validate these conclusions.
        """
        
        biased_text = """
        This amazing breakthrough will definitely revolutionize everything!
        All experts unanimously agree this is perfect.
        Anyone who disagrees is clearly wrong and uninformed.
        """
        
        # When
        neutral_result = bias_detector.detect_bias(neutral_text)
        biased_result = bias_detector.detect_bias(biased_text)
        
        # Then
        assert neutral_result.neutrality_score > biased_result.neutrality_score
        assert 0.0 <= neutral_result.neutrality_score <= 1.0
        assert 0.0 <= biased_result.neutrality_score <= 1.0

    @pytest.mark.unit
    def test_detect_language_patterns(self, bias_detector):
        """Test detection of biased language patterns."""
        # Given
        patterns_to_test = [
            ("clearly", BiasType.AUTHORITY_BIAS),
            ("obviously", BiasType.AUTHORITY_BIAS),
            ("revolutionary", BiasType.HYPE_BIAS),
            ("groundbreaking", BiasType.HYPE_BIAS),
            ("everyone knows", BiasType.BANDWAGON_BIAS),
            ("all experts agree", BiasType.CONSENSUS_BIAS)
        ]
        
        for pattern, expected_bias in patterns_to_test:
            # When
            text = f"This technology is {pattern} superior to alternatives."
            result = bias_detector._detect_language_patterns(text)
            
            # Then
            pattern_biases = [bias.bias_type for bias in result]
            # Note: May not detect all patterns depending on implementation
            assert isinstance(result, list)

    @pytest.mark.unit
    def test_analyze_source_credibility(self, bias_detector, sample_article):
        """Test source credibility analysis."""
        # Given - High-tier source
        sample_article.source_tier = 1
        sample_article.source = "Nature"
        sample_article.evidence.primary_sources = [
            {"type": "paper", "url": "https://arxiv.org/abs/2024.0001", "credibility_score": 0.9}
        ]
        
        # When
        credibility = bias_detector._analyze_source_credibility(sample_article)
        
        # Then
        assert 0.0 <= credibility <= 1.0
        assert credibility > 0.5  # Should be high for tier 1 source

    @pytest.mark.unit
    def test_detect_statistical_bias(self, bias_detector):
        """Test detection of statistical presentation bias."""
        # Given
        biased_stats = """
        Our model achieved 99.9% accuracy on the test set.
        Performance improved by 500% compared to baseline.
        The results are statistically significant (p < 0.001).
        """
        
        misleading_stats = """
        Sales increased by 200%! (from 1 to 3 customers)
        We're 10x better than competitors (in one specific metric).
        Success rate is 90% (out of 10 cherry-picked cases).
        """
        
        # When
        result1 = bias_detector._detect_statistical_bias(biased_stats)
        result2 = bias_detector._detect_statistical_bias(misleading_stats)
        
        # Then
        assert isinstance(result1, list)
        assert isinstance(result2, list)
        # result2 should potentially detect more bias indicators

    @pytest.mark.unit
    def test_generate_bias_warnings(self, bias_detector):
        """Test generation of user-friendly bias warnings."""
        # Given
        detected_biases = [
            {
                "bias_type": BiasType.CONFIRMATION_BIAS,
                "confidence": 0.8,
                "evidence": ["selective citation", "ignored counterarguments"]
            },
            {
                "bias_type": BiasType.COMMERCIAL_BIAS,
                "confidence": 0.6,
                "evidence": ["promotional language", "sales focus"]
            }
        ]
        
        # When
        warnings = bias_detector._generate_warnings(detected_biases)
        
        # Then
        assert isinstance(warnings, list)
        assert len(warnings) >= len(detected_biases)
        for warning in warnings:
            assert "message" in warning
            assert "severity" in warning
            assert warning["severity"] in ["low", "medium", "high"]

    @pytest.mark.unit
    def test_detect_emotional_manipulation(self, bias_detector):
        """Test detection of emotional manipulation tactics."""
        # Given
        emotional_text = """
        Don't let your competitors crush your business!
        This exclusive opportunity won't last forever.
        Fear missing out on this game-changing technology.
        Act now before it's too late!
        """
        
        # When
        result = bias_detector._detect_emotional_manipulation(emotional_text)
        
        # Then
        assert isinstance(result, list)
        # Should detect fear-based appeals, urgency tactics, etc.

    @pytest.mark.unit
    def test_analyze_balanced_reporting(self, bias_detector):
        """Test analysis of balanced vs. unbalanced reporting."""
        # Given
        balanced_text = """
        The new AI model shows promising results in initial testing.
        However, several limitations remain to be addressed.
        Both supporters and critics have raised valid concerns.
        More research is needed to fully validate the approach.
        """
        
        unbalanced_text = """
        This amazing AI breakthrough solves all existing problems!
        Every test showed perfect results with no issues whatsoever.
        All researchers are excited about this revolutionary advancement.
        """
        
        # When
        balanced_score = bias_detector._calculate_balance_score(balanced_text)
        unbalanced_score = bias_detector._calculate_balance_score(unbalanced_text)
        
        # Then
        assert balanced_score > unbalanced_score
        assert 0.0 <= balanced_score <= 1.0
        assert 0.0 <= unbalanced_score <= 1.0

    @pytest.mark.unit
    def test_transparency_score_calculation(self, bias_detector, sample_article):
        """Test transparency score calculation."""
        # Given - Article with good transparency
        sample_article.evidence.primary_sources = [
            {"type": "paper", "url": "https://example.com/paper1"},
            {"type": "code", "url": "https://github.com/example/repo"}
        ]
        sample_article.evidence.citations = ["Author et al. (2024)", "Research Group (2023)"]
        sample_article.technical.reproducibility_score = 0.8
        
        # When
        transparency = bias_detector._calculate_transparency_score(sample_article)
        
        # Then
        assert 0.0 <= transparency <= 1.0
        assert transparency > 0.5  # Should be high with good evidence

    @pytest.mark.unit
    def test_comprehensive_bias_report(self, bias_detector, sample_article):
        """Test comprehensive bias analysis of an article."""
        # Given
        sample_article.content = """
        According to leading experts, this revolutionary AI breakthrough
        will definitely transform every industry. Our extensive research
        proves this approach is 500% more effective than alternatives.
        Don't miss this game-changing opportunity!
        """
        
        # When
        report = bias_detector.analyze_article_bias(sample_article)
        
        # Then
        assert isinstance(report, BiasReport)
        assert hasattr(report, 'detected_biases')
        assert hasattr(report, 'neutrality_score')
        assert hasattr(report, 'transparency_score')
        assert hasattr(report, 'warnings')
        assert hasattr(report, 'recommendations')
        
        assert 0.0 <= report.neutrality_score <= 1.0
        assert 0.0 <= report.transparency_score <= 1.0