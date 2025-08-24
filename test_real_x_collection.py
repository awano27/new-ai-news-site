#!/usr/bin/env python3
"""Test real X article collection"""
import sys
from pathlib import Path
import requests
import csv
from io import StringIO

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from x_source_collector import XSourceCollector

def test_real_collection():
    """Test collection of real X articles"""
    print("🔍 Google SpreadsheetからX記事を取得テスト...")
    
    # Test direct CSV access
    csv_url = "https://docs.google.com/spreadsheets/d/1uuLKCLIJw--a1vCcO6UGxSpBiLTtN8uGl2cdMb6wcfg/export?format=csv&gid=0"
    
    try:
        print(f"📡 アクセス中: {csv_url}")
        response = requests.get(csv_url, timeout=15)
        print(f"📊 レスポンス: {response.status_code}")
        
        if response.status_code == 200:
            # Parse CSV
            csv_content = response.text
            print(f"📄 CSVサイズ: {len(csv_content)} 文字")
            
            reader = csv.DictReader(StringIO(csv_content))
            articles = list(reader)
            print(f"📰 記事数: {len(articles)}")
            
            # Show first few articles
            for i, article in enumerate(articles[:5]):
                print(f"\n記事 {i+1}:")
                print(f"  ユーザー: {article.get('username', 'N/A')}")
                print(f"  内容: {article.get('content', 'N/A')[:100]}...")
                print(f"  日付: {article.get('created_at', 'N/A')}")
        
        # Test with XSourceCollector
        print("\n🤖 XSourceCollectorでテスト...")
        collector = XSourceCollector()
        x_articles = collector.parse_x_articles()
        
        if x_articles:
            print(f"✅ {len(x_articles)}件のX記事を取得")
            for i, article in enumerate(x_articles[:3]):
                print(f"\n記事 {i+1}: {article.title[:50]}...")
                print(f"  ソース: {article.source}")
                print(f"  スコア: {article.evaluation}")
        else:
            print("❌ X記事を取得できませんでした")
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_collection()