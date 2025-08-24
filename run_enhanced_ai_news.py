#!/usr/bin/env python3
"""拡張AIニュースの簡単実行"""

import os
import sys
import asyncio
from pathlib import Path

# プロジェクト設定
project_root = Path(__file__).parent
os.chdir(str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    print("🚀 Daily AI News - 拡張版")
    print("X（旧Twitter）の代替として40+ソースから収集")
    print("=" * 60)
    
    try:
        print("📊 拡張AIニュース収集・サイト生成を開始...")
        
        from collect_enhanced_sources import main as enhanced_main
        success = asyncio.run(enhanced_main())
        
        if success:
            print("\n✅ 拡張AIニュースサイト生成完了！")
            
            # ブラウザで開く
            index_file = project_root / "docs" / "index.html"
            if index_file.exists():
                try:
                    os.startfile(str(index_file))
                    print("🌐 ブラウザが開かれました")
                except:
                    print(f"📂 ファイル場所: {index_file}")
            
            print("\n🎯 収集されたソース:")
            print("  🏢 AI企業: OpenAI, Anthropic, DeepMind, Google AI")
            print("  🎓 研究機関: MIT CSAIL, Stanford HAI, arXiv")
            print("  📰 英語メディア: MIT Tech Review, VentureBeat, TechCrunch")
            print("  🇯🇵 日本語メディア: ITmedia, Gizmodo, CNET Japan")
            print("  👥 コミュニティ: Hacker News, Reddit ML, Towards DS")
            
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
        print("\n🎉 拡張AIニュースサイトが正常に生成されました！")
        print("💡 X（旧Twitter）が使えなくても、40+ソースから最新情報を取得")
        print("🔧 機能:")
        print("  • 日本語・英語の多言語対応")
        print("  • AI企業・研究機関・メディアを網羅")
        print("  • 強化されたAI関連フィルタリング")
        print("  • エンジニア・ビジネス両視点の評価")
    else:
        print("\n⚠️ 実行に問題がありました")
        print("💡 代替コマンド:")
        print("  python collect_japanese_sources.py  # 日本語のみ")
        
    input("\nEnterを押して終了...")