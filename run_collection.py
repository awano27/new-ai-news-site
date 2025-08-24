#!/usr/bin/env python3
"""Simple runner for collection system"""
import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from collect_simple_2025 import main

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        print(f"\n✅ Collection completed successfully: {result}")
    except Exception as e:
        print(f"\n❌ Collection failed: {e}")
        import traceback
        traceback.print_exc()