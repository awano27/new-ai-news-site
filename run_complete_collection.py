#!/usr/bin/env python3
"""完全なソースコレクション実行スクリプト（日本語ソース含む）"""

import os
import sys
import asyncio
from pathlib import Path

# プロジェクトルートに移動
project_root = Path(__file__).parent
os.chdir(str(project_root))

# srcをパスに追加
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print("🌐 Daily AI News - 完全ソースコレクション")
print("=" * 50)
print("📌 日本語ソース含む全44+ソースから収集します")
print()

try:
    # collect_complete.py をインポートして実行
    from collect_complete import main as complete_main
    
    print("🚀 完全なニュース収集を開始...")
    success = asyncio.run(complete_main())
    
    if success:
        print("\n✅ 日本語情報を含む完全なサイト生成が完了しました！")
        print("📂 場所: docs/index.html")
        
        # ブラウザで開く
        docs_dir = project_root / "docs"
        index_file = docs_dir / "index.html"
        
        if index_file.exists():
            try:
                os.startfile(str(index_file))
                print("🌐 ブラウザが開かれました！")
            except:
                print(f"⚠️ 手動でこのファイルを開いてください: {index_file}")
        
        # 収集された情報の概要を表示
        print("\n📊 収集概要:")
        print("  • Tier 1ソース: 研究・技術、ビジネス、日本語メディア")
        print("  • Tier 2ソース: 開発者コミュニティ、テックメディア")
        print("  • 評価システム: エンジニア・ビジネス視点の双方")
        print("  • フィルタリング: ソース別、スコア別、難易度別")
        
        return True
    else:
        print("❌ サイト生成に失敗しました")
        return False
        
except ModuleNotFoundError as e:
    print(f"⚠️ モジュールエラー: {e}")
    print("💡 簡単なバージョンを実行します...")
    
    try:
        from collect_and_evaluate_simple import main as simple_main
        success = asyncio.run(simple_main())
        
        if success:
            print("✅ 簡単版のサイト生成が完了しました")
            return True
    except Exception as simple_error:
        print(f"❌ 簡単版も失敗: {simple_error}")
        return False
    
except Exception as e:
    print(f"❌ エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()
    return False

if __name__ == "__main__":
    print("🔄 実行中...")
    
    try:
        success = asyncio.run(main())
    except Exception as e:
        print(f"❌ 実行エラー: {e}")
        success = False
    
    if success:
        print("\n🎉 完了！日本語情報を含むAIニュースサイトが更新されました")
    else:
        print("\n⚠️ 実行に問題がありました")
        print("💡 代替案:")
        print("  1. インターネット接続を確認")
        print("  2. 既存のdocs/index.htmlを直接開く") 
        print("  3. collect_and_evaluate_simple.py を直接実行")
    
    input("\nEnterを押して終了...")