"""Unit tests for ROI Calculator."""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from src.features.roi_calculator import ROICalculator, BusinessScenario
from src.models.article import Article, BusinessMetadata, CaseStudy, FundingInfo


class TestROICalculator:
    """Test cases for ROI Calculator."""

    @pytest.fixture
    def roi_calculator(self, settings):
        """Create ROI calculator instance."""
        return ROICalculator(settings)

    @pytest.mark.unit
    def test_calculate_basic_roi(self, roi_calculator):
        """Test basic ROI calculation."""
        # Given
        scenario = BusinessScenario(
            initial_investment=100000,
            annual_savings=30000,
            annual_revenue_increase=50000,
            implementation_time_months=6,
            maintenance_cost_annual=10000
        )
        
        # When
        result = roi_calculator.calculate_roi(scenario)
        
        # Then
        assert result is not None
        assert "roi_percentage" in result
        assert "payback_period_months" in result
        assert "net_present_value" in result
        assert "irr" in result
        assert "cash_flows" in result
        
        assert result["roi_percentage"] > 0
        assert result["payback_period_months"] > 0

    @pytest.mark.unit
    def test_analyze_article_for_roi(self, roi_calculator, sample_article):
        """Test ROI analysis of article with business metadata."""
        # Given
        sample_article.business = BusinessMetadata(
            market_size="$50B",
            growth_rate=25.0,
            case_studies=[
                CaseStudy(
                    company="TechCorp",
                    industry="Software",
                    results="Reduced costs by 40%, increased efficiency by 60%",
                    timeline="6 months"
                )
            ],
            implementation_cost="medium"
        )
        sample_article.content = """
        Implementation of AI chatbot resulted in 40% cost reduction 
        and 60% efficiency improvement. Initial investment was $200K.
        """
        
        # When
        result = roi_calculator.analyze_article_roi(sample_article)
        
        # Then
        assert result is not None
        assert "scenarios" in result
        assert "confidence_score" in result
        assert "key_assumptions" in result
        assert len(result["scenarios"]) >= 1

    @pytest.mark.unit
    def test_sensitivity_analysis(self, roi_calculator):
        """Test ROI sensitivity analysis."""
        # Given
        base_scenario = BusinessScenario(
            initial_investment=100000,
            annual_savings=30000,
            annual_revenue_increase=20000,
            implementation_time_months=6
        )
        variables = ["initial_investment", "annual_savings"]
        variation_range = 0.2  # ±20%
        
        # When
        sensitivity = roi_calculator.perform_sensitivity_analysis(
            base_scenario, variables, variation_range
        )
        
        # Then
        assert isinstance(sensitivity, dict)
        for variable in variables:
            assert variable in sensitivity
            assert "low" in sensitivity[variable]
            assert "high" in sensitivity[variable]

    @pytest.mark.unit
    def test_monte_carlo_simulation(self, roi_calculator):
        """Test Monte Carlo ROI simulation."""
        # Given
        scenario_ranges = {
            "initial_investment": (80000, 120000),
            "annual_savings": (20000, 40000),
            "annual_revenue_increase": (15000, 35000)
        }
        num_simulations = 1000
        
        # When
        simulation = roi_calculator.monte_carlo_simulation(
            scenario_ranges, num_simulations
        )
        
        # Then
        assert "mean_roi" in simulation
        assert "std_roi" in simulation
        assert "confidence_intervals" in simulation
        assert "probability_positive_roi" in simulation
        assert len(simulation["roi_distribution"]) == num_simulations

    @pytest.mark.unit
    def test_extract_financial_metrics_from_text(self, roi_calculator):
        """Test extraction of financial metrics from article content."""
        # Given
        text = """
        The implementation cost was $150,000 initially. 
        After deployment, we saw 35% cost reduction and 
        $500,000 annual savings. ROI was achieved in 18 months.
        """
        
        # When
        metrics = roi_calculator._extract_financial_metrics(text)
        
        # Then
        assert isinstance(metrics, dict)
        if "initial_cost" in metrics:
            assert metrics["initial_cost"] > 0
        if "savings" in metrics:
            assert metrics["savings"] > 0

    @pytest.mark.unit
    def test_industry_benchmark_comparison(self, roi_calculator):
        """Test comparison with industry benchmarks."""
        # Given
        calculated_roi = 150  # 150% ROI
        industry = "software"
        
        # When
        comparison = roi_calculator._compare_with_industry_benchmarks(
            calculated_roi, industry
        )
        
        # Then
        assert "industry_average" in comparison
        assert "percentile_rank" in comparison
        assert "performance_category" in comparison
        assert comparison["performance_category"] in ["below_average", "average", "above_average", "exceptional"]

    @pytest.mark.unit
    def test_risk_adjusted_roi(self, roi_calculator):
        """Test risk-adjusted ROI calculation."""
        # Given
        base_scenario = BusinessScenario(
            initial_investment=100000,
            annual_savings=40000,
            annual_revenue_increase=20000,
            implementation_time_months=12
        )
        risk_factors = {
            "technology_risk": 0.3,
            "market_risk": 0.2,
            "execution_risk": 0.4
        }
        
        # When
        risk_adjusted = roi_calculator.calculate_risk_adjusted_roi(
            base_scenario, risk_factors
        )
        
        # Then
        assert "base_roi" in risk_adjusted
        assert "risk_adjusted_roi" in risk_adjusted
        assert "risk_premium" in risk_adjusted
        assert risk_adjusted["risk_adjusted_roi"] <= risk_adjusted["base_roi"]

    @pytest.mark.unit
    def test_generate_implementation_roadmap(self, roi_calculator):
        """Test generation of implementation roadmap with financial milestones."""
        # Given
        scenario = BusinessScenario(
            initial_investment=200000,
            annual_savings=60000,
            implementation_time_months=9
        )
        
        # When
        roadmap = roi_calculator._generate_implementation_roadmap(scenario)
        
        # Then
        assert isinstance(roadmap, list)
        assert len(roadmap) >= 3  # Planning, Implementation, Optimization phases
        
        for milestone in roadmap:
            assert "phase" in milestone
            assert "duration_months" in milestone
            assert "investment_required" in milestone
            assert "expected_benefits" in milestone

    @pytest.mark.unit
    def test_calculate_total_cost_of_ownership(self, roi_calculator):
        """Test TCO calculation over multiple years."""
        # Given
        scenario = BusinessScenario(
            initial_investment=150000,
            annual_savings=50000,
            maintenance_cost_annual=20000,
            training_cost=30000,
            hardware_refresh_cost=50000  # Every 3 years
        )
        years = 5
        
        # When
        tco = roi_calculator._calculate_tco(scenario, years)
        
        # Then
        assert "total_cost" in tco
        assert "annual_costs" in tco
        assert "cost_breakdown" in tco
        assert len(tco["annual_costs"]) == years

    @pytest.mark.unit
    def test_confidence_score_calculation(self, roi_calculator, sample_article):
        """Test confidence score for ROI estimates."""
        # Given - Article with varying amounts of financial data
        high_confidence_article = sample_article
        high_confidence_article.business.case_studies = [
            CaseStudy("TechCorp", "Software", "40% cost reduction, $2M savings", "12 months"),
            CaseStudy("InnovateCo", "Manufacturing", "35% efficiency gain", "8 months")
        ]
        high_confidence_article.content = "Detailed cost analysis shows $500K investment yields $150K annual savings"
        
        low_confidence_article = Article(
            id="low", title="AI Might Help", url="", source="", source_tier=2,
            content="AI could potentially improve business operations",
            business=BusinessMetadata()
        )
        
        # When
        high_conf_result = roi_calculator.analyze_article_roi(high_confidence_article)
        low_conf_result = roi_calculator.analyze_article_roi(low_confidence_article)
        
        # Then
        assert high_conf_result["confidence_score"] > low_conf_result["confidence_score"]
        assert 0.0 <= high_conf_result["confidence_score"] <= 1.0
        assert 0.0 <= low_conf_result["confidence_score"] <= 1.0

    @pytest.mark.unit
    def test_scenario_generation_from_case_studies(self, roi_calculator):
        """Test automatic scenario generation from case studies."""
        # Given
        case_studies = [
            CaseStudy(
                company="Alpha Corp",
                industry="Finance",
                results="Reduced processing time by 50%, saved $1M annually",
                timeline="6 months implementation"
            ),
            CaseStudy(
                company="Beta Inc",
                industry="Healthcare", 
                results="30% efficiency improvement, $500K cost savings",
                timeline="9 months"
            )
        ]
        
        # When
        scenarios = roi_calculator._generate_scenarios_from_case_studies(case_studies)
        
        # Then
        assert isinstance(scenarios, list)
        assert len(scenarios) >= len(case_studies)
        
        for scenario in scenarios:
            assert isinstance(scenario, BusinessScenario)
            assert scenario.initial_investment > 0
            assert scenario.annual_savings > 0

    @pytest.mark.unit
    def test_handle_edge_cases(self, roi_calculator):
        """Test handling of edge cases in ROI calculation."""
        # Test case 1: Zero investment
        zero_investment = BusinessScenario(
            initial_investment=0,
            annual_savings=10000,
            annual_revenue_increase=5000
        )
        
        result1 = roi_calculator.calculate_roi(zero_investment)
        assert result1["roi_percentage"] > 0  # Should handle gracefully
        
        # Test case 2: Negative savings (costs exceed benefits)
        negative_scenario = BusinessScenario(
            initial_investment=100000,
            annual_savings=-20000,  # Actually costs money
            annual_revenue_increase=10000
        )
        
        result2 = roi_calculator.calculate_roi(negative_scenario)
        assert result2["roi_percentage"] < 0  # Should show negative ROI