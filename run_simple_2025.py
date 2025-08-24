#!/usr/bin/env python3
"""2025年対応簡単版AI情報収集 - 依存関係なし実行"""

import os
import sys
import asyncio
from pathlib import Path

# プロジェクト設定
project_root = Path(__file__).parent
os.chdir(str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    print("⚡ Daily AI News - 2025年簡単版")
    print("標準ライブラリのみで動作（依存関係なし）")
    print("=" * 50)
    print()
    print("🎯 収集ソース:")
    print("  👥 Reddit: MachineLearning, LocalLLaMA")
    print("  📰 英語: MIT Tech Review, VentureBeat, TechCrunch, The Verge")
    print("  🇯🇵 日本語: ITmedia, INTERNET Watch, Gizmodo, CNET")
    print("  📧 ニュースレター: Import AI")
    print()
    print("🔍 2025年最新キーワード対応:")
    print("  • RAG (Retrieval Augmented Generation)")
    print("  • マルチモーダルAI")
    print("  • AIエージェント")
    print("  • GPT-4/Claude/Gemini最新動向")
    print()
    
    try:
        print("🚀 簡単版AI情報収集を開始...")
        
        from collect_simple_2025 import main as simple_main
        success = asyncio.run(simple_main())
        
        if success:
            print("\n✅ 2025年簡単版AIニュースサイト生成完了！")
            
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
        print("\n🎉 2025年簡単版AIニュースサイトが正常に完成しました！")
        print("⚡ 利点:")
        print("  📦 追加のライブラリインストール不要")
        print("  🔍 2025年最新AIトレンド対応")
        print("  🌍 日本語・英語記事を自動収集")
        print("  📊 高品質ソース厳選")
        print("  🚀 高速動作")
        
        print("\n💡 このサイトで得られる情報:")
        print("  🔬 最新AI研究動向")
        print("  💼 AI企業・投資情報")
        print("  🛠️ 実用的AIツール・技術")
        print("  🇯🇵 日本のAI業界情報")
        print("  📈 AIビジネストレンド")
    else:
        print("\n⚠️ 実行に問題がありました")
        print("💡 確認事項:")
        print("  • インターネット接続")
        print("  • Python 3.7以上")
        print("  • requests, feedparser パッケージ")
        
    input("\nEnterを押して終了...")