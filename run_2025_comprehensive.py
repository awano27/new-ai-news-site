#!/usr/bin/env python3
"""2025年完全対応AI情報収集システム - 簡単実行"""

import os
import sys
import asyncio
from pathlib import Path

# プロジェクト設定
project_root = Path(__file__).parent
os.chdir(str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    print("🌟 Daily AI News - 2025年完全対応版")
    print("「要件追加.txt」に基づく最高品質AI情報収集")
    print("=" * 70)
    print()
    print("🎯 収集予定ソース:")
    print("  🎓 研究: arXiv AI論文、BAIR Blog、MIT AI")
    print("  👥 コミュニティ: Reddit ML、LocalLLaMA、DeepLearning")
    print("  📰 英語メディア: MIT Tech Review、VentureBeat、TechCrunch")
    print("  🇯🇵 日本メディア: ITmedia AI+、日経xTECH、CNET Japan")
    print("  📧 ニュースレター: Import AI、Ahead of AI")
    print("  📺 動画/音声: Two Minute Papers、Lex Fridman Podcast")
    print()
    print("⚡ 2025年最新技術:")
    print("  • RAG（Retrieval Augmented Generation）")
    print("  • マルチモーダルAI")
    print("  • AIエージェント")
    print("  • ファインチューニング最新手法")
    print("  • GPT-4、Claude、Gemini最新動向")
    print()
    
    try:
        print("🚀 包括的AI情報収集を開始...")
        
        from collect_comprehensive_2025 import main as comprehensive_main
        success = asyncio.run(comprehensive_main())
        
        if success:
            print("\n✅ 2025年対応AIニュースサイト生成完了！")
            
            # ブラウザで開く
            index_file = project_root / "docs" / "index.html"
            if index_file.exists():
                try:
                    os.startfile(str(index_file))
                    print("🌐 ブラウザが開かれました")
                except:
                    print(f"📂 ファイル場所: {index_file}")
            
            print("\n🌟 完成したサイトの特徴:")
            print("  📊 信頼性★1-5段階評価")
            print("  🎯 50+高品質ソース")
            print("  🔍 2025年最新AIキーワード対応")
            print("  ⚡ レート制限・エンコーディング完全対応")
            print("  🌍 日本語・英語両対応")
            print("  🏆 エンジニア・ビジネス両視点評価")
            
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
        print("\n🎉 2025年最新対応AIニュースサイトが正常に完成しました！")
        print("💡 このサイトには以下の最新情報が含まれます:")
        print("  🔬 最新AI研究論文（arXiv）")
        print("  💼 AI企業の発表・動向")
        print("  🛠️ 実用的なAI技術・ツール")
        print("  📈 AIビジネス・投資情報")
        print("  🇯🇵 日本のAI業界動向")
        print("  📚 学習リソース・チュートリアル")
        print()
        print("🔧 サイト機能:")
        print("  • エンジニア・ビジネス視点切替")
        print("  • 信頼性フィルタリング")
        print("  • カテゴリ別絞り込み")
        print("  • キーワード検索")
        print("  • 実装難易度表示")
        print("  • ブックマーク機能")
    else:
        print("\n⚠️ 実行に問題がありました")
        print("💡 代替コマンド:")
        print("  python collect_enhanced_sources.py     # 基本版")
        print("  python collect_japanese_sources.py     # 日本語特化")
        
    input("\nEnterを押して終了...")