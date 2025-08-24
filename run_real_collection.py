#!/usr/bin/env python3
"""Run real data collection from Google Spreadsheet"""
import sys
import subprocess
import os
from pathlib import Path

def main():
    print("🔄 実際のGoogle SpreadsheetからX記事を収集中...")
    
    # Change to project directory
    os.chdir(r'C:\Users\yoshitaka\new-ai-news-site')
    
    try:
        # Run the collection script
        result = subprocess.run([
            sys.executable, 'collect_simple_2025.py'
        ], capture_output=True, text=True, timeout=120)
        
        print("=== 収集結果 ===")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        print(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("\n✅ 実際のX記事データでHTMLが更新されました！")
            print("ブラウザをリフレッシュしてください。")
        else:
            print("\n❌ 収集でエラーが発生しました。")
            
    except subprocess.TimeoutExpired:
        print("⏱️ 収集がタイムアウトしました（120秒）")
    except Exception as e:
        print(f"❌ 実行エラー: {e}")

if __name__ == "__main__":
    main()
    input("\nEnterキーを押して終了...")