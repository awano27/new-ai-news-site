#!/usr/bin/env python3
"""Test runner for complete collection system."""

import os
import sys
from pathlib import Path

# Set working directory
project_root = Path(__file__).parent
os.chdir(str(project_root))

# Add src to path
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    print("🔄 Starting complete collection test...")
    try:
        # Import and run the main collection
        from collect_complete import main
        import asyncio
        
        success = asyncio.run(main())
        
        if success:
            print("\n✅ Complete collection test PASSED!")
        else:
            print("\n❌ Complete collection test FAILED!")
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()