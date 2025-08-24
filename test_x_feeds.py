#!/usr/bin/env python3
"""X（旧Twitter）RSSフィードの接続テスト"""

import requests
import feedparser
import time

def test_x_rss_services():
    """XのRSSサービスをテスト"""
    
    # テスト用アカウント
    test_accounts = ["OpenAI", "AnthropicAI", "GoogleAI"]
    
    # 利用可能なRSSサービス
    rss_services = {
        "Nitter.net": "https://nitter.net/{}/rss",
        "TwitRSS.me": "https://twitrss.me/twitter_user_to_rss/?user={}",
        "TwitterRSS.me": "https://twitterrss.me/user/{}/feed", 
        "RSSHub": "https://rsshub.app/twitter/user/{}",
        "RSS Bridge": "https://rss-bridge.org/bridge01/?action=display&bridge=Twitter&context=By+username&u={}&format=Atom"
    }
    
    print("🐦 X（旧Twitter）RSSサービス接続テスト")
    print("=" * 50)
    
    results = {}
    
    for service_name, url_template in rss_services.items():
        print(f"\n🔍 {service_name} をテスト中...")
        results[service_name] = {}
        
        for account in test_accounts:
            try:
                url = url_template.format(account)
                print(f"  📡 テスト: @{account}")
                print(f"    URL: {url[:60]}...")
                
                headers = {
                    'User-Agent': 'DailyAINews/1.0 (Educational Project)',
                    'Accept': 'application/rss+xml, application/xml, text/xml'
                }
                
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    # RSS解析テスト
                    feed = feedparser.parse(response.content)
                    entries_count = len(feed.entries) if hasattr(feed, 'entries') else 0
                    
                    if entries_count > 0:
                        print(f"    ✅ 成功 - エントリー数: {entries_count}")
                        latest = feed.entries[0]
                        print(f"    最新: {latest.title[:50]}..." if hasattr(latest, 'title') else "    最新投稿情報なし")
                        results[service_name][account] = {
                            'status': 'success', 
                            'entries': entries_count, 
                            'latest': getattr(latest, 'title', 'No title')[:50]
                        }
                    else:
                        print(f"    ⚠️ エントリーなし")
                        results[service_name][account] = {'status': 'no_entries', 'entries': 0}
                else:
                    print(f"    ❌ HTTP {response.status_code}")
                    results[service_name][account] = {'status': 'http_error', 'code': response.status_code}
                    
            except Exception as e:
                print(f"    ❌ エラー: {str(e)[:60]}")
                results[service_name][account] = {'status': 'error', 'error': str(e)[:60]}
            
            time.sleep(2)  # レート制限回避
    
    # 結果サマリー
    print(f"\n📊 結果サマリー:")
    print("=" * 50)
    
    best_services = []
    
    for service_name, service_results in results.items():
        success_count = sum(1 for result in service_results.values() if result.get('status') == 'success')
        total_count = len(service_results)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        status_icon = "✅" if success_count > 0 else "❌"
        print(f"{status_icon} {service_name}: {success_count}/{total_count} ({success_rate:.0f}%)")
        
        if success_count > 0:
            best_services.append((service_name, success_count, success_rate))
    
    # 推奨サービス
    if best_services:
        best_services.sort(key=lambda x: x[2], reverse=True)  # 成功率でソート
        
        print(f"\n🎯 推奨RSSサービス:")
        for service_name, success_count, rate in best_services[:3]:
            print(f"  1️⃣ {service_name} - 成功率 {rate:.0f}%")
        
        print(f"\n💡 X投稿収集に使用できるサービスが見つかりました！")
        print(f"実行コマンド: python collect_x_posts.py")
    else:
        print(f"\n⚠️ 現在利用可能なXのRSSサービスがありません")
        print(f"代替案:")
        print(f"  • 公式Twitter API v2の使用")
        print(f"  • Selenium等でのスクレイピング")
        print(f"  • 手動でのツイート収集")
    
    return results

def test_specific_feeds():
    """特定のXフィードをテスト"""
    
    specific_feeds = {
        "OpenAI Nitter": "https://nitter.net/OpenAI/rss",
        "Anthropic TwitRSS": "https://twitrss.me/twitter_user_to_rss/?user=AnthropicAI",
        "AI Hashtag Search": "https://twitrss.me/twitter_search_to_rss/?term=%23AI%20OR%20%23MachineLearning"
    }
    
    print(f"\n🎯 特定フィード詳細テスト:")
    print("-" * 30)
    
    for name, url in specific_feeds.items():
        print(f"\n📡 テスト: {name}")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, timeout=15)
            print(f"ステータス: {response.status_code}")
            
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                entries = len(feed.entries) if hasattr(feed, 'entries') else 0
                
                if entries > 0:
                    print(f"✅ 成功 - {entries}個の投稿")
                    
                    # 最新3件表示
                    for i, entry in enumerate(feed.entries[:3]):
                        print(f"  {i+1}. {getattr(entry, 'title', 'タイトルなし')[:60]}...")
                else:
                    print(f"⚠️ 投稿なし")
            else:
                print(f"❌ 失敗")
                
        except Exception as e:
            print(f"❌ エラー: {str(e)[:80]}")

if __name__ == "__main__":
    print("🐦 X（旧Twitter）RSS収集テスト")
    
    try:
        # 基本的なRSSサービステスト
        results = test_x_rss_services()
        
        # 特定フィードの詳細テスト
        test_specific_feeds()
        
        print(f"\n🔧 テスト完了")
        print(f"利用可能なサービスがあれば、X投稿収集を実行できます")
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
    
    input("\nEnterを押して終了...")