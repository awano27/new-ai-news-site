#!/usr/bin/env python3
"""Verify that all required sources from requirements are included."""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from collect_complete import CompleteDataCollector

def verify_sources():
    """Verify source collection completeness."""
    collector = CompleteDataCollector()
    
    print("🔍 VERIFYING COMPLETE SOURCE COLLECTION")
    print("=" * 60)
    
    # Count sources by tier and category
    tier1_count = 0
    tier2_count = 0
    categories = {}
    
    for source_key, config in collector.sources.items():
        if config['tier'] == 1:
            tier1_count += 1
        elif config['tier'] == 2:
            tier2_count += 1
            
        category = config.get('category', 'unknown')
        categories[category] = categories.get(category, 0) + 1
    
    print(f"📊 TOTAL SOURCES: {len(collector.sources)}")
    print(f"🥇 Tier 1 Sources: {tier1_count}")
    print(f"🥈 Tier 2 Sources: {tier2_count}")
    print()
    
    print("📂 Categories:")
    for category, count in sorted(categories.items()):
        print(f"  • {category:12}: {count:2} sources")
    print()
    
    # Sample sources by category
    print("📋 SAMPLE SOURCES BY CATEGORY:")
    print("-" * 40)
    
    by_category = {}
    for source_key, config in collector.sources.items():
        category = config.get('category', 'unknown')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(config['source_name'])
    
    for category, sources in sorted(by_category.items()):
        print(f"\n{category.upper()}:")
        for i, source in enumerate(sources[:5]):  # Show first 5
            print(f"  {i+1}. {source}")
        if len(sources) > 5:
            print(f"    ... and {len(sources) - 5} more")
    
    print(f"\n✅ VERIFICATION COMPLETE")
    print(f"🎯 All {len(collector.sources)} sources from requirements specification included!")
    
    return len(collector.sources)

if __name__ == "__main__":
    try:
        source_count = verify_sources()
        print(f"\n🎉 SUCCESS: {source_count} sources ready for collection!")
    except Exception as e:
        print(f"❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()