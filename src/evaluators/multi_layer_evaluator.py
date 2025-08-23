"""Multi-layer evaluation system for articles."""

import math
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.config.settings import Settings
from src.models.article import Article


class MultiLayerEvaluator:
    """Multi-layer article evaluation system."""
    
    def __init__(self, settings: Settings):
        """Initialize the evaluator with settings."""
        self.settings = settings
        self.engineer_weights = settings.engineer_weights
        self.business_weights = settings.business_weights
    
    async def evaluate(self, article: Article, persona: str) -> Dict[str, Any]:
        """Evaluate article for specific persona."""
        if persona not in ["engineer", "business"]:
            raise ValueError(f"Unknown persona: {persona}")
        
        # Layer 1: Content quality score
        quality_score = self.assess_quality(article)
        
        # Layer 2: Persona-specific relevance score
        relevance_score = self.calculate_relevance(article, persona)
        
        # Layer 3: Temporal value score
        temporal_score = self.calculate_temporal_value(article)
        
        # Layer 4: Trust score (E-E-A-T compliance)
        trust_score = self.calculate_trust_score(article)
        
        # Layer 5: Actionability score
        action_score = self.calculate_actionability(article, persona)
        
        # Calculate weighted total
        scores = [quality_score, relevance_score, temporal_score, trust_score, action_score]
        weights = [0.25, 0.3, 0.15, 0.15, 0.15]  # Default weights
        
        total_score = self.weighted_sum(scores, weights)
        
        # Generate detailed breakdown
        breakdown = self._generate_detailed_breakdown(article, persona, {
            "quality": quality_score,
            "relevance": relevance_score,
            "temporal": temporal_score,
            "trust": trust_score,
            "actionability": action_score
        })
        
        result = {
            "total_score": min(1.0, max(0.0, total_score)),
            "breakdown": breakdown,
            "recommendation": self.generate_recommendation({
                "total_score": total_score,
                "breakdown": breakdown
            }),
            "evaluation_timestamp": datetime.now().isoformat(),
            "persona": persona
        }
        
        return result
    
    def assess_quality(self, article: Article) -> float:
        """Assess content quality based on multiple factors."""
        score = 0.0
        
        # Content length factor
        content_length = len(article.content) if article.content else 0
        if content_length >= self.settings.min_content_length:
            length_score = min(1.0, content_length / 2000)  # Normalize to 2000 chars
            score += 0.3 * length_score
        
        # Source tier factor
        tier_score = 1.0 if article.source_tier == 1 else 0.7
        score += 0.2 * tier_score
        
        # Metadata completeness
        metadata_score = 0.0
        if article.technical.paper_link:
            metadata_score += 0.2
        if article.technical.github_repo:
            metadata_score += 0.2
        if article.business.case_studies:
            metadata_score += 0.2
        if article.entities.companies or article.entities.technologies:
            metadata_score += 0.2
        if article.summaries.key_takeaways:
            metadata_score += 0.2
        
        score += 0.3 * metadata_score
        
        # Title quality (basic heuristics)
        title_score = 0.5
        if article.title:
            title_len = len(article.title)
            if 30 <= title_len <= 100:
                title_score = 1.0
            elif title_len < 30 or title_len > 150:
                title_score = 0.3
        
        score += 0.2 * title_score
        
        return min(1.0, score)
    
    def calculate_relevance(self, article: Article, persona: str) -> float:
        """Calculate persona-specific relevance."""
        if persona == "engineer":
            return self._calculate_engineer_relevance(article)
        elif persona == "business":
            return self._calculate_business_relevance(article)
        else:
            return 0.0
    
    def _calculate_engineer_relevance(self, article: Article) -> float:
        """Calculate relevance for engineers."""
        score = 0.0
        
        # Technical depth indicators
        if article.technical.implementation_ready:
            score += 0.25
        if article.technical.code_available:
            score += 0.2
        if article.technical.paper_link:
            score += 0.2
        if article.technical.reproducibility_score > 0.7:
            score += 0.15
        
        # Technology keywords
        tech_keywords = ["algorithm", "model", "neural", "transformer", "API", "framework", "library"]
        content_lower = article.content.lower() if article.content else ""
        tech_mentions = sum(1 for keyword in tech_keywords if keyword in content_lower)
        score += min(0.2, tech_mentions * 0.05)
        
        return min(1.0, score)
    
    def _calculate_business_relevance(self, article: Article) -> float:
        """Calculate relevance for business users."""
        score = 0.0
        
        # Business indicators
        if article.business.roi_indicators:
            score += 0.25
        if article.business.case_studies:
            score += 0.2
        if article.business.market_size:
            score += 0.15
        if article.business.funding_info:
            score += 0.1
        
        # Business keywords
        biz_keywords = ["revenue", "cost", "ROI", "market", "customer", "adoption", "scale", "enterprise"]
        content_lower = article.content.lower() if article.content else ""
        biz_mentions = sum(1 for keyword in biz_keywords if keyword in content_lower)
        score += min(0.3, biz_mentions * 0.06)
        
        return min(1.0, score)
    
    def calculate_temporal_value(self, article: Article) -> float:
        """Calculate temporal value based on freshness and evergreen potential."""
        now = datetime.now()
        
        # Freshness score (exponential decay)
        if article.published_date:
            hours_old = (now - article.published_date).total_seconds() / 3600
            half_life = self.settings.half_life_hours
            freshness = math.exp(-hours_old * math.log(2) / half_life)
        else:
            freshness = 0.5  # Default for unknown publish date
        
        # Evergreen score (heuristic based on content type)
        evergreen_score = article.evergreen_score if article.evergreen_score > 0 else self._estimate_evergreen_score(article)
        
        # Combine scores
        temporal_score = 0.6 * freshness + 0.4 * evergreen_score
        return min(1.0, temporal_score)
    
    def _estimate_evergreen_score(self, article: Article) -> float:
        """Estimate evergreen potential of article."""
        evergreen_indicators = ["tutorial", "guide", "fundamentals", "principles", "introduction"]
        content_lower = article.content.lower() if article.content else ""
        
        score = 0.3  # Base evergreen score
        for indicator in evergreen_indicators:
            if indicator in content_lower:
                score += 0.2
        
        # Research papers tend to have longer value
        if article.technical.paper_link:
            score += 0.3
        
        return min(1.0, score)
    
    def calculate_trust_score(self, article: Article) -> float:
        """Calculate trust score based on E-E-A-T principles."""
        score = 0.0
        
        # Source authority (tier-based)
        if article.source_tier == 1:
            score += 0.4
        elif article.source_tier == 2:
            score += 0.25
        else:
            score += 0.1
        
        # Evidence and citations
        if article.evidence.primary_sources:
            score += 0.3
        if article.evidence.citations:
            score += 0.2
        
        # Expert validation
        if article.evaluation and hasattr(article.evaluation, 'expert_validation'):
            if article.evaluation.expert_validation:
                score += 0.1
        
        return min(1.0, score)
    
    def calculate_actionability(self, article: Article, persona: str) -> float:
        """Calculate actionability score."""
        score = 0.0
        
        if persona == "engineer":
            # Code availability
            if article.technical.code_available:
                score += 0.3
            if article.technical.implementation_ready:
                score += 0.25
            # Clear next steps
            if article.summaries.action_items:
                score += 0.25
            # Reproducible
            if article.technical.reproducibility_score > 0.6:
                score += 0.2
        
        elif persona == "business":
            # Clear ROI indicators
            if article.business.roi_indicators:
                score += 0.3
            # Implementation guidance
            if article.business.case_studies:
                score += 0.25
            # Action items
            if article.summaries.action_items:
                score += 0.25
            # Clear value proposition
            if article.business.competitive_advantage:
                score += 0.2
        
        return min(1.0, score)
    
    def _generate_detailed_breakdown(self, article: Article, persona: str, base_scores: Dict[str, float]) -> Dict[str, float]:
        """Generate detailed breakdown based on persona."""
        if persona == "engineer":
            return {
                "technical_depth": base_scores["quality"] * 0.8 + (0.3 if article.technical.paper_link else 0.0),
                "implementation": 0.4 * base_scores["actionability"] + (0.3 if article.technical.code_available else 0.0),
                "novelty": base_scores["temporal"] * 0.6 + (0.2 if "breakthrough" in article.title.lower() else 0.0),
                "reproducibility": article.technical.reproducibility_score if article.technical.reproducibility_score > 0 else 0.5,
                "community_impact": base_scores["trust"] * 0.7
            }
        else:  # business
            return {
                "business_impact": base_scores["relevance"] * 0.8 + (0.2 if article.business.case_studies else 0.0),
                "roi_potential": 0.5 if article.business.roi_indicators else 0.3,
                "market_validation": 0.4 if article.business.funding_info else 0.2,
                "implementation_ease": 1.0 - (0.3 if article.business.implementation_cost == "high" else 0.1),
                "strategic_value": base_scores["trust"] * 0.6 + base_scores["temporal"] * 0.4
            }
    
    def weighted_sum(self, scores: List[float], weights: List[float]) -> float:
        """Calculate weighted sum of scores."""
        if len(scores) != len(weights):
            raise ValueError("Scores and weights must have same length")
        
        return sum(score * weight for score, weight in zip(scores, weights))
    
    def generate_recommendation(self, evaluation_result: Dict[str, Any]) -> str:
        """Generate recommendation based on total score."""
        total_score = evaluation_result["total_score"]
        
        if total_score >= 0.8:
            return "highly_recommended"
        elif total_score >= 0.6:
            return "recommended"
        elif total_score >= 0.4:
            return "consider"
        else:
            return "skip"