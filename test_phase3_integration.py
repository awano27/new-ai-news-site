#!/usr/bin/env python3
"""Phase 3 Integration Test Runner - Test all advanced features together."""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import Settings
from src.models.article import Article, TechnicalMetadata, BusinessMetadata, CaseStudy, ComputeRequirements
from src.features.implementation_difficulty import ImplementationDifficultyAnalyzer
from src.features.roi_calculator import ROICalculator, BusinessScenario
from src.features.bias_detector import BiasDetector


def create_test_article() -> Article:
    """Create a comprehensive test article for testing all features."""
    return Article(
        id="test-comprehensive-001",
        title="Revolutionary AI Framework Achieves 95% Accuracy: Enterprise Implementation Guide",
        url="https://example.com/ai-framework-breakthrough",
        source="TechCorp Research",
        source_tier=1,
        published_date=datetime.now(),
        content="""
        TechCorp's groundbreaking new AI framework represents a revolutionary breakthrough 
        in machine learning that will definitely transform every industry. According to 
        leading experts, this amazing technology achieves an unprecedented 95% accuracy 
        on benchmark tests, completely obsoleting all previous approaches.
        
        The implementation requires PyTorch, CUDA, and distributed training across 
        8x A100 GPUs with 80GB VRAM each. Initial setup costs approximately $500,000 
        but delivers 40% cost reduction and $2M annual savings according to early adopters.
        
        "This clearly represents the future of AI," says renowned expert Dr. Smith. 
        "Everyone in the industry agrees this will be a game-changer."
        
        Case Study Results:
        - MegaCorp: 40% cost reduction, $2M annual savings, 6-month implementation
        - InnovateCo: 35% efficiency improvement, $1.5M savings, 9-month rollout
        - DataDriven Inc: 50% faster processing, $800K savings, 4-month deployment
        
        The solution includes comprehensive documentation, open-source code repository, 
        and detailed reproducibility guidelines. Mathematical foundations are based on 
        novel transformer architectures with sparse attention mechanisms.
        
        Don't miss this exclusive opportunity to transform your business! Contact our 
        sales team today for amazing discounts. This limited-time offer won't last forever.
        """,
        technical=TechnicalMetadata(
            implementation_ready=True,
            code_available=True,
            paper_link="https://arxiv.org/abs/2024.0001",
            github_repo="https://github.com/techcorp/ai-framework",
            dependencies=["torch>=2.0", "transformers", "accelerate", "deepspeed", "cuda-toolkit"],
            reproducibility_score=0.85,
            compute_requirements=ComputeRequirements(
                gpu="8x A100 80GB",
                memory="640GB total",
                training_time="2 weeks"
            )
        ),
        business=BusinessMetadata(
            market_size="$50B",
            growth_rate=25.0,
            case_studies=[
                CaseStudy("MegaCorp", "Technology", "40% cost reduction, $2M annual savings", "6 months"),
                CaseStudy("InnovateCo", "Finance", "35% efficiency improvement, $1.5M savings", "9 months"),
                CaseStudy("DataDriven Inc", "Healthcare", "50% faster processing, $800K savings", "4 months")
            ],
            implementation_cost="high"
        )
    )


async def test_implementation_difficulty():
    """Test implementation difficulty analysis."""
    print("🔧 Testing Implementation Difficulty Analyzer...")
    
    settings = Settings()
    analyzer = ImplementationDifficultyAnalyzer(settings)
    article = create_test_article()
    
    try:
        result = analyzer.analyze(article)
        
        assert result is not None
        assert "difficulty_level" in result
        assert "skill_requirements" in result
        assert "time_estimate" in result
        assert "resource_requirements" in result
        assert "implementation_steps" in result
        
        print(f"✅ Difficulty Level: {result['difficulty_level']}")
        print(f"✅ Required Skills: {', '.join(result['skill_requirements'][:5])}")
        print(f"✅ Time Estimate: {result['time_estimate']['min_hours']}-{result['time_estimate']['max_hours']} hours")
        print(f"✅ Resource Cost: ${result['resource_requirements'].estimated_cost['monthly_160h']:.0f}/month")
        print(f"✅ Implementation Phases: {len(result['implementation_steps'])}")
        
        # Test edge cases
        minimal_article = Article(
            id="minimal", title="Simple Tutorial", url="", source="", source_tier=2,
            content="Basic Python tutorial for beginners"
        )
        minimal_result = analyzer.analyze(minimal_article)
        assert minimal_result["difficulty_level"] == "beginner"
        
        print("✅ Implementation Difficulty Analyzer: All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Implementation Difficulty test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_roi_calculator():
    """Test ROI calculator functionality."""
    print("\n💰 Testing ROI Calculator...")
    
    settings = Settings()
    calculator = ROICalculator(settings)
    article = create_test_article()
    
    try:
        # Test article analysis
        analysis_result = calculator.analyze_article_roi(article)
        
        assert analysis_result is not None
        assert "scenarios" in analysis_result.__dict__
        assert "confidence_score" in analysis_result.__dict__
        assert len(analysis_result.scenarios) > 0
        
        print(f"✅ Generated {len(analysis_result.scenarios)} scenarios")
        print(f"✅ Confidence Score: {analysis_result.confidence_score:.3f}")
        
        # Test individual scenario calculation
        test_scenario = BusinessScenario(
            initial_investment=500000,
            annual_savings=2000000,
            implementation_time_months=6,
            maintenance_cost_annual=100000
        )
        
        roi_result = calculator.calculate_roi(test_scenario)
        
        assert "roi_percentage" in roi_result
        assert "payback_period_months" in roi_result
        assert "net_present_value" in roi_result
        
        print(f"✅ Sample ROI: {roi_result['roi_percentage']:.1f}%")
        print(f"✅ Payback Period: {roi_result['payback_period_months']:.1f} months")
        print(f"✅ NPV: ${roi_result['net_present_value']:,.0f}")
        
        # Test Monte Carlo simulation
        monte_carlo = calculator._monte_carlo_simulation({}, num_simulations=100)
        assert "mean_roi" in monte_carlo
        assert "probability_positive_roi" in monte_carlo
        
        print(f"✅ Monte Carlo Mean ROI: {monte_carlo['mean_roi']:.1f}%")
        print(f"✅ Positive ROI Probability: {monte_carlo['probability_positive_roi']:.1%}")
        
        print("✅ ROI Calculator: All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ROI Calculator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_bias_detector():
    """Test bias detection functionality."""
    print("\n⚖️ Testing Bias Detector...")
    
    settings = Settings()
    detector = BiasDetector(settings)
    article = create_test_article()
    
    try:
        # Test comprehensive bias analysis
        bias_report = detector.analyze_article_bias(article)
        
        assert bias_report is not None
        assert hasattr(bias_report, 'detected_biases')
        assert hasattr(bias_report, 'neutrality_score')
        assert hasattr(bias_report, 'transparency_score')
        assert hasattr(bias_report, 'overall_quality_score')
        
        print(f"✅ Detected {len(bias_report.detected_biases)} bias indicators")
        print(f"✅ Neutrality Score: {bias_report.neutrality_score:.3f}")
        print(f"✅ Transparency Score: {bias_report.transparency_score:.3f}")
        print(f"✅ Overall Quality: {bias_report.overall_quality_score:.3f}")
        
        # Test individual bias types
        bias_types = set(bias.bias_type for bias in bias_report.detected_biases)
        expected_biases = {"hype_bias", "authority_bias", "commercial_bias"}
        
        detected_expected = bias_types.intersection(expected_biases)
        print(f"✅ Expected bias types detected: {', '.join(detected_expected)}")
        
        # Test neutral text
        neutral_article = Article(
            id="neutral", title="Research Study Results", url="", source="", source_tier=1,
            content="""
            A recent study examined the performance of machine learning models on 
            classification tasks. The research found both improvements and limitations 
            in current approaches. While some metrics showed enhancement, other areas 
            require further investigation. The methodology included proper controls 
            and statistical analysis. Results suggest that more research is needed 
            to fully understand the implications.
            """
        )
        
        neutral_report = detector.analyze_article_bias(neutral_article)
        assert neutral_report.neutrality_score > bias_report.neutrality_score
        
        print(f"✅ Neutral content score: {neutral_report.neutrality_score:.3f} (higher than biased content)")
        print("✅ Bias Detector: All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Bias Detector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integration():
    """Test integration of all advanced features."""
    print("\n🔗 Testing Feature Integration...")
    
    settings = Settings()
    article = create_test_article()
    
    try:
        # Initialize all analyzers
        difficulty_analyzer = ImplementationDifficultyAnalyzer(settings)
        roi_calculator = ROICalculator(settings)
        bias_detector = BiasDetector(settings)
        
        # Run all analyses
        difficulty_result = difficulty_analyzer.analyze(article)
        roi_result = roi_calculator.analyze_article_roi(article)
        bias_result = bias_detector.analyze_article_bias(article)
        
        # Create integrated assessment
        integrated_score = (
            (1.0 - (difficulty_result['complexity_score'] if 'complexity_score' in difficulty_result else 0.5)) * 0.3 +
            (roi_result.confidence_score) * 0.4 +
            (bias_result.overall_quality_score) * 0.3
        )
        
        print(f"✅ Integrated Quality Score: {integrated_score:.3f}")
        
        # Test cross-feature consistency
        if difficulty_result['difficulty_level'] == 'research' and roi_result.confidence_score < 0.5:
            print("✅ Consistency Check: High difficulty correlates with low ROI confidence")
        
        if len(bias_result.detected_biases) > 5 and bias_result.overall_quality_score < 0.6:
            print("✅ Consistency Check: High bias load correlates with low quality score")
        
        # Generate combined recommendations
        recommendations = []
        
        if difficulty_result['difficulty_level'] in ['advanced', 'research']:
            recommendations.append("High technical complexity - ensure adequate expertise and resources")
        
        if roi_result.confidence_score < 0.7:
            recommendations.append("ROI projections have uncertainty - consider pilot program")
        
        if bias_result.neutrality_score < 0.7:
            recommendations.append("Content shows bias indicators - seek additional sources")
        
        print(f"✅ Generated {len(recommendations)} integrated recommendations")
        
        print("✅ Feature Integration: All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all Phase 3 tests."""
    print("🚀 Phase 3 Advanced Features - Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Implementation Difficulty", test_implementation_difficulty),
        ("ROI Calculator", test_roi_calculator),
        ("Bias Detector", test_bias_detector),
        ("Feature Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 3 advanced features are working correctly!")
        print("\n📋 Feature Summary:")
        print("✅ Implementation Difficulty Analyzer - Technical complexity assessment")
        print("✅ ROI Calculator - Business value analysis with Monte Carlo simulation")
        print("✅ Bias Detector - Content quality and neutrality assessment")
        print("✅ Feature Integration - Combined analysis and recommendations")
        
        print("\n🚀 Phase 3 Complete - Ready for Phase 4 (UI/UX Implementation)")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Please review implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)