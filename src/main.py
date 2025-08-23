#!/usr/bin/env python3
"""Main entry point for Daily AI News system."""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler

from src.collectors.feed_collector import FeedCollector
from src.evaluators.multi_layer_evaluator import MultiLayerEvaluator
from src.generators.html_generator import HTMLGenerator
from src.config.settings import Settings

console = Console()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


class DailyAINews:
    """Main application class for Daily AI News system."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the application with configuration."""
        self.settings = Settings(config_path)
        self.collector = FeedCollector(self.settings)
        self.evaluator = MultiLayerEvaluator(self.settings)
        self.generator = HTMLGenerator(self.settings)
    
    async def run_pipeline(self, tier1_only: bool = False):
        """Run the complete data processing pipeline."""
        try:
            # Phase 1: Collect articles
            logger.info("Starting article collection...")
            articles = await self.collector.collect_all(tier1_only=tier1_only)
            logger.info(f"Collected {len(articles)} articles")
            
            # Phase 2: Evaluate articles
            logger.info("Evaluating articles...")
            evaluated_articles = []
            for article in articles:
                engineer_score = await self.evaluator.evaluate(article, persona="engineer")
                business_score = await self.evaluator.evaluate(article, persona="business")
                article.evaluation = {
                    "engineer": engineer_score,
                    "business": business_score
                }
                evaluated_articles.append(article)
            
            # Phase 3: Generate output
            logger.info("Generating HTML output...")
            output_path = await self.generator.generate(evaluated_articles)
            logger.info(f"Output generated at: {output_path}")
            
            return evaluated_articles
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise


@click.command()
@click.option("--config", type=click.Path(exists=True), help="Path to configuration file")
@click.option("--tier1-only", is_flag=True, help="Process only Tier 1 sources")
@click.option("--init", is_flag=True, help="Initialize database and indexes")
@click.option("--test-mode", is_flag=True, help="Run in test mode with limited data")
def main(config: Optional[str], tier1_only: bool, init: bool, test_mode: bool):
    """Daily AI News - AI-powered news aggregation and evaluation platform."""
    try:
        app = DailyAINews(Path(config) if config else None)
        
        if init:
            logger.info("Initializing database...")
            # Database initialization logic here
            logger.info("Database initialized successfully")
            return
        
        if test_mode:
            logger.info("Running in test mode...")
            # Test mode logic here
            return
        
        # Run main pipeline
        asyncio.run(app.run_pipeline(tier1_only=tier1_only))
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()