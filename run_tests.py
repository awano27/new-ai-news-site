#!/usr/bin/env python3
"""Simple test runner for development."""

import sys
import subprocess
from pathlib import Path

def main():
    """Run tests and display results."""
    print("🧪 Daily AI News - Test Runner")
    print("=" * 50)
    
    # Add src to path
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Try to import and run basic functionality tests
        print("📋 Testing imports...")
        
        # Test basic imports
        from src.config.settings import Settings
        print("✅ Settings import successful")
        
        from src.models.article import Article
        print("✅ Article model import successful")
        
        from src.evaluators.multi_layer_evaluator import MultiLayerEvaluator
        print("✅ MultiLayerEvaluator import successful")
        
        from src.collectors.feed_collector import FeedCollector
        print("✅ FeedCollector import successful")
        
        # Test basic instantiation
        print("\n📋 Testing basic instantiation...")
        settings = Settings()
        print("✅ Settings created")
        
        evaluator = MultiLayerEvaluator(settings)
        print("✅ MultiLayerEvaluator created")
        
        collector = FeedCollector(settings)
        print("✅ FeedCollector created")
        
        # Test basic article evaluation
        print("\n📋 Testing evaluation system...")
        
        # Create a test article
        from datetime import datetime
        from src.models.article import TechnicalMetadata, BusinessMetadata
        
        test_article = Article(
            id="test-001",
            title="Test AI Article: Revolutionary Machine Learning Breakthrough",
            url="https://example.com/test",
            source="Test Source",
            source_tier=1,
            published_date=datetime.now(),
            content="This is a test article about machine learning and AI research. " * 20,
            technical=TechnicalMetadata(implementation_ready=True, code_available=True),
            business=BusinessMetadata(market_size="$1B", growth_rate=25.0)
        )
        
        print("✅ Test article created")
        
        # Test evaluation (synchronous version for testing)
        import asyncio
        
        async def test_evaluation():
            engineer_result = await evaluator.evaluate(test_article, "engineer")
            business_result = await evaluator.evaluate(test_article, "business")
            return engineer_result, business_result
        
        engineer_eval, business_eval = asyncio.run(test_evaluation())
        
        print(f"✅ Engineer evaluation: {engineer_eval['total_score']:.3f}")
        print(f"✅ Business evaluation: {business_eval['total_score']:.3f}")
        print(f"✅ Engineer recommendation: {engineer_eval['recommendation']}")
        print(f"✅ Business recommendation: {business_eval['recommendation']}")
        
        print("\n" + "=" * 50)
        print("🎉 All basic tests passed!")
        
        # Display evaluation breakdown
        print("\n📊 Evaluation Breakdown (Engineer):")
        for key, value in engineer_eval['breakdown'].items():
            print(f"  {key}: {value:.3f}")
        
        print("\n📊 Evaluation Breakdown (Business):")
        for key, value in business_eval['breakdown'].items():
            print(f"  {key}: {value:.3f}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)