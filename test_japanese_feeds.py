#!/usr/bin/env python3
"""日本語フィードの接続テスト"""

import requests
import feedparser

def test_japanese_feeds():
    """日本語フィードのアクセステスト"""
    
    feeds = {
        "ITmedia AI": "https://rss.itmedia.co.jp/rss/2.0/ait.xml",
        "ITmedia テクノロジー": "https://rss.itmedia.co.jp/rss/2.0/news_technology.xml",
        "PC Watch": "https://pc.watch.impress.co.jp/data/rss/1.0/pcw/feed.rdf",
        "INTERNET Watch": "https://internet.watch.impress.co.jp/data/rss/1.0/iw/feed.rdf",
        "CNET Japan": "https://feeds.japan.cnet.com/rss/cnet/all.rdf",
        "Gizmodo Japan": "https://www.gizmodo.jp/index.xml",
        "TechCrunch Japan": "https://jp.techcrunch.com/feed/",
        "マイナビテック+": "https://news.mynavi.jp/rss/techplus"
    }
    
    print("🔍 日本語フィードアクセステスト")
    print("=" * 40)
    
    results = {}
    
    for name, url in feeds.items():
        try:
            print(f"\n📡 テスト中: {name}")
            print(f"URL: {url}")
            
            headers = {
                'User-Agent': 'DailyAINews/1.0 (Educational Project)',
                'Accept': 'application/rss+xml, application/xml'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"ステータス: {response.status_code}")
            
            if response.status_code == 200:
                # フィード解析テスト
                feed = feedparser.parse(response.content)
                entries_count = len(feed.entries) if hasattr(feed, 'entries') else 0
                
                print(f"✅ 成功 - エントリー数: {entries_count}")
                
                if entries_count > 0:
                    latest = feed.entries[0]
                    print(f"最新記事: {latest.title[:50]}...")
                    results[name] = {'status': 'success', 'entries': entries_count, 'latest': latest.title}
                else:
                    results[name] = {'status': 'no_entries', 'entries': 0}
            else:
                print(f"❌ HTTPエラー: {response.status_code}")
                results[name] = {'status': 'http_error', 'code': response.status_code}
                
        except Exception as e:
            print(f"❌ エラー: {str(e)[:100]}")
            results[name] = {'status': 'error', 'error': str(e)[:100]}
    
    print(f"\n📊 結果サマリー:")
    print("-" * 30)
    
    success_count = 0
    for name, result in results.items():
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_icon} {name}: {result['status']}")
        if result['status'] == 'success':
            success_count += 1
    
    print(f"\n📈 成功率: {success_count}/{len(feeds)} ({success_count/len(feeds)*100:.0f}%)")
    
    return results

if __name__ == "__main__":
    print("🇯🇵 日本語AIニュースフィード接続テスト")
    
    try:
        results = test_japanese_feeds()
        
        # 利用可能なソースをレポート
        available = [name for name, result in results.items() if result['status'] == 'success']
        
        if available:
            print(f"\n✅ 利用可能な日本語ソース: {len(available)}個")
            for name in available:
                print(f"  • {name}")
            
            print(f"\n💡 これらのソースから日本語記事を収集できます！")
            print(f"実行コマンド: python collect_japanese_sources.py")
        else:
            print(f"\n⚠️ 現在利用可能な日本語ソースがありません")
            print(f"ネットワーク接続またはフィードURLを確認してください")
            
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
    
    input("\nEnterを押して終了...")