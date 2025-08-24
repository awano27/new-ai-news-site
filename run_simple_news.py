#!/usr/bin/env python3
"""簡単にAIニュースサイトを生成・表示するスクリプト"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# プロジェクトルートに移動
project_root = Path(__file__).parent
os.chdir(str(project_root))

# srcをパスに追加
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    print("🚀 Daily AI News - 簡単実行スクリプト")
    print("=" * 50)
    
    try:
        # 既存の簡単なコレクションスクリプトを実行
        print("📰 AIニュースを収集中...")
        
        # collect_and_evaluate_simple.py を使用（より軽量で動作確実）
        from collect_and_evaluate_simple import main as simple_main
        
        print("⏳ ニュース収集と評価を開始...")
        success = asyncio.run(simple_main())
        
        if success:
            print("\n✅ サイト生成完了！")
            print("📁 生成場所: docs/index.html")
            
            # docsフォルダの確認
            docs_dir = project_root / "docs"
            if docs_dir.exists():
                files = list(docs_dir.glob("*"))
                print(f"📂 生成されたファイル: {len(files)}個")
                for file in files:
                    print(f"  - {file.name}")
                
                # ブラウザで開く
                index_file = docs_dir / "index.html"
                if index_file.exists():
                    print(f"\n🌐 ブラウザで開いています...")
                    
                    try:
                        # Windowsの場合
                        os.startfile(str(index_file))
                        print("✅ ブラウザが開かれました！")
                    except:
                        try:
                            # その他のOS
                            subprocess.run(["open", str(index_file)], check=False)
                        except:
                            print(f"⚠️ 手動でこのファイルを開いてください: {index_file}")
                    
                    print(f"\n📍 ファイルパス: {index_file.absolute()}")
                    return True
                else:
                    print("❌ index.htmlが見つかりません")
                    return False
            else:
                print("❌ docsフォルダが見つかりません")
                return False
        else:
            print("❌ サイト生成に失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Daily AI Newsサイトが正常に生成されました！")
        print("💡 ヒント: ページのフィルターやペルソナ切替を試してください")
    else:
        print("\n💡 問題が発生した場合は、以下を確認してください:")
        print("  - インターネット接続")
        print("  - Pythonパッケージのインストール状況")
    
    input("\n🔄 Enterを押して終了...")