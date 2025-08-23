"""Settings and configuration management."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

import yaml
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Application settings configuration."""
    
    # Basic settings
    hours_lookback: int = 24
    max_items_per_category: int = 10
    translate_to_ja: bool = True
    translate_engine: str = "deepl"
    
    # AI/ML settings
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = "gemini-2.5-flash-002"
    gemini_url_context_batch: int = 20
    embedding_model: str = "sentence-transformers/all-MiniLM-L12-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"
    ner_model: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    
    # Data source tiers
    tier1_sources: list = field(default_factory=lambda: [
        "arxiv", "openai", "anthropic", "deepmind", 
        "papers-with-code", "google-ai", "meta-ai",
        "microsoft-research", "hugging-face"
    ])
    
    tier2_sources: list = field(default_factory=lambda: [
        "github-trending", "towards-data-science", 
        "techcrunch", "venturebeat", "the-information",
        "reddit-ml", "hackernews"
    ])
    
    # Evaluation weights
    engineer_weights: Dict[str, float] = field(default_factory=lambda: {
        "technical_depth": 0.35,
        "implementation": 0.25,
        "novelty": 0.20,
        "reproducibility": 0.15,
        "community_impact": 0.05
    })
    
    business_weights: Dict[str, float] = field(default_factory=lambda: {
        "business_impact": 0.40,
        "roi_potential": 0.25,
        "market_validation": 0.20,
        "implementation_ease": 0.10,
        "strategic_value": 0.05
    })
    
    # Performance settings
    cache_ttl_seconds: int = 3600
    vector_index_size: int = 100000
    batch_processing_size: int = 50
    parallel_workers: int = 8
    
    # Search settings
    search_hybrid_weight: float = 0.7  # BM25 vs Semantic
    search_top_k: int = 100
    rerank_top_k: int = 20
    
    # Time value settings
    half_life_hours: int = 72
    evergreen_boost_factor: float = 1.5
    trend_window_days: int = 7
    
    # Quality thresholds
    min_content_length: int = 500
    max_summary_length: int = 300
    faithfulness_threshold: float = 0.8
    bias_detection_sensitivity: str = "medium"
    recommendation_threshold: float = 0.75
    noise_filter_threshold: float = 0.3
    
    # Database settings
    database_url: str = field(default_factory=lambda: os.getenv(
        "DATABASE_URL", 
        "postgresql://localhost/daily_ai_news"
    ))
    redis_url: str = field(default_factory=lambda: os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    ))
    qdrant_url: str = field(default_factory=lambda: os.getenv(
        "QDRANT_URL",
        "localhost:6333"
    ))
    
    # Output settings
    output_dir: Path = field(default_factory=lambda: Path("dist"))
    template_dir: Path = field(default_factory=lambda: Path("templates"))
    static_dir: Path = field(default_factory=lambda: Path("static"))
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize settings from environment and config file."""
        # Initialize default values from dataclass
        self.hours_lookback = 24
        self.max_items_per_category = 10
        self.translate_to_ja = True
        self.translate_engine = "deepl"
        
        # AI/ML settings
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = "gemini-2.5-flash-002"
        self.gemini_url_context_batch = 20
        self.embedding_model = "sentence-transformers/all-MiniLM-L12-v2"
        self.reranker_model = "cross-encoder/ms-marco-MiniLM-L-12-v2"
        self.ner_model = "dbmdz/bert-large-cased-finetuned-conll03-english"
        
        # Data source tiers
        self.tier1_sources = [
            "arxiv", "openai", "anthropic", "deepmind", 
            "papers-with-code", "google-ai", "meta-ai",
            "microsoft-research", "hugging-face"
        ]
        
        self.tier2_sources = [
            "github-trending", "towards-data-science", 
            "techcrunch", "venturebeat", "the-information",
            "reddit-ml", "hackernews"
        ]
        
        # Evaluation weights
        self.engineer_weights = {
            "technical_depth": 0.35,
            "implementation": 0.25,
            "novelty": 0.20,
            "reproducibility": 0.15,
            "community_impact": 0.05
        }
        
        self.business_weights = {
            "business_impact": 0.40,
            "roi_potential": 0.25,
            "market_validation": 0.20,
            "implementation_ease": 0.10,
            "strategic_value": 0.05
        }
        
        # Performance settings
        self.cache_ttl_seconds = 3600
        self.vector_index_size = 100000
        self.batch_processing_size = 50
        self.parallel_workers = 8
        
        # Search settings
        self.search_hybrid_weight = 0.7
        self.search_top_k = 100
        self.rerank_top_k = 20
        
        # Time value settings
        self.half_life_hours = 72
        self.evergreen_boost_factor = 1.5
        self.trend_window_days = 7
        
        # Quality thresholds
        self.min_content_length = 500
        self.max_summary_length = 300
        self.faithfulness_threshold = 0.8
        self.bias_detection_sensitivity = "medium"
        self.recommendation_threshold = 0.75
        self.noise_filter_threshold = 0.3
        
        # Database settings
        self.database_url = os.getenv("DATABASE_URL", "postgresql://localhost/daily_ai_news")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.qdrant_url = os.getenv("QDRANT_URL", "localhost:6333")
        
        # Output settings - Get from environment or use defaults
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "docs"))
        self.template_dir = Path(os.getenv("TEMPLATE_DIR", "templates"))
        self.static_dir = Path(os.getenv("STATIC_DIR", "static"))
        
        # UI settings
        self.ui_theme = os.getenv("UI_THEME", "professional")
        self.base_url = os.getenv("BASE_URL", "https://example.com")
        self.default_persona = os.getenv("DEFAULT_PERSONA", "engineer")
        
        # Load from config file if provided
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
        
        # Override with environment variables
        self._load_from_env()
        
        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_from_env(self):
        """Load settings from environment variables."""
        env_mappings = {
            "HOURS_LOOKBACK": ("hours_lookback", int),
            "MAX_ITEMS_PER_CATEGORY": ("max_items_per_category", int),
            "TRANSLATE_TO_JA": ("translate_to_ja", lambda x: x.lower() == "true"),
            "GEMINI_API_KEY": ("gemini_api_key", str),
            "GEMINI_MODEL": ("gemini_model", str),
            "CACHE_TTL_SECONDS": ("cache_ttl_seconds", int),
            "BATCH_PROCESSING_SIZE": ("batch_processing_size", int),
        }
        
        for env_key, (attr_name, converter) in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value:
                setattr(self, attr_name, converter(env_value))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            key: getattr(self, key)
            for key in self.__dataclass_fields__.keys()
        }