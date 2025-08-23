"""Implementation Difficulty Analyzer - Engineer-focused feature."""

import re
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.config.settings import Settings
from src.models.article import Article, DifficultyLevel


class SkillLevel(str, Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class ImplementationPhase:
    """Implementation phase with time estimates."""
    phase: str
    description: str
    estimated_hours: int
    required_skills: List[str]
    deliverables: List[str]
    risk_factors: List[str]


@dataclass
class ResourceRequirement:
    """Resource requirements for implementation."""
    compute: Dict[str, Any]
    storage: Dict[str, str]
    network: Dict[str, str]
    estimated_cost: Dict[str, float]
    alternatives: List[str]


class ImplementationDifficultyAnalyzer:
    """Analyzes technical implementation difficulty and provides detailed guidance."""
    
    def __init__(self, settings: Settings):
        """Initialize the analyzer."""
        self.settings = settings
        
        # Skill taxonomy
        self.skill_taxonomy = self._build_skill_taxonomy()
        
        # Complexity indicators
        self.complexity_patterns = self._build_complexity_patterns()
        
        # Cost estimation models
        self.cost_models = self._build_cost_models()
    
    def _build_skill_taxonomy(self) -> Dict[str, Dict]:
        """Build comprehensive skill taxonomy for AI/ML implementation."""
        return {
            # Programming languages
            "python": {"category": "programming", "level": "intermediate", "alternatives": ["R", "Julia"]},
            "javascript": {"category": "programming", "level": "beginner", "alternatives": ["TypeScript", "Python"]},
            "rust": {"category": "programming", "level": "advanced", "alternatives": ["C++", "Go"]},
            "cuda": {"category": "programming", "level": "expert", "alternatives": ["OpenCL", "ROCm"]},
            
            # Frameworks
            "pytorch": {"category": "framework", "level": "intermediate", "alternatives": ["TensorFlow", "JAX"]},
            "tensorflow": {"category": "framework", "level": "intermediate", "alternatives": ["PyTorch", "Keras"]},
            "transformers": {"category": "library", "level": "intermediate", "alternatives": ["Custom implementation"]},
            "sklearn": {"category": "library", "level": "beginner", "alternatives": ["Custom ML", "XGBoost"]},
            
            # Infrastructure
            "docker": {"category": "devops", "level": "intermediate", "alternatives": ["Kubernetes", "Bare metal"]},
            "kubernetes": {"category": "devops", "level": "advanced", "alternatives": ["Docker Swarm", "Nomad"]},
            "aws": {"category": "cloud", "level": "intermediate", "alternatives": ["GCP", "Azure"]},
            "distributed": {"category": "architecture", "level": "advanced", "alternatives": ["Single node"]},
            
            # Mathematics/Theory
            "linear_algebra": {"category": "math", "level": "intermediate", "alternatives": []},
            "statistics": {"category": "math", "level": "intermediate", "alternatives": []},
            "optimization": {"category": "math", "level": "advanced", "alternatives": []},
            "information_theory": {"category": "math", "level": "expert", "alternatives": []},
            
            # Domain expertise
            "computer_vision": {"category": "domain", "level": "intermediate", "alternatives": []},
            "nlp": {"category": "domain", "level": "intermediate", "alternatives": []},
            "reinforcement_learning": {"category": "domain", "level": "advanced", "alternatives": []},
            "mlops": {"category": "domain", "level": "advanced", "alternatives": []},
        }
    
    def _build_complexity_patterns(self) -> Dict[str, re.Pattern]:
        """Build patterns to detect complexity indicators."""
        return {
            "novel_architecture": re.compile(r"\b(novel|new|custom|proposed) (architecture|model|approach)\b", re.IGNORECASE),
            "distributed_training": re.compile(r"\b(distributed|parallel|multi-node|cluster) (training|computation)\b", re.IGNORECASE),
            "large_scale": re.compile(r"\b(\d+[BMK]|billion|million) (parameters?|samples?|tokens?)\b", re.IGNORECASE),
            "optimization_required": re.compile(r"\b(optimization|tuning|hyperparameter|grid search)\b", re.IGNORECASE),
            "custom_implementation": re.compile(r"\b(custom|from scratch|implement|build) (layer|model|algorithm)\b", re.IGNORECASE),
            "research_level": re.compile(r"\b(research|experimental|bleeding edge|cutting edge)\b", re.IGNORECASE),
            "mathematical_heavy": re.compile(r"\b(gradient|jacobian|hessian|eigenvalue|convex|optimization)\b", re.IGNORECASE),
        }
    
    def _build_cost_models(self) -> Dict[str, Any]:
        """Build cost estimation models for different resources."""
        return {
            "compute_hourly_rates": {
                "cpu_only": 0.05,
                "rtx_4090": 0.5,
                "v100": 2.0,
                "a100": 4.0,
                "h100": 8.0,
                "8x_a100": 25.0,
                "tpu_v4": 3.0
            },
            "storage_monthly_rates": {
                "ssd_gb": 0.10,
                "hdd_gb": 0.04,
                "object_storage_gb": 0.023
            },
            "network_costs": {
                "ingress_free": True,
                "egress_gb": 0.09,
                "inter_region_gb": 0.02
            }
        }
    
    def analyze(self, article: Article) -> Dict[str, Any]:
        """Perform comprehensive difficulty analysis."""
        # Calculate complexity score
        complexity_factors = self._extract_complexity_factors(article)
        complexity_score = self._calculate_complexity_score(complexity_factors)
        
        # Determine difficulty level
        difficulty_level = self._determine_difficulty_level(complexity_score, complexity_factors)
        
        # Identify required skills
        required_skills = self._identify_skill_requirements(article)
        
        # Estimate implementation time
        time_estimate = self._estimate_time_requirements(difficulty_level, complexity_factors)
        
        # Assess resource requirements
        resource_requirements = self._assess_resource_requirements(article)
        
        # Generate implementation roadmap
        roadmap = self._generate_implementation_roadmap({
            "difficulty_level": difficulty_level,
            "skill_requirements": required_skills,
            "time_estimate": time_estimate,
            "complexity_factors": complexity_factors
        })
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(article, complexity_factors)
        
        return {
            "difficulty_level": difficulty_level,
            "complexity_score": complexity_score,
            "skill_requirements": required_skills,
            "time_estimate": time_estimate,
            "resource_requirements": resource_requirements,
            "implementation_steps": roadmap,
            "confidence_score": confidence_score,
            "warnings": self._generate_warnings(difficulty_level, complexity_factors),
            "alternatives": self._suggest_alternatives(required_skills, difficulty_level)
        }
    
    def _extract_complexity_factors(self, article: Article) -> Dict[str, Any]:
        """Extract complexity factors from article."""
        content = f"{article.title} {article.content}".lower()
        
        factors = {
            "dependencies_count": len(article.technical.dependencies) if article.technical.dependencies else 0,
            "has_paper": bool(article.technical.paper_link),
            "code_available": article.technical.code_available,
            "implementation_ready": article.technical.implementation_ready,
            "gpu_required": False,
            "distributed_required": False,
            "novel_architecture": False,
            "large_scale": False,
            "research_level": False,
            "mathematical_complexity": 0,
            "reproducibility_score": article.technical.reproducibility_score
        }
        
        # Analyze content for complexity patterns
        for pattern_name, pattern in self.complexity_patterns.items():
            if pattern.search(content):
                if pattern_name in ["distributed_training", "distributed_required"]:
                    factors["distributed_required"] = True
                elif pattern_name == "novel_architecture":
                    factors["novel_architecture"] = True
                elif pattern_name == "large_scale":
                    factors["large_scale"] = True
                elif pattern_name == "research_level":
                    factors["research_level"] = True
        
        # Check for GPU requirements
        gpu_indicators = ["gpu", "cuda", "tensor", "neural network", "deep learning"]
        factors["gpu_required"] = any(indicator in content for indicator in gpu_indicators)
        
        # Estimate mathematical complexity
        math_terms = ["gradient", "optimization", "matrix", "vector", "calculus", "linear algebra"]
        factors["mathematical_complexity"] = sum(1 for term in math_terms if term in content)
        
        return factors
    
    def _calculate_complexity_score(self, factors: Dict[str, Any]) -> float:
        """Calculate overall complexity score (0-1)."""
        score = 0.0
        
        # Dependencies complexity
        deps_score = min(1.0, factors["dependencies_count"] / 10)
        score += 0.15 * deps_score
        
        # Implementation readiness (inverse)
        if not factors["implementation_ready"]:
            score += 0.2
        
        # Code availability (inverse)
        if not factors["code_available"]:
            score += 0.15
        
        # Hardware requirements
        if factors["gpu_required"]:
            score += 0.1
        if factors["distributed_required"]:
            score += 0.15
        
        # Novelty and research level
        if factors["novel_architecture"]:
            score += 0.1
        if factors["research_level"]:
            score += 0.1
        
        # Scale
        if factors["large_scale"]:
            score += 0.1
        
        # Mathematical complexity
        math_score = min(1.0, factors["mathematical_complexity"] / 5)
        score += 0.1 * math_score
        
        # Reproducibility (inverse)
        if factors["reproducibility_score"] > 0:
            score += 0.1 * (1 - factors["reproducibility_score"])
        else:
            score += 0.1  # Unknown reproducibility adds complexity
        
        return min(1.0, score)
    
    def _determine_difficulty_level(self, complexity_score: float, factors: Dict[str, Any]) -> str:
        """Determine difficulty level based on complexity score and factors."""
        if complexity_score >= 0.8 or factors["research_level"]:
            return DifficultyLevel.RESEARCH.value
        elif complexity_score >= 0.6 or factors["novel_architecture"] or factors["distributed_required"]:
            return DifficultyLevel.ADVANCED.value
        elif complexity_score >= 0.3 or factors["gpu_required"] or not factors["code_available"]:
            return DifficultyLevel.INTERMEDIATE.value
        else:
            return DifficultyLevel.BEGINNER.value
    
    def _identify_skill_requirements(self, article: Article) -> List[str]:
        """Identify required skills for implementation."""
        content = f"{article.title} {article.content}".lower()
        skills = set()
        
        # Analyze dependencies
        if article.technical.dependencies:
            for dep in article.technical.dependencies:
                dep_lower = dep.lower()
                if dep_lower in self.skill_taxonomy:
                    skills.add(dep)
                # Map common dependencies to skills
                elif "torch" in dep_lower:
                    skills.add("PyTorch")
                elif "tensorflow" in dep_lower or "tf" in dep_lower:
                    skills.add("TensorFlow")
                elif "transformers" in dep_lower:
                    skills.add("Transformers")
                elif "sklearn" in dep_lower:
                    skills.add("scikit-learn")
        
        # Analyze content for skill mentions
        skill_patterns = {
            "python": ["python", "pytorch", "tensorflow", "scikit-learn"],
            "machine_learning": ["machine learning", "ml", "neural network", "deep learning"],
            "computer_vision": ["computer vision", "cv", "image", "vision"],
            "nlp": ["nlp", "natural language", "text", "language model"],
            "distributed_systems": ["distributed", "parallel", "cluster", "multi-node"],
            "docker": ["docker", "container", "containerization"],
            "cloud_computing": ["aws", "gcp", "azure", "cloud"],
            "linear_algebra": ["matrix", "vector", "linear algebra", "eigenvalue"],
            "statistics": ["statistics", "probability", "statistical", "distribution"],
            "cuda": ["cuda", "gpu programming", "parallel computing"]
        }
        
        for skill, keywords in skill_patterns.items():
            if any(keyword in content for keyword in keywords):
                skills.add(skill.replace("_", " ").title())
        
        # Add basic skills
        if not skills:
            skills.add("Programming")
        
        # Add domain-specific skills based on content
        if any(term in content for term in ["neural", "network", "model", "training"]):
            skills.add("Deep Learning")
        
        return sorted(list(skills))
    
    def _estimate_time_requirements(self, difficulty_level: str, factors: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate implementation time requirements."""
        # Base time estimates by difficulty level (in hours)
        base_estimates = {
            "beginner": (8, 24),
            "intermediate": (24, 80),
            "advanced": (80, 200),
            "research": (200, 500)
        }
        
        min_hours, max_hours = base_estimates.get(difficulty_level, (24, 80))
        
        # Adjust based on complexity factors
        multiplier = 1.0
        
        if not factors["code_available"]:
            multiplier *= 1.5
        if not factors["implementation_ready"]:
            multiplier *= 1.3
        if factors["novel_architecture"]:
            multiplier *= 1.4
        if factors["distributed_required"]:
            multiplier *= 1.6
        if factors["large_scale"]:
            multiplier *= 1.3
        if factors["dependencies_count"] > 5:
            multiplier *= 1.2
        
        final_min = int(min_hours * multiplier)
        final_max = int(max_hours * multiplier)
        
        # Generate phase breakdown
        phases = self._generate_time_phases(final_min, final_max, difficulty_level)
        
        return {
            "min_hours": final_min,
            "max_hours": final_max,
            "multiplier_applied": round(multiplier, 2),
            "phases": phases,
            "confidence": self._estimate_time_confidence(factors)
        }
    
    def _generate_time_phases(self, min_hours: int, max_hours: int, difficulty: str) -> List[Dict]:
        """Generate time breakdown by implementation phases."""
        total_avg = (min_hours + max_hours) // 2
        
        if difficulty == "beginner":
            phases = [
                {"phase": "Setup & Learning", "percentage": 0.3},
                {"phase": "Implementation", "percentage": 0.5},
                {"phase": "Testing & Debugging", "percentage": 0.2}
            ]
        elif difficulty == "intermediate":
            phases = [
                {"phase": "Research & Planning", "percentage": 0.2},
                {"phase": "Environment Setup", "percentage": 0.15},
                {"phase": "Core Implementation", "percentage": 0.4},
                {"phase": "Integration & Testing", "percentage": 0.15},
                {"phase": "Optimization & Debugging", "percentage": 0.1}
            ]
        elif difficulty == "advanced":
            phases = [
                {"phase": "Deep Research", "percentage": 0.25},
                {"phase": "Architecture Design", "percentage": 0.15},
                {"phase": "Infrastructure Setup", "percentage": 0.1},
                {"phase": "Core Development", "percentage": 0.3},
                {"phase": "Advanced Testing", "percentage": 0.1},
                {"phase": "Performance Optimization", "percentage": 0.1}
            ]
        else:  # research
            phases = [
                {"phase": "Literature Review", "percentage": 0.2},
                {"phase": "Theoretical Development", "percentage": 0.15},
                {"phase": "Experimental Design", "percentage": 0.1},
                {"phase": "Implementation", "percentage": 0.25},
                {"phase": "Experimentation", "percentage": 0.15},
                {"phase": "Analysis & Refinement", "percentage": 0.15}
            ]
        
        # Calculate hours for each phase
        for phase in phases:
            phase["estimated_hours"] = int(total_avg * phase["percentage"])
        
        return phases
    
    def _estimate_time_confidence(self, factors: Dict[str, Any]) -> float:
        """Estimate confidence in time estimates."""
        confidence = 1.0
        
        if not factors["code_available"]:
            confidence -= 0.2
        if factors["novel_architecture"]:
            confidence -= 0.3
        if factors["research_level"]:
            confidence -= 0.4
        if factors["reproducibility_score"] < 0.5:
            confidence -= 0.2
        if factors["dependencies_count"] > 10:
            confidence -= 0.1
        
        return max(0.1, confidence)
    
    def _assess_resource_requirements(self, article: Article) -> ResourceRequirement:
        """Assess computational and infrastructure resource requirements."""
        compute_req = self._assess_compute_requirements(article)
        storage_req = self._assess_storage_requirements(article)
        network_req = self._assess_network_requirements(article)
        cost_estimate = self._estimate_implementation_cost(compute_req["type"])
        alternatives = self._suggest_resource_alternatives(compute_req)
        
        return ResourceRequirement(
            compute=compute_req,
            storage=storage_req,
            network=network_req,
            estimated_cost=cost_estimate,
            alternatives=alternatives
        )
    
    def _assess_compute_requirements(self, article: Article) -> Dict[str, Any]:
        """Assess compute requirements."""
        content = f"{article.title} {article.content}".lower()
        
        # Check for explicit compute requirements
        if article.technical.compute_requirements:
            gpu_spec = article.technical.compute_requirements.gpu
            memory_spec = article.technical.compute_requirements.memory
            return {
                "type": gpu_spec,
                "memory": memory_spec,
                "recommended_instance": self._map_to_cloud_instance(gpu_spec),
                "parallel_capability": "distributed" in content
            }
        
        # Infer requirements from content
        if any(term in content for term in ["8x a100", "multi-gpu", "distributed"]):
            compute_type = "8x_a100"
        elif any(term in content for term in ["a100", "v100", "large model"]):
            compute_type = "a100"
        elif any(term in content for term in ["gpu", "cuda", "neural"]):
            compute_type = "rtx_4090"
        else:
            compute_type = "cpu_only"
        
        return {
            "type": compute_type,
            "memory": self._estimate_memory_requirements(content),
            "recommended_instance": self._map_to_cloud_instance(compute_type),
            "parallel_capability": "distributed" in content or "parallel" in content
        }
    
    def _assess_storage_requirements(self, article: Article) -> Dict[str, str]:
        """Assess storage requirements."""
        content = f"{article.title} {article.content}".lower()
        
        # Estimate based on data scale mentioned
        if any(term in content for term in ["billion", "tb", "petabyte"]):
            return {"size": "1-10 TB", "type": "High-performance SSD", "backup": "Required"}
        elif any(term in content for term in ["million", "gb", "dataset"]):
            return {"size": "100GB-1TB", "type": "SSD recommended", "backup": "Recommended"}
        else:
            return {"size": "10-100 GB", "type": "Standard SSD", "backup": "Optional"}
    
    def _assess_network_requirements(self, article: Article) -> Dict[str, str]:
        """Assess network requirements."""
        content = f"{article.title} {article.content}".lower()
        
        if "distributed" in content or "cluster" in content:
            return {
                "bandwidth": "High (10+ Gbps)",
                "latency": "Low (<1ms inter-node)",
                "type": "InfiniBand recommended"
            }
        elif "cloud" in content or "remote" in content:
            return {
                "bandwidth": "Medium (1+ Gbps)",
                "latency": "Standard",
                "type": "Standard Ethernet"
            }
        else:
            return {
                "bandwidth": "Standard",
                "latency": "Standard", 
                "type": "Standard connection"
            }
    
    def _map_to_cloud_instance(self, compute_type: str) -> str:
        """Map compute requirements to cloud instance types."""
        mapping = {
            "cpu_only": "c5.2xlarge (AWS) / n1-highcpu-8 (GCP)",
            "rtx_4090": "g4dn.xlarge (AWS) / n1-standard-4 + T4 (GCP)",
            "v100": "p3.2xlarge (AWS) / n1-standard-8 + V100 (GCP)", 
            "a100": "p4d.xlarge (AWS) / a2-highgpu-1g (GCP)",
            "8x_a100": "p4d.24xlarge (AWS) / a2-megagpu-16g (GCP)",
            "h100": "p5.xlarge (AWS) / a3-highgpu-8g (GCP)"
        }
        return mapping.get(compute_type, "Standard compute instance")
    
    def _estimate_memory_requirements(self, content: str) -> str:
        """Estimate memory requirements from content."""
        if any(term in content for term in ["billion parameters", "large model", "175b"]):
            return "200+ GB"
        elif any(term in content for term in ["million parameters", "medium model"]):
            return "32-200 GB"
        elif any(term in content for term in ["neural", "deep learning"]):
            return "8-32 GB"
        else:
            return "4-16 GB"
    
    def _estimate_implementation_cost(self, compute_requirement: str = "cpu_only") -> Dict[str, float]:
        """Estimate implementation costs."""
        hourly_rate = self.cost_models["compute_hourly_rates"].get(compute_requirement, 0.1)
        
        # Estimate for different time periods
        return {
            "hourly": hourly_rate,
            "daily_8h": hourly_rate * 8,
            "weekly_40h": hourly_rate * 40,
            "monthly_160h": hourly_rate * 160,
            "full_project_estimate": hourly_rate * 200  # Rough project estimate
        }
    
    def _suggest_resource_alternatives(self, compute_req: Dict) -> List[str]:
        """Suggest alternative resource configurations."""
        alternatives = []
        
        compute_type = compute_req.get("type", "cpu_only")
        
        if compute_type == "8x_a100":
            alternatives = [
                "Use gradient checkpointing to reduce memory",
                "Model parallelism across multiple smaller GPUs", 
                "Use cloud spot instances for cost savings",
                "Consider TPU alternatives",
                "Implement mixed precision training"
            ]
        elif compute_type == "a100":
            alternatives = [
                "Use multiple RTX 4090s instead",
                "Cloud GPU instances with preemption",
                "Local GPU cluster setup",
                "Rent dedicated GPU servers"
            ]
        elif compute_type == "rtx_4090":
            alternatives = [
                "Use RTX 4080 with longer training time",
                "Cloud GPU instances (T4/V100)",
                "Google Colab Pro+ with A100 access",
                "Local RTX 3080/3090 setup"
            ]
        else:
            alternatives = [
                "Use cloud CPU instances for scalability",
                "Local development machine sufficient",
                "Consider GPU acceleration for speedup"
            ]
        
        return alternatives
    
    def _generate_implementation_roadmap(self, analysis: Dict[str, Any]) -> List[ImplementationPhase]:
        """Generate detailed implementation roadmap."""
        difficulty = analysis["difficulty_level"]
        skills = analysis["skill_requirements"]
        time_phases = analysis["time_estimate"]["phases"]
        
        roadmap = []
        
        for phase_info in time_phases:
            phase = ImplementationPhase(
                phase=phase_info["phase"],
                description=self._generate_phase_description(phase_info["phase"], difficulty),
                estimated_hours=phase_info["estimated_hours"],
                required_skills=self._get_phase_skills(phase_info["phase"], skills),
                deliverables=self._get_phase_deliverables(phase_info["phase"]),
                risk_factors=self._get_phase_risks(phase_info["phase"], difficulty)
            )
            roadmap.append(phase)
        
        return roadmap
    
    def _generate_phase_description(self, phase_name: str, difficulty: str) -> str:
        """Generate description for implementation phase."""
        descriptions = {
            "Setup & Learning": "Set up development environment, learn required frameworks and tools",
            "Research & Planning": "Understand the technical approach, read papers, plan architecture", 
            "Deep Research": "Comprehensive literature review, theoretical understanding, experimental design",
            "Environment Setup": "Configure development environment, install dependencies, set up infrastructure",
            "Architecture Design": "Design system architecture, plan component interactions, create technical specs",
            "Core Implementation": "Implement main algorithms and functionality",
            "Core Development": "Build core system components with advanced features",
            "Implementation": "Build and iterate on the solution",
            "Integration & Testing": "Integrate components, write tests, validate functionality",
            "Advanced Testing": "Comprehensive testing including edge cases and performance validation",
            "Testing & Debugging": "Test implementation and fix issues",
            "Optimization & Debugging": "Performance optimization and bug fixes",
            "Performance Optimization": "Advanced performance tuning and scalability improvements",
            "Experimentation": "Run experiments, collect data, analyze results",
            "Analysis & Refinement": "Analyze results, refine approach, document findings"
        }
        return descriptions.get(phase_name, "Complete this implementation phase")
    
    def _get_phase_skills(self, phase_name: str, all_skills: List[str]) -> List[str]:
        """Get skills required for specific phase."""
        if "Research" in phase_name or "Literature" in phase_name:
            return ["Research", "Academic Reading", "Technical Analysis"]
        elif "Setup" in phase_name or "Environment" in phase_name:
            return ["DevOps", "System Administration", "Package Management"]
        elif "Architecture" in phase_name or "Design" in phase_name:
            return ["System Design", "Software Architecture", "Technical Planning"]
        elif "Implementation" in phase_name or "Development" in phase_name:
            return all_skills
        elif "Testing" in phase_name:
            return ["Testing", "Debugging", "Quality Assurance"]
        elif "Optimization" in phase_name:
            return ["Performance Optimization", "Profiling", "Advanced Debugging"]
        else:
            return all_skills[:3]  # Top 3 skills for other phases
    
    def _get_phase_deliverables(self, phase_name: str) -> List[str]:
        """Get expected deliverables for phase."""
        deliverables = {
            "Setup & Learning": ["Development environment", "Learning notes", "Tool familiarity"],
            "Research & Planning": ["Technical specification", "Implementation plan", "Resource requirements"],
            "Deep Research": ["Literature review", "Theoretical framework", "Research notes"],
            "Environment Setup": ["Configured environment", "Dependency installation", "Infrastructure setup"],
            "Architecture Design": ["System architecture", "Component specifications", "Technical documentation"],
            "Core Implementation": ["Working prototype", "Core functionality", "Basic tests"],
            "Core Development": ["Full implementation", "Advanced features", "Integration tests"],
            "Implementation": ["Working solution", "Documentation", "Basic validation"],
            "Integration & Testing": ["Integrated system", "Test suite", "Validation results"],
            "Advanced Testing": ["Comprehensive test results", "Performance benchmarks", "Edge case validation"],
            "Testing & Debugging": ["Tested implementation", "Bug fixes", "Validation report"],
            "Optimization & Debugging": ["Optimized code", "Performance improvements", "Issue resolution"],
            "Performance Optimization": ["Performance metrics", "Optimization report", "Scalability analysis"],
            "Experimentation": ["Experimental results", "Data analysis", "Performance metrics"],
            "Analysis & Refinement": ["Final analysis", "Refinement recommendations", "Documentation"]
        }
        return deliverables.get(phase_name, ["Phase completion", "Documentation", "Progress report"])
    
    def _get_phase_risks(self, phase_name: str, difficulty: str) -> List[str]:
        """Get risk factors for phase."""
        common_risks = []
        
        if "Research" in phase_name:
            common_risks = ["Information overload", "Analysis paralysis", "Unclear requirements"]
        elif "Setup" in phase_name:
            common_risks = ["Compatibility issues", "Missing dependencies", "Configuration errors"]
        elif "Implementation" in phase_name or "Development" in phase_name:
            common_risks = ["Technical challenges", "Scope creep", "Integration issues"]
        elif "Testing" in phase_name:
            common_risks = ["Insufficient test coverage", "Hard-to-reproduce bugs", "Performance issues"]
        elif "Optimization" in phase_name:
            common_risks = ["Premature optimization", "Performance degradation", "Complexity increase"]
        
        if difficulty in ["advanced", "research"]:
            common_risks.extend(["Novel technical challenges", "Limited documentation", "Experimental approaches"])
        
        return common_risks
    
    def _calculate_confidence_score(self, article: Article, factors: Dict[str, Any]) -> float:
        """Calculate confidence in the analysis."""
        confidence = 1.0
        
        # Reduce confidence for missing information
        if not article.technical.paper_link:
            confidence -= 0.1
        if not article.technical.dependencies:
            confidence -= 0.15
        if not article.technical.compute_requirements:
            confidence -= 0.1
        if article.technical.reproducibility_score < 0.3:
            confidence -= 0.2
        if factors["research_level"]:
            confidence -= 0.25
        if factors["novel_architecture"]:
            confidence -= 0.15
        
        return max(0.1, confidence)
    
    def _generate_warnings(self, difficulty: str, factors: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate warnings for implementation challenges."""
        warnings = []
        
        if difficulty == "research":
            warnings.append({
                "level": "high",
                "message": "This is research-level work that may require significant time and expertise",
                "recommendation": "Consider collaborating with research institutions or hiring specialists"
            })
        
        if factors["novel_architecture"]:
            warnings.append({
                "level": "medium", 
                "message": "Novel architecture may require custom implementation from scratch",
                "recommendation": "Budget extra time for experimentation and debugging"
            })
        
        if factors["distributed_required"]:
            warnings.append({
                "level": "medium",
                "message": "Distributed systems expertise required for proper implementation", 
                "recommendation": "Consider consulting with distributed systems experts"
            })
        
        if not factors["code_available"]:
            warnings.append({
                "level": "medium",
                "message": "No reference implementation available - will require building from scratch",
                "recommendation": "Expect longer development time and higher complexity"
            })
        
        if factors["large_scale"]:
            warnings.append({
                "level": "high",
                "message": "Large-scale implementation requires significant computational resources",
                "recommendation": "Plan for substantial infrastructure and cost requirements"
            })
        
        return warnings
    
    def _suggest_alternatives(self, skills: List[str], difficulty: str) -> List[Dict[str, str]]:
        """Suggest alternative approaches or technologies."""
        alternatives = []
        
        # Suggest simpler alternatives for high difficulty
        if difficulty in ["advanced", "research"]:
            alternatives.append({
                "type": "approach",
                "suggestion": "Start with simpler baseline implementation",
                "benefit": "Faster time to working prototype, easier debugging"
            })
            alternatives.append({
                "type": "collaboration", 
                "suggestion": "Partner with academic institutions or research labs",
                "benefit": "Access to expertise and computational resources"
            })
        
        # Suggest cloud alternatives for resource-intensive projects
        if any(skill in ["CUDA", "Distributed Systems"] for skill in skills):
            alternatives.append({
                "type": "infrastructure",
                "suggestion": "Use managed cloud ML services (AWS SageMaker, Google Vertex AI)",
                "benefit": "Reduced infrastructure management, built-in scaling"
            })
        
        # Suggest open-source alternatives
        alternatives.append({
            "type": "tools",
            "suggestion": "Leverage existing open-source implementations and libraries",
            "benefit": "Faster development, community support, proven reliability"
        })
        
        return alternatives