#!/usr/bin/env python3
"""日本語AIニュース + X投稿統合版の簡単実行"""

import os
import sys
import asyncio
from pathlib import Path

# プロジェクト設定
project_root = Path(__file__).parent
os.chdir(str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    print("🚀 Daily AI News - 統合版（日本語 + X投稿）")
    print("=" * 60)
    
    try:
        # 1. X RSSサービステスト
        print("1️⃣ X（旧Twitter）RSSサービステスト中...")
        from test_x_feeds import test_x_rss_services
        x_results = test_x_rss_services()
        
        # 利用可能なXサービス数をカウント
        x_services_available = sum(1 for service_results in x_results.values() 
                                  if any(result.get('status') == 'success' for result in service_results.values()))
        
        print(f"✅ {x_services_available}個のXサービスが利用可能")
        
        # 2. 統合収集・サイト生成実行
        print("\n2️⃣ 統合ニュース収集・サイト生成中...")
        from collect_x_posts import main as collect_main
        
        success = asyncio.run(collect_main())
        
        if success:
            print("\n✅ 統合AIニュースサイト生成完了！")
            print("📱 X投稿と📰日本語記事が統合されています")
            
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
        print("\n🎉 統合AIニュースサイトが正常に生成されました！")
        print("💡 機能:")
        print("  📰 日本語AIニュース記事")
        print("  📱 X（旧Twitter）のAI関連投稿")
        print("  🔍 統合検索・フィルタリング")
        print("  👤 エンジニア・ビジネス視点切替")
    else:
        print("\n⚠️ 実行に問題がありました")
        print("💡 代替実行:")
        print("  • python collect_japanese_sources.py  # 日本語のみ")
        print("  • python collect_x_posts.py          # 統合版")
        
    input("\nEnterを押して終了...")