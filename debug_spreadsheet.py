#!/usr/bin/env python3
"""
Google Spreadsheetsアクセスの詳細デバッグツール
"""

import requests
import sys
from datetime import datetime

def debug_spreadsheet_access():
    """スプレッドシートアクセスの詳細デバッグ"""
    
    spreadsheet_id = "1uuLKCLIJw--a1vCcO6UGxSpBiLTtN8uGl2cdMb6wcfg"
    
    # 様々なエンドポイントとヘッダーでテスト
    test_configs = [
        {
            "name": "標準CSV export",
            "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid=0",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        },
        {
            "name": "gviz API",
            "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&gid=0",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        },
        {
            "name": "シンプル export",
            "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        },
        {
            "name": "pub パラメータ付き",
            "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid=0&single=true&output=csv",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
    ]
    
    print("=" * 80)
    print("Google Spreadsheetsアクセス詳細デバッグ")
    print("=" * 80)
    print(f"対象スプレッドシート ID: {spreadsheet_id}")
    print(f"テスト時刻: {datetime.now()}")
    print()
    
    for i, config in enumerate(test_configs, 1):
        print(f"🔍 テスト {i}: {config['name']}")
        print(f"   URL: {config['url']}")
        print(f"   Headers: {config['headers']}")
        
        try:
            response = requests.get(
                config['url'], 
                headers=config['headers'], 
                timeout=15, 
                allow_redirects=True
            )
            
            print(f"   ✅ ステータス: {response.status_code}")
            print(f"   📊 Content-Length: {len(response.content)} bytes")
            print(f"   📝 Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 200:
                # コンテンツの最初の200文字を表示
                content_preview = response.text[:200].replace('\n', '\\n').replace('\r', '\\r')
                print(f"   👀 内容プレビュー: {content_preview}...")
                
                # エンコーディング検出
                encoding = response.encoding or 'utf-8'
                print(f"   🔤 検出エンコーディング: {encoding}")
                
                # 行数カウント
                lines = response.text.split('\n')
                print(f"   📏 行数: {len(lines)}")
                
                if len(lines) > 1:
                    print(f"   📋 最初の行: {lines[0][:100]}...")
                    if len(lines) > 2:
                        print(f"   📋 2行目: {lines[1][:100]}...")
                
                # 文字化け検出
                if '�' in response.text or 'Ã' in response.text:
                    print("   ⚠️ 文字化けが検出されました")
                    
                    # 異なるエンコーディングで試行
                    encodings_to_try = ['utf-8', 'shift-jis', 'euc-jp', 'iso-2022-jp', 'cp932']
                    for enc in encodings_to_try:
                        try:
                            decoded_content = response.content.decode(enc)
                            if '�' not in decoded_content[:200]:
                                print(f"   💡 {enc}でのデコードが成功: {decoded_content[:100]}...")
                                break
                        except:
                            continue
                
            else:
                print(f"   ❌ エラーレスポンス: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ リクエストエラー: {str(e)}")
        except Exception as e:
            print(f"   ❌ その他エラー: {str(e)}")
        
        print("-" * 60)
        print()
    
    # 追加の診断情報
    print("🔧 追加診断情報:")
    print(f"   • Python version: {sys.version}")
    print(f"   • requests version: {requests.__version__}")
    
    # 手動での確認方法を案内
    print()
    print("💡 手動確認方法:")
    print("1. ブラウザで以下のURLにアクセスしてください:")
    print(f"   https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid=0")
    print("2. 「ファイル」→「共有」→「リンクを知っている全員」に設定")
    print("3. 「ファイル」→「ダウンロード」→「カンマ区切り値(.csv)」")
    print("4. ダウンロードしたファイルの内容を確認")
    print()

if __name__ == "__main__":
    debug_spreadsheet_access()