"""Bias Detection System for content quality assurance."""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math

from src.config.settings import Settings
from src.models.article import Article


class BiasType(str, Enum):
    """Types of biases that can be detected."""
    CONFIRMATION_BIAS = "confirmation_bias"
    SELECTION_BIAS = "selection_bias"  
    AUTHORITY_BIAS = "authority_bias"
    BANDWAGON_BIAS = "bandwagon_bias"
    TEMPORAL_BIAS = "temporal_bias"
    COMMERCIAL_BIAS = "commercial_bias"
    HYPE_BIAS = "hype_bias"
    CONSENSUS_BIAS = "consensus_bias"
    SURVIVORSHIP_BIAS = "survivorship_bias"
    STATISTICAL_BIAS = "statistical_bias"


@dataclass
class BiasIndicator:
    """Individual bias indicator with evidence."""
    bias_type: BiasType
    confidence: float
    evidence: List[str] = field(default_factory=list)
    explanation: str = ""
    severity: str = "medium"  # low, medium, high
    location: str = ""  # where in text the bias was found


@dataclass 
class BiasReport:
    """Comprehensive bias analysis report."""
    detected_biases: List[BiasIndicator] = field(default_factory=list)
    neutrality_score: float = 0.0
    transparency_score: float = 0.0
    balance_score: float = 0.0
    credibility_score: float = 0.0
    overall_quality_score: float = 0.0
    warnings: List[Dict[str, str]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence_level: float = 0.0


class BiasDetector:
    """Advanced bias detection system for news articles."""
    
    def __init__(self, settings: Settings):
        """Initialize the bias detector."""
        self.settings = settings
        
        # Language patterns for bias detection
        self.bias_patterns = self._build_bias_patterns()
        
        # Statistical patterns
        self.statistical_patterns = self._build_statistical_patterns()
        
        # Emotional manipulation patterns
        self.emotional_patterns = self._build_emotional_patterns()
        
        # Authority and credibility indicators
        self.authority_indicators = self._build_authority_indicators()
        
        # Commercial bias indicators
        self.commercial_indicators = self._build_commercial_indicators()
    
    def _build_bias_patterns(self) -> Dict[BiasType, List[re.Pattern]]:
        """Build regex patterns for different bias types."""
        patterns = {
            BiasType.AUTHORITY_BIAS: [
                re.compile(r'\b(?:clearly|obviously|undoubtedly|certainly|definitely)\b', re.IGNORECASE),
                re.compile(r'\b(?:experts?|authorities|leaders?)\s+(?:all\s+)?(?:agree|say|believe|think)\b', re.IGNORECASE),
                re.compile(r'\b(?:leading|top|renowned|famous)\s+(?:expert|scientist|researcher)\b', re.IGNORECASE),
                re.compile(r'\baccording\s+to\s+(?:the\s+)?(?:genius|mastermind|visionary)\b', re.IGNORECASE),
            ],
            
            BiasType.BANDWAGON_BIAS: [
                re.compile(r'\b(?:everyone|everybody)\s+(?:knows|agrees|says|thinks)\b', re.IGNORECASE),
                re.compile(r'\b(?:most|many)\s+(?:people|experts|companies)\s+(?:believe|think|agree)\b', re.IGNORECASE),
                re.compile(r'\b(?:popular|trending|mainstream)\s+(?:opinion|view|belief)\b', re.IGNORECASE),
                re.compile(r'\bjoin\s+the\s+(?:revolution|movement|trend)\b', re.IGNORECASE),
            ],
            
            BiasType.HYPE_BIAS: [
                re.compile(r'\b(?:revolutionary|groundbreaking|breakthrough|game-?changing)\b', re.IGNORECASE),
                re.compile(r'\b(?:amazing|incredible|unbelievable|unprecedented)\b', re.IGNORECASE),
                re.compile(r'\b(?:will\s+definitely|guaranteed\s+to|certain\s+to)\s+(?:change|transform|revolutionize)\b', re.IGNORECASE),
                re.compile(r'\b(?:next\s+big\s+thing|holy\s+grail|silver\s+bullet)\b', re.IGNORECASE),
            ],
            
            BiasType.TEMPORAL_BIAS: [
                re.compile(r'\b(?:latest|newest|most\s+recent)\s+(?:always|definitely)\b', re.IGNORECASE),
                re.compile(r'\b(?:old|outdated|legacy)\s+(?:methods?|approaches?)\s+are\s+(?:useless|obsolete)\b', re.IGNORECASE),
                re.compile(r'\bcompletely\s+(?:obsoletes?|replaces?|supersedes?)\s+(?:all\s+)?previous\b', re.IGNORECASE),
                re.compile(r'\b(?:cutting[- ]edge|bleeding[- ]edge|state[- ]of[- ]the[- ]art)\s+is\s+always\s+better\b', re.IGNORECASE),
            ],
            
            BiasType.CONSENSUS_BIAS: [
                re.compile(r'\b(?:all|every)\s+(?:expert|scientist|researcher)s?\s+agree\b', re.IGNORECASE),
                re.compile(r'\bthere\s+is\s+(?:complete|total|universal)\s+agreement\b', re.IGNORECASE),
                re.compile(r'\bno\s+one\s+disagrees?\s+(?:that|with)\b', re.IGNORECASE),
                re.compile(r'\bscientific\s+consensus\s+is\s+(?:clear|obvious|settled)\b', re.IGNORECASE),
            ],
            
            BiasType.CONFIRMATION_BIAS: [
                re.compile(r'\b(?:ignore|dismiss|overlook)\s+(?:critics?|criticism|opposing\s+views?)\b', re.IGNORECASE),
                re.compile(r'\bonly\s+(?:studies?|research|evidence)\s+that\s+(?:supports?|confirms?)\b', re.IGNORECASE),
                re.compile(r'\b(?:cherry[- ]pick|selective)\s+(?:evidence|data|studies?)\b', re.IGNORECASE),
                re.compile(r'\bconvenient(?:ly)?\s+(?:ignore|forget|omit)\b', re.IGNORECASE),
            ]
        }
        return patterns
    
    def _build_statistical_patterns(self) -> List[re.Pattern]:
        """Build patterns to detect statistical manipulation."""
        return [
            # Misleading percentages
            re.compile(r'(\d+)%\s+(?:increase|improvement|better)(?:\s+\([^)]*from\s+\d+\s+to\s+\d+\))', re.IGNORECASE),
            
            # Cherry-picked metrics
            re.compile(r'(?:best|top|highest)\s+(?:in\s+)?(?:one|specific|particular)\s+(?:metric|measure|test)', re.IGNORECASE),
            
            # Vague statistics
            re.compile(r'\b(?:up\s+to|as\s+much\s+as|over)\s+\d+%', re.IGNORECASE),
            
            # Correlation vs causation
            re.compile(r'\b(?:because|since|due\s+to)\s+.*(?:correlation|associated\s+with)', re.IGNORECASE),
            
            # Sample size issues
            re.compile(r'(?:study|test|survey)\s+(?:of|with)\s+(?:just|only)?\s*\d+\s+(?:people|subjects|cases)', re.IGNORECASE),
        ]
    
    def _build_emotional_patterns(self) -> List[re.Pattern]:
        """Build patterns for emotional manipulation detection."""
        return [
            # Fear-based appeals
            re.compile(r'\b(?:don\'?t\s+(?:let|allow)|avoid|prevent|stop)\s+.*(?:destroy|ruin|devastate|crush)', re.IGNORECASE),
            re.compile(r'\b(?:crisis|disaster|catastrophe|failure)\s+(?:if\s+you\s+don\'?t|unless\s+you)', re.IGNORECASE),
            
            # Urgency tactics
            re.compile(r'\b(?:act\s+now|limited\s+time|don\'?t\s+wait|hurry|urgent)', re.IGNORECASE),
            re.compile(r'\b(?:before\s+it\'?s\s+too\s+late|last\s+chance|final\s+opportunity)', re.IGNORECASE),
            
            # FOMO (Fear of Missing Out)
            re.compile(r'\b(?:don\'?t\s+(?:miss|lose)\s+out|exclusive|secret|insider)', re.IGNORECASE),
            re.compile(r'\bwhile\s+(?:others?|competitors?)\s+(?:struggle|fail|fall\s+behind)', re.IGNORECASE),
        ]
    
    def _build_authority_indicators(self) -> Dict[str, float]:
        """Build authority figures and their credibility weights."""
        return {
            # High credibility (research/academic)
            "professor": 0.9,
            "researcher": 0.8,
            "scientist": 0.8,
            "phd": 0.8,
            "dr.": 0.8,
            
            # Medium credibility (industry)
            "engineer": 0.7,
            "analyst": 0.7,
            "consultant": 0.6,
            "expert": 0.6,
            
            # Variable credibility (business)
            "ceo": 0.5,
            "founder": 0.5,
            "executive": 0.4,
            
            # Low credibility (potentially biased)
            "influencer": 0.3,
            "blogger": 0.3,
            "spokesperson": 0.2,
        }
    
    def _build_commercial_indicators(self) -> List[re.Pattern]:
        """Build patterns for commercial bias detection."""
        return [
            re.compile(r'\b(?:buy|purchase|order|subscribe|sign\s+up)\s+(?:now|today)', re.IGNORECASE),
            re.compile(r'\b(?:special|exclusive|limited)\s+(?:offer|deal|discount|price)', re.IGNORECASE),
            re.compile(r'\b(?:contact|call|visit)\s+(?:our|us)\s+(?:sales|team)', re.IGNORECASE),
            re.compile(r'\bpricing\s+starts?\s+(?:at|from)\s+\$', re.IGNORECASE),
            re.compile(r'\b(?:free\s+trial|money[- ]back\s+guarantee|risk[- ]free)', re.IGNORECASE),
        ]
    
    def analyze_article_bias(self, article: Article) -> BiasReport:
        """Perform comprehensive bias analysis on an article."""
        full_text = f"{article.title}\n\n{article.content}"
        
        # Detect various types of bias
        detected_biases = self.detect_bias(full_text).detected_biases
        
        # Calculate scores
        neutrality_score = self._calculate_neutrality_score(full_text, detected_biases)
        transparency_score = self._calculate_transparency_score(article)
        balance_score = self._calculate_balance_score(full_text)
        credibility_score = self._analyze_source_credibility(article)
        
        # Calculate overall quality score
        overall_quality = (neutrality_score + transparency_score + balance_score + credibility_score) / 4
        
        # Generate warnings and recommendations
        warnings = self._generate_warnings(detected_biases)
        recommendations = self._generate_recommendations(detected_biases, article)
        
        # Calculate confidence in the analysis
        confidence = self._calculate_analysis_confidence(article, detected_biases)
        
        return BiasReport(
            detected_biases=detected_biases,
            neutrality_score=neutrality_score,
            transparency_score=transparency_score,
            balance_score=balance_score,
            credibility_score=credibility_score,
            overall_quality_score=overall_quality,
            warnings=warnings,
            recommendations=recommendations,
            confidence_level=confidence
        )
    
    def detect_bias(self, text: str) -> BiasReport:
        """Detect biases in given text."""
        detected_biases = []
        
        # Language pattern detection
        for bias_type, patterns in self.bias_patterns.items():
            indicators = self._detect_language_patterns(text, patterns, bias_type)
            detected_biases.extend(indicators)
        
        # Statistical bias detection
        statistical_biases = self._detect_statistical_bias(text)
        detected_biases.extend(statistical_biases)
        
        # Emotional manipulation detection
        emotional_biases = self._detect_emotional_manipulation(text)
        detected_biases.extend(emotional_biases)
        
        # Commercial bias detection
        commercial_biases = self._detect_commercial_bias(text)
        detected_biases.extend(commercial_biases)
        
        # Calculate neutrality score
        neutrality = self._calculate_neutrality_score(text, detected_biases)
        
        return BiasReport(
            detected_biases=detected_biases,
            neutrality_score=neutrality
        )
    
    def _detect_language_patterns(self, text: str, patterns: List[re.Pattern], bias_type: BiasType) -> List[BiasIndicator]:
        """Detect bias using language patterns."""
        indicators = []
        
        for pattern in patterns:
            matches = pattern.finditer(text)
            for match in matches:
                confidence = 0.7  # Base confidence for pattern matches
                
                # Adjust confidence based on context
                context = text[max(0, match.start()-50):match.end()+50]
                if self._is_in_quote(text, match.start()):
                    confidence *= 0.5  # Lower confidence if it's a quote
                
                severity = "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low"
                
                indicator = BiasIndicator(
                    bias_type=bias_type,
                    confidence=confidence,
                    evidence=[match.group(0)],
                    explanation=f"Detected {bias_type.value.replace('_', ' ')} pattern: '{match.group(0)}'",
                    severity=severity,
                    location=f"Position {match.start()}-{match.end()}"
                )
                indicators.append(indicator)
        
        return indicators
    
    def _detect_statistical_bias(self, text: str) -> List[BiasIndicator]:
        """Detect statistical presentation bias."""
        indicators = []
        
        for pattern in self.statistical_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                indicator = BiasIndicator(
                    bias_type=BiasType.STATISTICAL_BIAS,
                    confidence=0.6,
                    evidence=[match.group(0)],
                    explanation="Potentially misleading statistical presentation",
                    severity="medium",
                    location=f"Position {match.start()}-{match.end()}"
                )
                indicators.append(indicator)
        
        # Check for specific statistical issues
        
        # Percentage without context
        percentage_matches = re.finditer(r'(\d+)%\s+(?:increase|improvement|better)', text, re.IGNORECASE)
        for match in percentage_matches:
            # Look for context (baseline numbers)
            context = text[max(0, match.start()-100):match.end()+100]
            if not re.search(r'from\s+\d+', context, re.IGNORECASE):
                indicator = BiasIndicator(
                    bias_type=BiasType.STATISTICAL_BIAS,
                    confidence=0.8,
                    evidence=[match.group(0)],
                    explanation="Percentage improvement without baseline context",
                    severity="high",
                    location=f"Position {match.start()}-{match.end()}"
                )
                indicators.append(indicator)
        
        return indicators
    
    def _detect_emotional_manipulation(self, text: str) -> List[BiasIndicator]:
        """Detect emotional manipulation tactics."""
        indicators = []
        
        for pattern in self.emotional_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                indicator = BiasIndicator(
                    bias_type=BiasType.HYPE_BIAS,  # Categorize as hype bias
                    confidence=0.7,
                    evidence=[match.group(0)],
                    explanation="Emotional manipulation detected",
                    severity="medium",
                    location=f"Position {match.start()}-{match.end()}"
                )
                indicators.append(indicator)
        
        return indicators
    
    def _detect_commercial_bias(self, text: str) -> List[BiasIndicator]:
        """Detect commercial bias indicators."""
        indicators = []
        
        for pattern in self.commercial_indicators:
            matches = pattern.finditer(text)
            for match in matches:
                indicator = BiasIndicator(
                    bias_type=BiasType.COMMERCIAL_BIAS,
                    confidence=0.8,
                    evidence=[match.group(0)],
                    explanation="Commercial/promotional content detected",
                    severity="high",
                    location=f"Position {match.start()}-{match.end()}"
                )
                indicators.append(indicator)
        
        return indicators
    
    def _is_in_quote(self, text: str, position: int) -> bool:
        """Check if position is within a quotation."""
        before_text = text[:position]
        quote_count = before_text.count('"') + before_text.count("'")
        return quote_count % 2 == 1
    
    def _calculate_neutrality_score(self, text: str, biases: List[BiasIndicator]) -> float:
        """Calculate neutrality score (0-1, higher is more neutral)."""
        if not text.strip():
            return 0.5
        
        # Start with base neutrality
        score = 1.0
        
        # Penalize for detected biases
        for bias in biases:
            penalty = bias.confidence * 0.1
            if bias.severity == "high":
                penalty *= 2.0
            elif bias.severity == "low":
                penalty *= 0.5
            
            score -= penalty
        
        # Check for balanced language
        balanced_indicators = [
            "however", "although", "but", "nevertheless", "on the other hand",
            "in contrast", "alternatively", "meanwhile", "conversely"
        ]
        
        balanced_count = sum(1 for indicator in balanced_indicators if indicator in text.lower())
        if balanced_count > 0:
            score += min(0.2, balanced_count * 0.05)
        
        # Check for hedging language (indicates uncertainty/nuance)
        hedging_words = [
            "might", "could", "possibly", "perhaps", "likely", "seems", "appears",
            "suggests", "indicates", "may", "potentially"
        ]
        
        hedging_count = sum(1 for word in hedging_words if word in text.lower())
        if hedging_count > 0:
            score += min(0.1, hedging_count * 0.02)
        
        return max(0.0, min(1.0, score))
    
    def _calculate_transparency_score(self, article: Article) -> float:
        """Calculate transparency score based on article metadata and evidence."""
        score = 0.0
        
        # Source transparency
        if article.source and article.source_tier:
            if article.source_tier == 1:
                score += 0.3
            elif article.source_tier == 2:
                score += 0.2
            else:
                score += 0.1
        
        # Evidence and citations
        if article.evidence.primary_sources:
            score += 0.3
            # Bonus for multiple sources
            if len(article.evidence.primary_sources) > 1:
                score += 0.1
        
        if article.evidence.citations:
            score += 0.2
        
        # Technical metadata transparency
        if article.technical.paper_link:
            score += 0.1
        
        if article.technical.code_available:
            score += 0.1
        
        if article.technical.reproducibility_score > 0.7:
            score += 0.1
        
        # Author/byline information
        if hasattr(article, 'author') and article.author:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_balance_score(self, text: str) -> float:
        """Calculate balance score (presents multiple viewpoints)."""
        if not text.strip():
            return 0.5
        
        score = 0.5  # Start neutral
        
        # Look for balanced presentation indicators
        positive_indicators = [
            "benefits", "advantages", "pros", "strengths", "improvements",
            "success", "effective", "efficient", "breakthrough"
        ]
        
        negative_indicators = [
            "limitations", "drawbacks", "cons", "weaknesses", "challenges",
            "problems", "issues", "concerns", "risks", "failures"
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_indicators if word in text_lower)
        negative_count = sum(1 for word in negative_indicators if word in text_lower)
        
        total_count = positive_count + negative_count
        if total_count > 0:
            # Calculate balance ratio
            balance_ratio = min(positive_count, negative_count) / max(positive_count, negative_count)
            score = 0.3 + (0.7 * balance_ratio)  # Scale between 0.3 and 1.0
        
        # Look for explicit acknowledgment of limitations
        limitation_phrases = [
            "however", "but", "although", "despite", "nevertheless",
            "limitations include", "challenges remain", "further research needed"
        ]
        
        limitation_count = sum(1 for phrase in limitation_phrases if phrase in text_lower)
        if limitation_count > 0:
            score += min(0.2, limitation_count * 0.05)
        
        return min(1.0, score)
    
    def _analyze_source_credibility(self, article: Article) -> float:
        """Analyze source credibility."""
        score = 0.5  # Start with neutral credibility
        
        # Source tier weighting
        if article.source_tier == 1:
            score = 0.9
        elif article.source_tier == 2:
            score = 0.7
        elif article.source_tier == 3:
            score = 0.5
        else:
            score = 0.3
        
        # Adjust based on evidence quality
        if article.evidence.primary_sources:
            for source in article.evidence.primary_sources:
                if hasattr(source, 'credibility_score'):
                    score = (score + source.credibility_score) / 2
        
        # Factor in expert validation
        if hasattr(article.evaluation, 'expert_validation') and article.evaluation.expert_validation:
            score += 0.1
        
        return min(1.0, score)
    
    def _generate_warnings(self, biases: List[BiasIndicator]) -> List[Dict[str, str]]:
        """Generate user-friendly warnings based on detected biases."""
        warnings = []
        
        # Group biases by type
        bias_counts = {}
        for bias in biases:
            bias_counts[bias.bias_type] = bias_counts.get(bias.bias_type, 0) + 1
        
        # Generate warnings for significant bias patterns
        for bias_type, count in bias_counts.items():
            if count >= 3:  # Multiple instances of same bias
                severity = "high"
                message = f"Multiple instances of {bias_type.value.replace('_', ' ')} detected ({count} occurrences)"
            elif count >= 2:
                severity = "medium"
                message = f"Repeated {bias_type.value.replace('_', ' ')} patterns detected"
            else:
                continue  # Don't warn for single instances
            
            warning = {
                "severity": severity,
                "bias_type": bias_type.value,
                "message": message,
                "recommendation": self._get_bias_recommendation(bias_type)
            }
            warnings.append(warning)
        
        # Overall bias load warning
        if len(biases) > 5:
            warnings.append({
                "severity": "high",
                "bias_type": "overall",
                "message": f"High bias load detected ({len(biases)} total indicators)",
                "recommendation": "Review content for objectivity and balance"
            })
        
        return warnings
    
    def _get_bias_recommendation(self, bias_type: BiasType) -> str:
        """Get specific recommendation for bias type."""
        recommendations = {
            BiasType.AUTHORITY_BIAS: "Verify claims independently and consider alternative viewpoints",
            BiasType.BANDWAGON_BIAS: "Look for actual evidence rather than popular opinion",
            BiasType.HYPE_BIAS: "Seek balanced analysis and consider potential limitations",
            BiasType.TEMPORAL_BIAS: "Consider the value of established methods and gradual improvement",
            BiasType.COMMERCIAL_BIAS: "Be aware of promotional content and seek independent analysis",
            BiasType.STATISTICAL_BIAS: "Look for complete statistical context and methodology",
            BiasType.CONFIRMATION_BIAS: "Seek out contradicting evidence and alternative perspectives",
            BiasType.CONSENSUS_BIAS: "Verify the actual state of expert opinion",
        }
        return recommendations.get(bias_type, "Apply critical thinking and seek additional sources")
    
    def _generate_recommendations(self, biases: List[BiasIndicator], article: Article) -> List[str]:
        """Generate actionable recommendations for the reader."""
        recommendations = []
        
        # Bias-specific recommendations
        if any(b.bias_type == BiasType.STATISTICAL_BIAS for b in biases):
            recommendations.append("Verify statistical claims with original sources and look for complete methodology")
        
        if any(b.bias_type == BiasType.COMMERCIAL_BIAS for b in biases):
            recommendations.append("This content may be promotional - seek independent analysis and reviews")
        
        if any(b.bias_type in [BiasType.HYPE_BIAS, BiasType.TEMPORAL_BIAS] for b in biases):
            recommendations.append("Look for balanced analysis that includes limitations and challenges")
        
        # Source-based recommendations
        if article.source_tier > 2:
            recommendations.append("Consider seeking additional sources for verification of claims")
        
        if not article.evidence.primary_sources:
            recommendations.append("Look for primary sources and original research to verify information")
        
        # General recommendations
        if len(biases) > 3:
            recommendations.append("Apply extra scrutiny due to multiple bias indicators")
        
        recommendations.append("Cross-reference with other reputable sources before making decisions")
        
        return recommendations
    
    def _calculate_analysis_confidence(self, article: Article, biases: List[BiasIndicator]) -> float:
        """Calculate confidence in the bias analysis."""
        confidence = 1.0
        
        # Reduce confidence for short content
        content_length = len(article.content) if article.content else 0
        if content_length < 500:
            confidence -= 0.2
        
        # Reduce confidence for very technical content (harder to analyze)
        if article.technical.paper_link and not article.business.case_studies:
            confidence -= 0.1
        
        # High bias load might indicate detection issues
        if len(biases) > 10:
            confidence -= 0.15
        
        # Very low bias detection might also indicate issues
        if len(biases) == 0 and content_length > 1000:
            confidence -= 0.1
        
        return max(0.1, confidence)