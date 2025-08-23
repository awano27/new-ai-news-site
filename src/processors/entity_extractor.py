"""Entity extraction from article content."""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.config.settings import Settings
from src.models.article import Article, Entities


@dataclass
class EntityMatch:
    """Entity match with confidence score."""
    text: str
    entity_type: str
    confidence: float
    start_pos: int = 0
    end_pos: int = 0


class EntityExtractor:
    """Extract entities from article content using NLP and pattern matching."""
    
    def __init__(self, settings: Settings):
        """Initialize entity extractor."""
        self.settings = settings
        
        # Precompiled patterns for efficiency
        self.patterns = self._compile_patterns()
        
        # Known entity dictionaries
        self.known_companies = self._load_known_companies()
        self.known_technologies = self._load_known_technologies()
        self.known_people = self._load_known_people()
        self.known_concepts = self._load_known_concepts()
        self.known_products = self._load_known_products()
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for entity extraction."""
        patterns = {
            # Company patterns
            "company_suffix": re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc|Corp|LLC|Ltd|Co|Company)\b'),
            "company_prefix": re.compile(r'\b(?:The\s+)?([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\s+(?:Corporation|Company)\b'),
            
            # Technology patterns
            "model_version": re.compile(r'\b([A-Z]+)-?(\d+(?:\.\d+)*)\b'),  # GPT-4, BERT-base
            "framework": re.compile(r'\b(TensorFlow|PyTorch|Keras|scikit-learn|Hugging\s+Face)\b', re.IGNORECASE),
            "programming_lang": re.compile(r'\b(Python|JavaScript|Java|C\+\+|Go|Rust|Swift)\b'),
            
            # Performance metrics
            "accuracy": re.compile(r'(\d+\.?\d*)\s*%?\s*accuracy'),
            "parameters": re.compile(r'(\d+\.?\d*)\s*([BMK])\s*parameters?'),
            "benchmark": re.compile(r'\b([A-Z]+(?:[A-Z0-9\-]*[A-Z0-9])?)\s+benchmark'),
            
            # Person patterns
            "person_name": re.compile(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'),
            "researcher": re.compile(r'(?:Dr\.\s+|Prof\.\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+)'),
            
            # Product patterns
            "product_name": re.compile(r'\b([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)\s+(?:API|SDK|platform|system)\b'),
            
            # Concept patterns
            "ai_concept": re.compile(r'\b(machine learning|deep learning|neural network|natural language processing|computer vision|reinforcement learning)\b', re.IGNORECASE),
            "technical_concept": re.compile(r'\b(transformer|attention|embedding|gradient|optimization|regularization)\b', re.IGNORECASE),
        }
        
        return patterns
    
    def _load_known_companies(self) -> Dict[str, float]:
        """Load known company names with confidence scores."""
        companies = {
            # Major tech companies
            "OpenAI": 0.95, "Microsoft": 0.95, "Google": 0.95, "Meta": 0.95, "Apple": 0.95,
            "Amazon": 0.95, "Netflix": 0.9, "Tesla": 0.9, "NVIDIA": 0.95, "AMD": 0.9,
            
            # AI-specific companies
            "Anthropic": 0.95, "DeepMind": 0.95, "Cohere": 0.9, "Stability AI": 0.9,
            "Hugging Face": 0.9, "Scale AI": 0.85, "Weights & Biases": 0.85,
            
            # Research institutions
            "MIT": 0.9, "Stanford": 0.9, "CMU": 0.9, "Berkeley": 0.85, "Oxford": 0.85,
            "Cambridge": 0.85, "Harvard": 0.85, "Princeton": 0.85,
            
            # Startups and smaller companies
            "Replicate": 0.8, "Runway": 0.8, "Character.AI": 0.8, "Midjourney": 0.8,
        }
        return companies
    
    def _load_known_technologies(self) -> Dict[str, float]:
        """Load known technology terms."""
        technologies = {
            # Models and architectures
            "GPT": 0.95, "BERT": 0.95, "T5": 0.9, "CLIP": 0.9, "DALLE": 0.9,
            "ChatGPT": 0.95, "Claude": 0.9, "LLaMA": 0.9, "PaLM": 0.9,
            "Transformer": 0.95, "CNN": 0.9, "RNN": 0.85, "LSTM": 0.85,
            
            # Frameworks and libraries
            "TensorFlow": 0.95, "PyTorch": 0.95, "Keras": 0.9, "JAX": 0.85,
            "scikit-learn": 0.9, "OpenCV": 0.85, "NLTK": 0.8, "spaCy": 0.8,
            
            # Hardware and infrastructure
            "CUDA": 0.9, "TPU": 0.9, "GPU": 0.85, "CPU": 0.7,
            "A100": 0.85, "V100": 0.8, "H100": 0.9,
            
            # Techniques and methods
            "fine-tuning": 0.9, "transfer learning": 0.9, "few-shot": 0.85,
            "zero-shot": 0.85, "prompt engineering": 0.9, "RLHF": 0.9,
        }
        return technologies
    
    def _load_known_people(self) -> Dict[str, float]:
        """Load known person names in AI/tech."""
        people = {
            # OpenAI
            "Sam Altman": 0.95, "Greg Brockman": 0.9, "Ilya Sutskever": 0.95,
            
            # Google/DeepMind
            "Demis Hassabis": 0.95, "Geoffrey Hinton": 0.95, "Yann LeCun": 0.95,
            "Yoshua Bengio": 0.95, "Andrew Ng": 0.95,
            
            # Meta/Facebook
            "Mark Zuckerberg": 0.9, "Jerome Pesenti": 0.8,
            
            # Anthropic
            "Dario Amodei": 0.9, "Daniela Amodei": 0.85,
            
            # Academic researchers
            "Fei-Fei Li": 0.9, "Sebastian Thrun": 0.85, "Pieter Abbeel": 0.8,
            "Andrej Karpathy": 0.9, "Chelsea Finn": 0.8,
        }
        return people
    
    def _load_known_concepts(self) -> Dict[str, float]:
        """Load known AI/ML concepts."""
        concepts = {
            "artificial intelligence": 0.95, "machine learning": 0.95, "deep learning": 0.95,
            "neural networks": 0.9, "natural language processing": 0.9, "computer vision": 0.9,
            "reinforcement learning": 0.9, "supervised learning": 0.85, "unsupervised learning": 0.85,
            "generative AI": 0.9, "large language model": 0.9, "foundation model": 0.85,
            "multimodal": 0.8, "alignment": 0.8, "safety": 0.7, "interpretability": 0.8,
        }
        return concepts
    
    def _load_known_products(self) -> Dict[str, float]:
        """Load known AI products and services."""
        products = {
            "ChatGPT": 0.95, "Claude": 0.9, "Bard": 0.9, "Bing Chat": 0.85,
            "DALL-E": 0.9, "Midjourney": 0.9, "Stable Diffusion": 0.9,
            "GitHub Copilot": 0.9, "CodeWhisperer": 0.8, "Tabnine": 0.8,
            "AutoGPT": 0.8, "LangChain": 0.8, "Pinecone": 0.8,
        }
        return products
    
    async def extract_entities(self, text: str) -> Entities:
        """Extract all types of entities from text."""
        if not text or not text.strip():
            return Entities()
        
        entities = Entities()
        
        # Extract each type of entity
        entities.companies = self.extract_companies(text)
        entities.technologies = self.extract_technologies(text)
        entities.people = self.extract_people(text)
        entities.concepts = self.extract_concepts(text)
        entities.products = self.extract_products(text)
        
        # Normalize and deduplicate
        entities.companies = self.normalize_entities(entities.companies)
        entities.technologies = self.normalize_entities(entities.technologies)
        entities.people = self.normalize_entities(entities.people)
        entities.concepts = self.normalize_entities(entities.concepts)
        entities.products = self.normalize_entities(entities.products)
        
        return entities
    
    async def extract_from_article(self, article: Article) -> Entities:
        """Extract entities from article content."""
        full_text = f"{article.title}\n\n{article.content}"
        return await self.extract_entities(full_text)
    
    def extract_companies(self, text: str) -> List[str]:
        """Extract company entities."""
        companies = []
        
        # Check against known companies
        for company, confidence in self.known_companies.items():
            if company.lower() in text.lower():
                companies.append(company)
        
        # Pattern-based extraction
        for pattern_name, pattern in self.patterns.items():
            if "company" in pattern_name:
                matches = pattern.findall(text)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]  # Take first group
                    if len(match) > 2 and match not in companies:
                        companies.append(match)
        
        return companies
    
    def extract_technologies(self, text: str) -> List[str]:
        """Extract technology entities."""
        technologies = []
        
        # Check against known technologies
        for tech, confidence in self.known_technologies.items():
            # Case-insensitive search for technologies
            pattern = re.compile(re.escape(tech), re.IGNORECASE)
            if pattern.search(text):
                technologies.append(tech)
        
        # Pattern-based extraction
        tech_patterns = ["model_version", "framework", "programming_lang"]
        for pattern_name in tech_patterns:
            if pattern_name in self.patterns:
                matches = self.patterns[pattern_name].findall(text)
                for match in matches:
                    if isinstance(match, tuple):
                        match = "-".join(match) if pattern_name == "model_version" else match[0]
                    if match not in technologies:
                        technologies.append(match)
        
        return technologies
    
    def extract_people(self, text: str) -> List[str]:
        """Extract person entities."""
        people = []
        
        # Check against known people
        for person, confidence in self.known_people.items():
            if person.lower() in text.lower():
                people.append(person)
        
        # Pattern-based extraction for person names
        person_matches = self.patterns["person_name"].findall(text)
        researcher_matches = self.patterns["researcher"].findall(text)
        
        all_matches = person_matches + researcher_matches
        
        for match in all_matches:
            # Filter out common false positives
            if self._is_likely_person_name(match) and match not in people:
                people.append(match)
        
        return people
    
    def extract_concepts(self, text: str) -> List[str]:
        """Extract concept entities."""
        concepts = []
        
        # Check against known concepts
        for concept, confidence in self.known_concepts.items():
            pattern = re.compile(re.escape(concept), re.IGNORECASE)
            if pattern.search(text):
                concepts.append(concept)
        
        # Pattern-based extraction
        concept_patterns = ["ai_concept", "technical_concept"]
        for pattern_name in concept_patterns:
            if pattern_name in self.patterns:
                matches = self.patterns[pattern_name].findall(text)
                for match in matches:
                    if match.lower() not in [c.lower() for c in concepts]:
                        concepts.append(match.lower())
        
        return concepts
    
    def extract_products(self, text: str) -> List[str]:
        """Extract product entities."""
        products = []
        
        # Check against known products
        for product, confidence in self.known_products.items():
            if product.lower() in text.lower():
                products.append(product)
        
        # Pattern-based extraction
        product_matches = self.patterns["product_name"].findall(text)
        for match in products:
            if match not in products and len(match) > 3:
                products.append(match)
        
        return products
    
    def _is_likely_person_name(self, name: str) -> bool:
        """Check if a string is likely a person's name."""
        # Simple heuristics to filter out false positives
        false_positives = {
            "United States", "New York", "San Francisco", "Los Angeles",
            "Machine Learning", "Deep Learning", "Computer Science",
            "Artificial Intelligence", "Natural Language", "Neural Network"
        }
        
        if name in false_positives:
            return False
        
        # Name should have 2-3 parts, each capitalized
        parts = name.split()
        if len(parts) < 2 or len(parts) > 3:
            return False
        
        # Each part should start with capital letter
        for part in parts:
            if not part[0].isupper() or len(part) < 2:
                return False
        
        return True
    
    def normalize_entities(self, entities: List[str]) -> List[str]:
        """Normalize and deduplicate entities."""
        if not entities:
            return []
        
        normalized = []
        seen_lower = set()
        
        for entity in entities:
            entity_clean = entity.strip()
            entity_lower = entity_clean.lower()
            
            # Skip if already seen (case-insensitive)
            if entity_lower in seen_lower:
                continue
            
            # Skip very short entities
            if len(entity_clean) < 2:
                continue
            
            # Skip common stop words
            stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            if entity_lower in stop_words:
                continue
            
            normalized.append(entity_clean)
            seen_lower.add(entity_lower)
        
        return sorted(normalized)  # Sort for consistency
    
    def filter_by_confidence(self, entities_with_confidence: List[Dict[str, Any]], threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Filter entities by confidence threshold."""
        return [
            entity for entity in entities_with_confidence
            if entity.get("confidence", 0.0) >= threshold
        ]
    
    def extract_metrics(self, text: str) -> Dict[str, Any]:
        """Extract performance metrics from text."""
        metrics = {}
        
        # Accuracy extraction
        accuracy_matches = self.patterns["accuracy"].findall(text)
        if accuracy_matches:
            metrics["accuracy"] = [float(match) for match in accuracy_matches]
        
        # Parameter count extraction
        param_matches = self.patterns["parameters"].findall(text)
        if param_matches:
            params = []
            for value, unit in param_matches:
                multiplier = {"B": 1e9, "M": 1e6, "K": 1e3}.get(unit, 1)
                params.append(float(value) * multiplier)
            metrics["parameters"] = params
        
        # Benchmark mentions
        benchmark_matches = self.patterns["benchmark"].findall(text)
        if benchmark_matches:
            metrics["benchmarks"] = list(set(benchmark_matches))
        
        return metrics
    
    def get_entity_statistics(self) -> Dict[str, int]:
        """Get statistics about known entities."""
        return {
            "companies": len(self.known_companies),
            "technologies": len(self.known_technologies),
            "people": len(self.known_people),
            "concepts": len(self.known_concepts),
            "products": len(self.known_products)
        }