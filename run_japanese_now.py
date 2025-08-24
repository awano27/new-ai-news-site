#!/usr/bin/env python3
"""日本語AIニュースを今すぐ収集・表示"""

import os
import sys
import asyncio
from pathlib import Path

# プロジェクトルート設定
project_root = Path(__file__).parent
os.chdir(str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    print("🚀 日本語AIニュース - 即座実行")
    print("=" * 40)
    
    try:
        # フィードテスト実行
        print("1️⃣ 日本語フィード接続テスト中...")
        from test_japanese_feeds import test_japanese_feeds
        results = test_japanese_feeds()
        
        # 成功したソース数をカウント
        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        
        if success_count == 0:
            print("❌ 利用可能な日本語フィードがありません")
            return False
        
        print(f"✅ {success_count}個の日本語フィードが利用可能です")
        
        # 日本語ニュース収集実行
        print("\n2️⃣ 日本語ニュース収集・サイト生成中...")
        from collect_japanese_sources import main as collect_main
        
        success = asyncio.run(collect_main())
        
        if success:
            print("\n✅ 日本語AIニュースサイト生成完了！")
            
            # ブラウザで開く
            index_file = project_root / "docs" / "index.html"
            if index_file.exists():
                try:
                    os.startfile(str(index_file))
                    print("🌐 ブラウザが開かれました")
                except:
                    print(f"📂 ファイル場所: {index_file}")
                    
            return True
        else:
            print("❌ サイト生成に失敗")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎌 日本語AIニュースを正常に生成しました！")
        print("💡 ページ内のフィルタやペルソナ切替をお試しください")
    else:
        print("\n⚠️ 実行に問題がありました")
        print("💡 手動実行: python collect_japanese_sources.py")
        
    input("\nEnterを押して終了...")