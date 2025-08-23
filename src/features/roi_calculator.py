"""ROI Calculator - Business-focused feature for investment analysis."""

import re
import math
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

from src.config.settings import Settings
from src.models.article import Article, CaseStudy


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ImplementationComplexity(str, Enum):
    """Implementation complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass
class BusinessScenario:
    """Business scenario for ROI calculation."""
    # Investment costs
    initial_investment: float = 0.0
    implementation_cost: float = 0.0
    training_cost: float = 0.0
    hardware_cost: float = 0.0
    software_licensing_cost: float = 0.0
    
    # Ongoing costs
    maintenance_cost_annual: float = 0.0
    operational_cost_annual: float = 0.0
    staff_cost_annual: float = 0.0
    
    # Benefits
    annual_savings: float = 0.0
    annual_revenue_increase: float = 0.0
    productivity_gain_percentage: float = 0.0
    cost_reduction_percentage: float = 0.0
    
    # Timeline
    implementation_time_months: int = 6
    benefit_realization_delay_months: int = 0
    project_lifecycle_years: int = 5
    
    # Risk factors
    technology_risk: float = 0.2
    market_risk: float = 0.1
    execution_risk: float = 0.3
    
    # Additional metadata
    industry: str = ""
    company_size: str = ""  # small, medium, large, enterprise
    use_case: str = ""


@dataclass 
class ROIAnalysisResult:
    """Complete ROI analysis result."""
    scenarios: List[Dict[str, Any]] = field(default_factory=list)
    best_case: Dict[str, Any] = field(default_factory=dict)
    worst_case: Dict[str, Any] = field(default_factory=dict)
    most_likely: Dict[str, Any] = field(default_factory=dict)
    sensitivity_analysis: Dict[str, Any] = field(default_factory=dict)
    monte_carlo_results: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    key_assumptions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)


class ROICalculator:
    """Advanced ROI calculator with scenario modeling and risk analysis."""
    
    def __init__(self, settings: Settings):
        """Initialize the ROI calculator."""
        self.settings = settings
        
        # Industry benchmarks and cost models
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.cost_models = self._build_cost_models()
        self.benefit_models = self._build_benefit_models()
        
        # Financial parameters
        self.discount_rate = 0.10  # 10% discount rate
        self.inflation_rate = 0.03  # 3% inflation
        self.tax_rate = 0.25  # 25% corporate tax rate
    
    def _load_industry_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Load industry-specific ROI benchmarks."""
        return {
            "software": {
                "average_roi": 156,
                "median_roi": 120,
                "top_quartile": 250,
                "payback_months": 18,
                "success_rate": 0.70
            },
            "finance": {
                "average_roi": 180,
                "median_roi": 150,
                "top_quartile": 300,
                "payback_months": 15,
                "success_rate": 0.65
            },
            "healthcare": {
                "average_roi": 140,
                "median_roi": 110,
                "top_quartile": 200,
                "payback_months": 20,
                "success_rate": 0.60
            },
            "manufacturing": {
                "average_roi": 200,
                "median_roi": 160,
                "top_quartile": 320,
                "payback_months": 16,
                "success_rate": 0.75
            },
            "retail": {
                "average_roi": 130,
                "median_roi": 100,
                "top_quartile": 180,
                "payback_months": 22,
                "success_rate": 0.55
            }
        }
    
    def _build_cost_models(self) -> Dict[str, Any]:
        """Build cost estimation models."""
        return {
            "implementation_costs": {
                "simple": {"min": 50000, "max": 150000, "typical": 100000},
                "moderate": {"min": 150000, "max": 500000, "typical": 300000},
                "complex": {"min": 500000, "max": 1500000, "typical": 1000000},
                "very_complex": {"min": 1500000, "max": 5000000, "typical": 3000000}
            },
            "ongoing_costs_percentage": {
                "maintenance": 0.15,  # 15% of initial investment annually
                "support": 0.10,      # 10% of initial investment annually
                "upgrades": 0.05      # 5% of initial investment annually
            },
            "staff_costs": {
                "ai_engineer": 150000,        # Annual salary
                "data_scientist": 130000,
                "ml_engineer": 140000,
                "project_manager": 120000,
                "business_analyst": 100000
            }
        }
    
    def _build_benefit_models(self) -> Dict[str, Any]:
        """Build benefit estimation models."""
        return {
            "productivity_multipliers": {
                "automation": {"min": 1.2, "max": 3.0, "typical": 2.0},
                "optimization": {"min": 1.1, "max": 1.8, "typical": 1.4},
                "decision_support": {"min": 1.1, "max": 1.5, "typical": 1.3},
                "quality_improvement": {"min": 1.1, "max": 2.0, "typical": 1.5}
            },
            "cost_reduction_areas": {
                "labor_costs": {"min": 0.1, "max": 0.5, "typical": 0.25},
                "operational_costs": {"min": 0.05, "max": 0.3, "typical": 0.15},
                "error_reduction": {"min": 0.02, "max": 0.2, "typical": 0.10},
                "resource_optimization": {"min": 0.05, "max": 0.25, "typical": 0.15}
            }
        }
    
    def analyze_article_roi(self, article: Article) -> ROIAnalysisResult:
        """Analyze ROI potential based on article content and metadata."""
        # Extract financial information from article
        extracted_metrics = self._extract_financial_metrics(article.content)
        
        # Generate scenarios from case studies
        case_study_scenarios = []
        if article.business.case_studies:
            case_study_scenarios = self._generate_scenarios_from_case_studies(
                article.business.case_studies
            )
        
        # Generate base scenarios
        base_scenarios = self._generate_base_scenarios(article, extracted_metrics)
        
        # Combine all scenarios
        all_scenarios = case_study_scenarios + base_scenarios
        
        # Analyze each scenario
        analyzed_scenarios = []
        for scenario in all_scenarios:
            roi_result = self.calculate_roi(scenario)
            analyzed_scenarios.append({
                "scenario": scenario,
                "results": roi_result,
                "confidence": self._calculate_scenario_confidence(scenario, article)
            })
        
        # Perform advanced analysis
        sensitivity = self._perform_sensitivity_analysis(base_scenarios[0] if base_scenarios else BusinessScenario())
        monte_carlo = self._monte_carlo_simulation(extracted_metrics)
        
        # Calculate confidence score
        confidence_score = self._calculate_analysis_confidence(article, extracted_metrics)
        
        # Generate key assumptions
        assumptions = self._generate_key_assumptions(article, extracted_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analyzed_scenarios, article)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(article, analyzed_scenarios)
        
        return ROIAnalysisResult(
            scenarios=analyzed_scenarios,
            best_case=self._find_best_scenario(analyzed_scenarios),
            worst_case=self._find_worst_scenario(analyzed_scenarios),
            most_likely=self._find_most_likely_scenario(analyzed_scenarios),
            sensitivity_analysis=sensitivity,
            monte_carlo_results=monte_carlo,
            confidence_score=confidence_score,
            key_assumptions=assumptions,
            recommendations=recommendations,
            risk_factors=risk_factors
        )
    
    def calculate_roi(self, scenario: BusinessScenario) -> Dict[str, Any]:
        """Calculate comprehensive ROI metrics for a scenario."""
        # Calculate total investment
        total_investment = (
            scenario.initial_investment +
            scenario.implementation_cost +
            scenario.training_cost +
            scenario.hardware_cost +
            scenario.software_licensing_cost
        )
        
        # Calculate annual costs and benefits
        annual_costs = (
            scenario.maintenance_cost_annual +
            scenario.operational_cost_annual +
            scenario.staff_cost_annual
        )
        
        annual_benefits = (
            scenario.annual_savings +
            scenario.annual_revenue_increase
        )
        
        # Calculate net annual benefit
        net_annual_benefit = annual_benefits - annual_costs
        
        # Calculate basic ROI
        if total_investment > 0:
            simple_roi = ((net_annual_benefit * scenario.project_lifecycle_years) - total_investment) / total_investment * 100
        else:
            simple_roi = float('inf') if net_annual_benefit > 0 else 0
        
        # Calculate payback period
        payback_months = self._calculate_payback_period(
            total_investment, net_annual_benefit, scenario.benefit_realization_delay_months
        )
        
        # Calculate NPV
        npv = self._calculate_npv(
            total_investment, net_annual_benefit, scenario.project_lifecycle_years,
            self.discount_rate, scenario.benefit_realization_delay_months
        )
        
        # Calculate IRR
        irr = self._calculate_irr(total_investment, net_annual_benefit, scenario.project_lifecycle_years)
        
        # Generate cash flow projections
        cash_flows = self._generate_cash_flow_projections(scenario)
        
        # Calculate risk-adjusted metrics
        risk_adjusted_roi = self._calculate_risk_adjusted_roi(simple_roi, scenario)
        
        return {
            "roi_percentage": round(simple_roi, 2),
            "risk_adjusted_roi": round(risk_adjusted_roi, 2),
            "payback_period_months": round(payback_months, 1),
            "net_present_value": round(npv, 2),
            "irr": round(irr * 100, 2) if irr else None,
            "total_investment": total_investment,
            "annual_benefits": annual_benefits,
            "annual_costs": annual_costs,
            "net_annual_benefit": net_annual_benefit,
            "cash_flows": cash_flows,
            "break_even_month": self._calculate_break_even_point(cash_flows)
        }
    
    def _extract_financial_metrics(self, content: str) -> Dict[str, Any]:
        """Extract financial metrics from article content."""
        metrics = {}
        content_lower = content.lower()
        
        # Cost patterns
        cost_patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|m)\s*(?:investment|cost|funding)',
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:thousand|k)\s*(?:investment|cost|funding)',
            r'(\d+(?:\.\d+)?)\s*%\s*cost\s*reduction',
            r'(\d+(?:\.\d+)?)\s*%\s*savings',
            r'save\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'reduced?\s*costs?\s*by\s*(\d+(?:\.\d+)?)\s*%',
            r'roi\s*of\s*(\d+(?:\.\d+)?)\s*%',
            r'return\s*on\s*investment\s*.*?(\d+(?:\.\d+)?)\s*%'
        ]
        
        for pattern in cost_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            if matches:
                for match in matches:
                    value = float(match.replace(',', ''))
                    if 'million' in pattern:
                        value *= 1000000
                    elif 'thousand' in pattern:
                        value *= 1000
                    
                    if 'cost' in pattern or 'investment' in pattern:
                        metrics.setdefault('costs', []).append(value)
                    elif 'saving' in pattern or 'save' in pattern:
                        metrics.setdefault('savings', []).append(value)
                    elif 'roi' in pattern or 'return' in pattern:
                        metrics.setdefault('roi_mentioned', []).append(value)
        
        # Time patterns
        time_patterns = [
            r'(\d+)\s*months?\s*(?:implementation|deployment|rollout)',
            r'(\d+)\s*weeks?\s*(?:implementation|deployment|rollout)',
            r'implemented\s*in\s*(\d+)\s*months?',
            r'payback\s*(?:period\s*)?(?:of\s*)?(\d+)\s*months?'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            if matches:
                months = [int(match) for match in matches]
                if 'weeks' in pattern:
                    months = [m // 4 for m in months]  # Convert weeks to months
                
                if 'payback' in pattern:
                    metrics['payback_months'] = months[0]
                else:
                    metrics['implementation_months'] = months[0]
        
        # Percentage improvements
        improvement_patterns = [
            r'(\d+(?:\.\d+)?)\s*%\s*(?:improvement|increase|boost|gain)',
            r'improved?\s*(?:by\s*)?(\d+(?:\.\d+)?)\s*%',
            r'increased?\s*(?:by\s*)?(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:\.\d+)?)\s*%\s*(?:more\s*)?efficient'
        ]
        
        for pattern in improvement_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            if matches:
                metrics.setdefault('improvements', []).extend([float(m) for m in matches])
        
        return metrics
    
    def _generate_scenarios_from_case_studies(self, case_studies: List[CaseStudy]) -> List[BusinessScenario]:
        """Generate business scenarios from case studies."""
        scenarios = []
        
        for case_study in case_studies:
            scenario = BusinessScenario()
            
            # Extract metrics from case study
            results_text = case_study.results.lower()
            timeline_text = case_study.timeline.lower()
            
            # Parse cost reductions
            cost_reduction_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%.*?(?:cost|saving)', results_text)
            if cost_reduction_matches:
                reduction_pct = float(cost_reduction_matches[0]) / 100
                scenario.cost_reduction_percentage = reduction_pct
                # Estimate annual savings based on typical company costs
                typical_annual_cost = self._estimate_company_costs(case_study.company, case_study.industry)
                scenario.annual_savings = typical_annual_cost * reduction_pct
            
            # Parse efficiency improvements
            efficiency_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%.*?(?:efficiency|productivity)', results_text)
            if efficiency_matches:
                scenario.productivity_gain_percentage = float(efficiency_matches[0]) / 100
            
            # Parse timeline
            timeline_matches = re.findall(r'(\d+)\s*months?', timeline_text)
            if timeline_matches:
                scenario.implementation_time_months = int(timeline_matches[0])
            
            # Estimate investment based on company size and industry
            scenario.initial_investment = self._estimate_investment(
                case_study.company, case_study.industry, scenario.implementation_time_months
            )
            
            # Set industry and metadata
            scenario.industry = case_study.industry.lower()
            scenario.use_case = f"Based on {case_study.company} case study"
            
            scenarios.append(scenario)
        
        return scenarios
    
    def _generate_base_scenarios(self, article: Article, metrics: Dict[str, Any]) -> List[BusinessScenario]:
        """Generate base scenarios for ROI analysis."""
        scenarios = []
        
        # Conservative scenario
        conservative = BusinessScenario(
            initial_investment=metrics.get('costs', [200000])[0] if 'costs' in metrics else 200000,
            annual_savings=metrics.get('savings', [50000])[0] * 0.7 if 'savings' in metrics else 50000,
            implementation_time_months=metrics.get('implementation_months', 12),
            technology_risk=0.3,
            market_risk=0.2,
            execution_risk=0.4,
            use_case="Conservative estimate"
        )
        
        # Optimistic scenario
        optimistic = BusinessScenario(
            initial_investment=metrics.get('costs', [150000])[0] * 0.8 if 'costs' in metrics else 150000,
            annual_savings=metrics.get('savings', [80000])[0] * 1.3 if 'savings' in metrics else 80000,
            annual_revenue_increase=50000,
            implementation_time_months=max(6, metrics.get('implementation_months', 8) - 2),
            technology_risk=0.1,
            market_risk=0.1,
            execution_risk=0.2,
            use_case="Optimistic estimate"
        )
        
        # Realistic scenario
        realistic = BusinessScenario(
            initial_investment=metrics.get('costs', [175000])[0] if 'costs' in metrics else 175000,
            annual_savings=metrics.get('savings', [65000])[0] if 'savings' in metrics else 65000,
            annual_revenue_increase=25000,
            implementation_time_months=metrics.get('implementation_months', 10),
            technology_risk=0.2,
            market_risk=0.15,
            execution_risk=0.3,
            use_case="Realistic estimate"
        )
        
        scenarios.extend([conservative, optimistic, realistic])
        return scenarios
    
    def _estimate_company_costs(self, company: str, industry: str) -> float:
        """Estimate typical annual costs for a company."""
        industry_multipliers = {
            "software": 2000000,
            "finance": 5000000,
            "healthcare": 3000000,
            "manufacturing": 4000000,
            "retail": 1500000
        }
        return industry_multipliers.get(industry.lower(), 2500000)
    
    def _estimate_investment(self, company: str, industry: str, months: int) -> float:
        """Estimate investment required based on company and timeline."""
        base_monthly_cost = 50000  # Base monthly project cost
        industry_multipliers = {
            "software": 1.0,
            "finance": 1.5,
            "healthcare": 1.3,
            "manufacturing": 1.4,
            "retail": 0.8
        }
        
        multiplier = industry_multipliers.get(industry.lower(), 1.0)
        return base_monthly_cost * months * multiplier
    
    def _calculate_payback_period(self, investment: float, net_monthly_benefit: float, delay_months: int = 0) -> float:
        """Calculate payback period in months."""
        if net_monthly_benefit <= 0:
            return float('inf')
        
        monthly_benefit = net_monthly_benefit / 12
        payback = investment / monthly_benefit + delay_months
        return max(0, payback)
    
    def _calculate_npv(self, investment: float, annual_benefit: float, years: int, discount_rate: float, delay_months: int = 0) -> float:
        """Calculate Net Present Value."""
        npv = -investment
        delay_years = delay_months / 12
        
        for year in range(1, years + 1):
            discounted_benefit = annual_benefit / ((1 + discount_rate) ** (year + delay_years))
            npv += discounted_benefit
        
        return npv
    
    def _calculate_irr(self, investment: float, annual_benefit: float, years: int) -> Optional[float]:
        """Calculate Internal Rate of Return using Newton-Raphson method."""
        if annual_benefit <= 0:
            return None
        
        # Initial guess
        irr = 0.1
        
        # Newton-Raphson iterations
        for _ in range(100):
            f = -investment + sum(annual_benefit / ((1 + irr) ** year) for year in range(1, years + 1))
            df = -sum(year * annual_benefit / ((1 + irr) ** (year + 1)) for year in range(1, years + 1))
            
            if abs(df) < 1e-10:
                break
            
            irr_new = irr - f / df
            
            if abs(irr_new - irr) < 1e-6:
                return irr_new
            
            irr = irr_new
        
        return irr if 0 <= irr <= 10 else None  # Return None for unrealistic IRR values
    
    def _generate_cash_flow_projections(self, scenario: BusinessScenario) -> List[Dict[str, float]]:
        """Generate detailed cash flow projections."""
        cash_flows = []
        cumulative_cash_flow = -scenario.initial_investment
        
        for year in range(scenario.project_lifecycle_years + 1):
            if year == 0:
                # Initial investment year
                cash_flow = {
                    "year": year,
                    "investment": -scenario.initial_investment,
                    "benefits": 0,
                    "costs": 0,
                    "net_cash_flow": -scenario.initial_investment,
                    "cumulative_cash_flow": cumulative_cash_flow
                }
            else:
                # Account for benefit realization delay
                benefit_factor = 1.0 if year > (scenario.benefit_realization_delay_months / 12) else 0.0
                
                benefits = (scenario.annual_savings + scenario.annual_revenue_increase) * benefit_factor
                costs = (scenario.maintenance_cost_annual + scenario.operational_cost_annual + 
                        scenario.staff_cost_annual)
                
                # Apply inflation
                inflation_factor = (1 + self.inflation_rate) ** year
                benefits *= inflation_factor
                costs *= inflation_factor
                
                net_cash_flow = benefits - costs
                cumulative_cash_flow += net_cash_flow
                
                cash_flow = {
                    "year": year,
                    "investment": 0,
                    "benefits": round(benefits, 2),
                    "costs": round(costs, 2),
                    "net_cash_flow": round(net_cash_flow, 2),
                    "cumulative_cash_flow": round(cumulative_cash_flow, 2)
                }
            
            cash_flows.append(cash_flow)
        
        return cash_flows
    
    def _calculate_break_even_point(self, cash_flows: List[Dict[str, float]]) -> Optional[int]:
        """Calculate break-even point in months."""
        for i, cf in enumerate(cash_flows):
            if cf["cumulative_cash_flow"] >= 0:
                if i == 0:
                    return 0
                
                # Interpolate to find exact month
                prev_cf = cash_flows[i - 1]
                months_into_year = 12 * (-prev_cf["cumulative_cash_flow"] / cf["net_cash_flow"])
                return int((i - 1) * 12 + months_into_year)
        
        return None  # Break-even not achieved within project lifecycle
    
    def _calculate_risk_adjusted_roi(self, base_roi: float, scenario: BusinessScenario) -> float:
        """Calculate risk-adjusted ROI."""
        total_risk = scenario.technology_risk + scenario.market_risk + scenario.execution_risk
        risk_factor = 1 - (total_risk / 3)  # Average risk
        return base_roi * risk_factor
    
    def _perform_sensitivity_analysis(self, base_scenario: BusinessScenario) -> Dict[str, Any]:
        """Perform sensitivity analysis on key variables."""
        variables = {
            "initial_investment": base_scenario.initial_investment,
            "annual_savings": base_scenario.annual_savings,
            "implementation_time": base_scenario.implementation_time_months,
            "maintenance_cost": base_scenario.maintenance_cost_annual
        }
        
        sensitivity_results = {}
        base_roi = self.calculate_roi(base_scenario)["roi_percentage"]
        
        for var_name, base_value in variables.items():
            # Test ±20% variation
            low_scenario = self._create_scenario_variant(base_scenario, var_name, base_value * 0.8)
            high_scenario = self._create_scenario_variant(base_scenario, var_name, base_value * 1.2)
            
            low_roi = self.calculate_roi(low_scenario)["roi_percentage"]
            high_roi = self.calculate_roi(high_scenario)["roi_percentage"]
            
            sensitivity_results[var_name] = {
                "base_value": base_value,
                "base_roi": base_roi,
                "low_value": base_value * 0.8,
                "low_roi": low_roi,
                "high_value": base_value * 1.2,
                "high_roi": high_roi,
                "sensitivity": abs(high_roi - low_roi) / (0.4 * base_roi) if base_roi != 0 else 0
            }
        
        return sensitivity_results
    
    def _create_scenario_variant(self, base_scenario: BusinessScenario, var_name: str, new_value: float) -> BusinessScenario:
        """Create a variant of the scenario with one variable changed."""
        import copy
        scenario = copy.deepcopy(base_scenario)
        
        if var_name == "initial_investment":
            scenario.initial_investment = new_value
        elif var_name == "annual_savings":
            scenario.annual_savings = new_value
        elif var_name == "implementation_time":
            scenario.implementation_time_months = int(new_value)
        elif var_name == "maintenance_cost":
            scenario.maintenance_cost_annual = new_value
        
        return scenario
    
    def _monte_carlo_simulation(self, metrics: Dict[str, Any], num_simulations: int = 1000) -> Dict[str, Any]:
        """Perform Monte Carlo simulation for ROI distribution."""
        roi_results = []
        
        for _ in range(num_simulations):
            # Generate random scenario
            scenario = self._generate_random_scenario(metrics)
            roi_result = self.calculate_roi(scenario)
            roi_results.append(roi_result["roi_percentage"])
        
        # Calculate statistics
        roi_results.sort()
        mean_roi = sum(roi_results) / len(roi_results)
        
        # Calculate standard deviation
        variance = sum((x - mean_roi) ** 2 for x in roi_results) / len(roi_results)
        std_roi = math.sqrt(variance)
        
        # Calculate percentiles
        p10 = roi_results[int(0.1 * len(roi_results))]
        p25 = roi_results[int(0.25 * len(roi_results))]
        p50 = roi_results[int(0.5 * len(roi_results))]
        p75 = roi_results[int(0.75 * len(roi_results))]
        p90 = roi_results[int(0.9 * len(roi_results))]
        
        positive_roi_count = sum(1 for roi in roi_results if roi > 0)
        
        return {
            "mean_roi": round(mean_roi, 2),
            "std_roi": round(std_roi, 2),
            "median_roi": round(p50, 2),
            "min_roi": round(roi_results[0], 2),
            "max_roi": round(roi_results[-1], 2),
            "confidence_intervals": {
                "p10": round(p10, 2),
                "p25": round(p25, 2),
                "p75": round(p75, 2),
                "p90": round(p90, 2)
            },
            "probability_positive_roi": round(positive_roi_count / len(roi_results), 3),
            "roi_distribution": roi_results[::10]  # Sample every 10th result for visualization
        }
    
    def _generate_random_scenario(self, metrics: Dict[str, Any]) -> BusinessScenario:
        """Generate a random scenario for Monte Carlo simulation."""
        # Use normal distribution with metrics as means and reasonable std dev
        base_investment = metrics.get('costs', [250000])[0] if 'costs' in metrics else 250000
        base_savings = metrics.get('savings', [75000])[0] if 'savings' in metrics else 75000
        
        scenario = BusinessScenario(
            initial_investment=max(50000, random.gauss(base_investment, base_investment * 0.3)),
            annual_savings=max(10000, random.gauss(base_savings, base_savings * 0.4)),
            annual_revenue_increase=max(0, random.gauss(30000, 15000)),
            implementation_time_months=max(3, int(random.gauss(9, 3))),
            maintenance_cost_annual=random.gauss(base_investment * 0.15, base_investment * 0.05),
            technology_risk=max(0.05, min(0.5, random.gauss(0.2, 0.1))),
            market_risk=max(0.05, min(0.4, random.gauss(0.15, 0.08))),
            execution_risk=max(0.1, min(0.6, random.gauss(0.3, 0.15)))
        )
        
        return scenario
    
    def _calculate_scenario_confidence(self, scenario: BusinessScenario, article: Article) -> float:
        """Calculate confidence score for a specific scenario."""
        confidence = 1.0
        
        # Reduce confidence for high risk
        total_risk = scenario.technology_risk + scenario.market_risk + scenario.execution_risk
        confidence -= total_risk * 0.2
        
        # Reduce confidence for lack of evidence
        if not article.business.case_studies:
            confidence -= 0.2
        
        if not article.business.roi_indicators:
            confidence -= 0.15
        
        if article.source_tier > 1:
            confidence -= 0.1
        
        return max(0.1, confidence)
    
    def _calculate_analysis_confidence(self, article: Article, metrics: Dict[str, Any]) -> float:
        """Calculate overall confidence in the ROI analysis."""
        confidence = 1.0
        
        # Evidence quality
        if article.business.case_studies and len(article.business.case_studies) >= 2:
            confidence += 0.2
        elif article.business.case_studies:
            confidence += 0.1
        else:
            confidence -= 0.3
        
        if article.business.roi_indicators:
            confidence += 0.15
        
        if article.business.funding_info:
            confidence += 0.1
        
        # Metrics extraction quality
        if 'costs' in metrics and 'savings' in metrics:
            confidence += 0.2
        elif 'costs' in metrics or 'savings' in metrics:
            confidence += 0.1
        else:
            confidence -= 0.2
        
        # Source credibility
        if article.source_tier == 1:
            confidence += 0.1
        elif article.source_tier > 2:
            confidence -= 0.15
        
        return max(0.1, min(1.0, confidence))
    
    def _generate_key_assumptions(self, article: Article, metrics: Dict[str, Any]) -> List[str]:
        """Generate key assumptions underlying the analysis."""
        assumptions = []
        
        assumptions.append("Business environment remains stable during implementation period")
        assumptions.append("Technology performance matches expectations from testing/pilots")
        assumptions.append("Staff adoption and training proceed as planned")
        
        if not metrics.get('costs'):
            assumptions.append("Investment costs estimated based on industry benchmarks")
        
        if not metrics.get('savings'):
            assumptions.append("Benefits estimated from similar case studies and industry data")
        
        if not article.business.case_studies:
            assumptions.append("ROI projections based on theoretical benefits rather than proven results")
        
        if article.technical.reproducibility_score < 0.7:
            assumptions.append("Technical implementation complexity may be higher than anticipated")
        
        assumptions.append("Discount rate reflects current cost of capital and risk profile")
        assumptions.append("Inflation and market conditions remain within historical ranges")
        
        return assumptions
    
    def _generate_recommendations(self, scenarios: List[Dict], article: Article) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        if not scenarios:
            return ["Insufficient data for specific recommendations"]
        
        # Analyze scenario results
        avg_roi = sum(s["results"]["roi_percentage"] for s in scenarios) / len(scenarios)
        min_payback = min(s["results"]["payback_period_months"] for s in scenarios)
        
        if avg_roi > 150:
            recommendations.append("Strong ROI potential - consider accelerating implementation timeline")
        elif avg_roi > 100:
            recommendations.append("Positive ROI expected - proceed with detailed planning and pilot program")
        elif avg_roi > 50:
            recommendations.append("Moderate ROI - focus on risk mitigation and phased implementation")
        else:
            recommendations.append("Low ROI - reassess business case and consider alternative approaches")
        
        if min_payback > 36:
            recommendations.append("Long payback period - explore ways to accelerate benefit realization")
        
        # Risk-based recommendations
        high_risk_scenarios = sum(1 for s in scenarios 
                                 if s["scenario"].technology_risk + s["scenario"].market_risk + s["scenario"].execution_risk > 0.6)
        
        if high_risk_scenarios / len(scenarios) > 0.5:
            recommendations.append("High risk profile - implement robust risk management and contingency planning")
        
        # Implementation recommendations
        if not article.business.case_studies:
            recommendations.append("Limited proven results - start with pilot program to validate assumptions")
        
        if article.technical.implementation_ready:
            recommendations.append("Technology appears mature - focus on organizational change management")
        else:
            recommendations.append("Technology requires development - budget additional time and resources")
        
        recommendations.append("Regular ROI monitoring and adjustment of projections based on actual results")
        
        return recommendations
    
    def _identify_risk_factors(self, article: Article, scenarios: List[Dict]) -> List[str]:
        """Identify key risk factors affecting ROI."""
        risks = []
        
        # Technical risks
        if not article.technical.implementation_ready:
            risks.append("Technology maturity risk - solution may require significant development")
        
        if article.technical.reproducibility_score < 0.5:
            risks.append("Implementation uncertainty - limited reproducibility may increase costs")
        
        if not article.technical.code_available:
            risks.append("Development risk - building from scratch increases time and cost")
        
        # Business risks
        if not article.business.case_studies:
            risks.append("Proof of concept risk - limited evidence of real-world success")
        
        if article.business.implementation_cost in ["high", "enterprise"]:
            risks.append("Cost overrun risk - high complexity implementations often exceed budgets")
        
        # Market risks
        if article.business.market_size and "early stage" in article.content.lower():
            risks.append("Market timing risk - early adoption may face unexpected challenges")
        
        # Scenario-based risks
        if scenarios:
            avg_payback = sum(s["results"]["payback_period_months"] for s in scenarios) / len(scenarios)
            if avg_payback > 24:
                risks.append("Liquidity risk - long payback period may strain cash flow")
        
        # Organizational risks
        risks.append("Change management risk - employee resistance may slow adoption")
        risks.append("Skill gap risk - may need to hire or train specialized personnel")
        
        return risks
    
    def _find_best_scenario(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Find the best case scenario."""
        if not scenarios:
            return {}
        return max(scenarios, key=lambda s: s["results"]["roi_percentage"])
    
    def _find_worst_scenario(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Find the worst case scenario."""
        if not scenarios:
            return {}
        return min(scenarios, key=lambda s: s["results"]["roi_percentage"])
    
    def _find_most_likely_scenario(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Find the most likely scenario based on confidence scores."""
        if not scenarios:
            return {}
        return max(scenarios, key=lambda s: s["confidence"])