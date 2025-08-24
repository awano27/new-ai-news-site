#!/usr/bin/env python3
"""毎日実行用X記事統合AIニュース収集システム"""

import os
import sys
import asyncio
from pathlib import Path

# プロジェクト設定
project_root = Path(__file__).parent
os.chdir(str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    print("🌟 Daily AI News - X記事統合版")
    print("通常のRSSフィード + X記事スプレッドシートから収集")
    print("=" * 60)
    print()
    print("🎯 収集ソース:")
    print("  🐦 X記事: Google Spreadsheetsから手動抜粋記事")
    print("  👥 Reddit: MachineLearning, LocalLLaMA")
    print("  📰 英語: MIT Tech Review, VentureBeat, TechCrunch")
    print("  🇯🇵 日本語: ITmedia, Gizmodo, CNET Japan")
    print()
    print("⚡ 2025年最新技術対応:")
    print("  • RAG (Retrieval Augmented Generation)")
    print("  • マルチモーダルAI")
    print("  • AIエージェント")
    print("  • GPT-4/Claude/Gemini最新動向")
    print()
    
    try:
        print("🚀 X記事統合AI情報収集を開始...")
        
        from collect_simple_2025 import main as simple_main
        success = asyncio.run(simple_main())
        
        if success:
            print("\n✅ X記事統合AIニュースサイト生成完了！")
            
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
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 X記事統合AIニュースサイトが正常に完成しました！")
        print("🔥 統合された情報源:")
        print("  🐦 X記事: 最新AI情報とコミュニティ動向")
        print("  📊 RSS記事: 高信頼性メディア・研究機関")
        print("  🌍 多言語: 英語・日本語記事")
        print("  ⚡ 2025年AI技術トレンド完全対応")
        
        print("\n💡 このサイトで得られる情報:")
        print("  🔬 最新AI研究動向")
        print("  💼 AI企業・投資情報")
        print("  🛠️ 実用的AIツール・技術")
        print("  🐦 X/TwitterのAI専門家の洞察")
        print("  🇯🇵 日本のAI業界情報")
        print("  📈 AIビジネストレンド")
    else:
        print("\n⚠️ 実行に問題がありました")
        print("💡 確認事項:")
        print("  • インターネット接続")
        print("  • Python 3.7以上")
        print("  • requests, feedparser パッケージ")
        print("  • Google Spreadsheetsへのアクセス可能性")
        
    input("\nEnterを押して終了...")