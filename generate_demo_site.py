#!/usr/bin/env python3
"""Generate demo site for testing and preview."""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import Settings
from src.models.article import Article
from src.generators.static_site_generator import StaticSiteGenerator


async def create_demo_articles():
    """Create demo articles for the site."""
    articles = []
    
    # Article 1: High-tier technical breakthrough
    article1 = Article(
        id="demo-001",
        title="Revolutionary Transformer Architecture Achieves State-of-the-Art Performance",
        url="https://arxiv.org/abs/2024.example1",
        source="ArXiv",
        source_tier=1,
        published_date=datetime.now(),
        content="""
        Researchers have developed a novel transformer architecture that achieves unprecedented 
        performance across multiple NLP benchmarks. The architecture, dubbed "UltraTransformer", 
        incorporates sparse attention mechanisms and dynamic layer routing to reduce computational 
        complexity while maintaining accuracy. Key innovations include:
        
        - Adaptive attention patterns that adjust based on input complexity
        - Dynamic layer selection for optimal resource utilization  
        - Novel positional encodings for longer context understanding
        - Efficient gradient flow through skip connections
        
        The model demonstrates 15% improvement on GLUE benchmarks while using 40% less compute 
        than comparable models. Implementation code and trained weights are available on GitHub.
        """
    )
    article1.evaluation = {
        "engineer": {
            "total_score": 0.92,
            "breakdown": {
                "technical_depth": 0.95,
                "implementation_ready": 0.90,
                "novelty": 0.88,
                "reproducibility": 0.94
            }
        },
        "business": {
            "total_score": 0.78,
            "breakdown": {
                "business_impact": 0.82,
                "market_potential": 0.75,
                "adoption_timeline": 0.70
            }
        }
    }
    articles.append(article1)
    
    # Article 2: Business-focused case study
    article2 = Article(
        id="demo-002",
        title="Enterprise AI Implementation Delivers $50M in Cost Savings: McKinsey Case Study",
        url="https://mckinsey.com/ai-case-study-2024",
        source="McKinsey & Company",
        source_tier=1,
        published_date=datetime.now(),
        content="""
        A comprehensive analysis of Fortune 500 AI implementations reveals significant ROI 
        opportunities. The study, spanning 18 months across 50 companies, identifies key 
        success factors and quantifiable business outcomes:
        
        Financial Impact:
        - Average 35% reduction in operational costs
        - $50M average annual savings per implementation
        - 6-month average payback period
        - 250% average ROI over 2 years
        
        Implementation Insights:
        - C-suite engagement critical for success (95% correlation)
        - Phased rollout reduces risk and accelerates adoption
        - Change management investments yield 3x returns
        - Cross-functional teams outperform siloed approaches
        
        The study provides actionable frameworks for AI strategy development and execution 
        roadmaps tailored to different industry verticals.
        """
    )
    article2.evaluation = {
        "engineer": {
            "total_score": 0.65,
            "breakdown": {
                "technical_depth": 0.60,
                "implementation_ready": 0.70,
                "novelty": 0.55
            }
        },
        "business": {
            "total_score": 0.94,
            "breakdown": {
                "business_impact": 0.96,
                "market_potential": 0.92,
                "adoption_timeline": 0.90,
                "roi_potential": 0.98
            }
        }
    }
    articles.append(article2)
    
    # Article 3: Open source development tool
    article3 = Article(
        id="demo-003",
        title="LangChain 2.0: Enhanced Framework for LLM Application Development",
        url="https://github.com/langchain-ai/langchain",
        source="LangChain",
        source_tier=2,
        published_date=datetime.now(),
        content="""
        LangChain has released version 2.0 of its popular framework for building LLM-powered 
        applications. This major update introduces significant architectural improvements and 
        new capabilities for enterprise deployment:
        
        New Features:
        - Streaming API for real-time responses
        - Enhanced memory management for long conversations
        - Built-in observability and debugging tools
        - Improved integration with vector databases
        - Production-ready deployment templates
        
        Developer Experience:
        - Type-safe Python and TypeScript APIs
        - Comprehensive documentation and tutorials
        - Visual chain debugging interface
        - Performance profiling and optimization guides
        
        The framework now supports over 50 LLM providers and includes templates for common 
        use cases like chatbots, document analysis, and code generation. Community adoption 
        has grown to over 500,000 developers globally.
        """
    )
    article3.evaluation = {
        "engineer": {
            "total_score": 0.86,
            "breakdown": {
                "technical_depth": 0.82,
                "implementation_ready": 0.92,
                "community_impact": 0.88,
                "documentation_quality": 0.90
            }
        },
        "business": {
            "total_score": 0.72,
            "breakdown": {
                "business_impact": 0.75,
                "market_potential": 0.70,
                "adoption_timeline": 0.85
            }
        }
    }
    articles.append(article3)
    
    # Article 4: Industry trend analysis
    article4 = Article(
        id="demo-004",
        title="AI Chip Market Reaches $100B: NVIDIA, AMD, and Intel Competition Intensifies",
        url="https://example.com/ai-chip-market-2024",
        source="TechCrunch",
        source_tier=2,
        published_date=datetime.now(),
        content="""
        The AI chip market has reached a historic milestone of $100 billion in annual revenue, 
        driven by surging demand for ML training and inference workloads. Market dynamics show 
        intense competition between major players:
        
        Market Leaders:
        - NVIDIA maintains 80% market share with H100/A100 dominance
        - AMD gains ground with MI300 series competitive pricing
        - Intel re-enters with Gaudi processors and aggressive pricing
        - Custom silicon from Google, Amazon, Meta shows strong performance
        
        Technology Trends:
        - Shift towards specialized AI inference chips
        - Edge computing driving demand for efficient processors
        - Software-hardware co-design becoming competitive advantage
        - Open source alternatives gaining enterprise adoption
        
        Investment continues to pour in, with $50B in new chip development funding announced 
        across the industry. Supply chain constraints remain a limiting factor for growth.
        """
    )
    article4.evaluation = {
        "engineer": {
            "total_score": 0.74,
            "breakdown": {
                "technical_depth": 0.78,
                "market_insight": 0.82,
                "trend_analysis": 0.75
            }
        },
        "business": {
            "total_score": 0.89,
            "breakdown": {
                "business_impact": 0.92,
                "market_potential": 0.95,
                "investment_potential": 0.87,
                "competitive_analysis": 0.88
            }
        }
    }
    articles.append(article4)
    
    # Article 5: Research breakthrough
    article5 = Article(
        id="demo-005",
        title="MIT Breakthrough: Neural Network Learns to Program Itself",
        url="https://news.mit.edu/neural-self-programming-2024",
        source="MIT News",
        source_tier=1,
        published_date=datetime.now(),
        content="""
        MIT researchers have developed a neural network architecture capable of modifying its 
        own code and structure during training. This breakthrough in meta-learning represents 
        a significant step toward truly autonomous AI systems:
        
        Technical Innovation:
        - Self-modifying neural architecture search (SMNAS)
        - Dynamic computation graphs that evolve during training
        - Learned optimization strategies that outperform hand-crafted methods
        - Automatic discovery of novel architectural components
        
        Experimental Results:
        - 40% improvement on few-shot learning benchmarks
        - Discovers architectures that generalize to unseen domains
        - Reduces manual hyperparameter tuning by 90%
        - Achieves human-level performance on abstract reasoning tasks
        
        The research opens new avenues for automated machine learning and could accelerate 
        AI development across domains. Code and datasets will be released under open license.
        """
    )
    article5.evaluation = {
        "engineer": {
            "total_score": 0.96,
            "breakdown": {
                "technical_depth": 0.98,
                "novelty": 0.95,
                "reproducibility": 0.92,
                "scientific_rigor": 0.97
            }
        },
        "business": {
            "total_score": 0.71,
            "breakdown": {
                "business_impact": 0.68,
                "market_potential": 0.75,
                "adoption_timeline": 0.60
            }
        }
    }
    articles.append(article5)
    
    return articles


async def main():
    """Generate demo site."""
    print("🚀 Generating Daily AI News Demo Site...")
    
    try:
        # Create settings
        settings = Settings()
        settings.output_dir = "docs"
        settings.base_url = "https://github.com/user/new-ai-news-site"
        
        # Create articles
        articles = await create_demo_articles()
        print(f"📰 Created {len(articles)} demo articles")
        
        # Generate site
        generator = StaticSiteGenerator(settings)
        
        result = await generator.generate_complete_site(
            articles,
            persona="engineer",
            include_interactive=True,
            include_rss=True,
            include_sitemap=True,
            optimize=True,
            secure=True
        )
        
        print(f"✅ Site generated successfully!")
        print(f"📁 Output directory: {result['output_dir']}")
        print(f"📄 Files generated: {len(result['files_generated'])}")
        print(f"🕐 Generation time: {result['generation_time']}")
        
        # List generated files
        print("\n📋 Generated files:")
        for file in result['files_generated']:
            file_path = Path(result['output_dir']) / file
            size = file_path.stat().st_size if file_path.exists() else 0
            print(f"  - {file} ({size:,} bytes)")
        
        print(f"\n🌐 Open docs/index.html in your browser to view the site")
        
        # Generate persona-specific pages
        print("\n👥 Generating persona-specific pages...")
        persona_results = await generator.generate_persona_specific_pages(articles)
        for persona, path in persona_results.items():
            print(f"  - {persona}.html generated")
        
        print("\n🎉 Demo site generation complete!")
        return True
        
    except Exception as e:
        print(f"❌ Demo site generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)