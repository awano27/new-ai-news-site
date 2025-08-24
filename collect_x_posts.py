#!/usr/bin/env python3
"""X（旧Twitter）のAI関連ポストを収集"""

import sys
import asyncio
import requests
import feedparser
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import re
import json
from urllib.parse import quote_plus

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import Settings
from src.models.article import Article, TechnicalMetadata, BusinessMetadata, ImplementationCost
from src.generators.static_site_generator import StaticSiteGenerator

class XPostCollector:
    """X（旧Twitter）のAI関連ポスト収集"""
    
    def __init__(self):
        # RSS形式でアクセス可能なXアカウント
        self.x_sources = {
            # AI企業・研究機関の公式アカウント
            "openai": {
                "url": "https://nitter.net/OpenAI/rss",
                "backup_url": "https://twitrss.me/twitter_user_to_rss/?user=OpenAI",
                "tier": 1,
                "source_name": "OpenAI (X)",
                "category": "ai_company",
                "account": "@OpenAI"
            },
            "anthropic": {
                "url": "https://nitter.net/AnthropicAI/rss", 
                "backup_url": "https://twitrss.me/twitter_user_to_rss/?user=AnthropicAI",
                "tier": 1,
                "source_name": "Anthropic (X)",
                "category": "ai_company",
                "account": "@AnthropicAI"
            },
            "google_ai": {
                "url": "https://nitter.net/GoogleAI/rss",
                "backup_url": "https://twitrss.me/twitter_user_to_rss/?user=GoogleAI",
                "tier": 1,
                "source_name": "Google AI (X)",
                "category": "ai_company", 
                "account": "@GoogleAI"
            },
            "deepmind": {
                "url": "https://nitter.net/DeepMind/rss",
                "backup_url": "https://twitrss.me/twitter_user_to_rss/?user=DeepMind",
                "tier": 1,
                "source_name": "DeepMind (X)",
                "category": "ai_company",
                "account": "@DeepMind"
            },
            # AI研究者・インフルエンサー
            "ylecun": {
                "url": "https://nitter.net/ylecun/rss",
                "backup_url": "https://twitrss.me/twitter_user_to_rss/?user=ylecun",
                "tier": 1,
                "source_name": "Yann LeCun (X)",
                "category": "ai_researcher",
                "account": "@ylecun"
            },
            "karpathy": {
                "url": "https://nitter.net/karpathy/rss",
                "backup_url": "https://twitrss.me/twitter_user_to_rss/?user=karpathy",
                "tier": 1,
                "source_name": "Andrej Karpathy (X)",
                "category": "ai_researcher",
                "account": "@karpathy"
            },
            # 日本のAI関連アカウント
            "preferred_networks": {
                "url": "https://nitter.net/PreferredNet/rss",
                "backup_url": "https://twitrss.me/twitter_user_to_rss/?user=PreferredNet",
                "tier": 1,
                "source_name": "Preferred Networks (X)",
                "category": "ai_company_jp",
                "account": "@PreferredNet"
            },
            "rinna_inc": {
                "url": "https://nitter.net/rinna_inc/rss", 
                "backup_url": "https://twitrss.me/twitter_user_to_rss/?user=rinna_inc",
                "tier": 1,
                "source_name": "rinna (X)",
                "category": "ai_company_jp",
                "account": "@rinna_inc"
            },
            # AI系ハッシュタグ検索（代替手法）
            "ai_hashtag": {
                "url": "https://twitrss.me/twitter_search_to_rss/?term=%23AI%20OR%20%23MachineLearning%20OR%20%23DeepLearning",
                "tier": 2,
                "source_name": "AI Hashtag Posts (X)",
                "category": "hashtag_search",
                "search_terms": "#AI #MachineLearning #DeepLearning"
            }
        }
        
        # 代替RSSサービス
        self.rss_services = [
            "https://nitter.net/{}/rss",
            "https://twitrss.me/twitter_user_to_rss/?user={}",
            "https://twitterrss.me/user/{}/feed",
            "https://rsshub.app/twitter/user/{}"
        ]
    
    def get_working_x_url(self, account_config: Dict) -> str:
        """動作するXのRSS URLを取得"""
        urls_to_try = []
        
        # 設定されたURLを追加
        if "url" in account_config:
            urls_to_try.append(account_config["url"])
        if "backup_url" in account_config:
            urls_to_try.append(account_config["backup_url"])
        
        # アカウント名がある場合は各サービスを試す
        if "account" in account_config:
            username = account_config["account"].replace("@", "")
            for service_template in self.rss_services:
                if "{}" in service_template:
                    urls_to_try.append(service_template.format(username))
        
        # 各URLを試す
        for url in urls_to_try:
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ 動作URL発見: {url[:50]}...")
                    return url
            except:
                continue
        
        # どれもダメなら元のURLを返す
        return account_config.get("url", "")
    
    def collect_from_x_feed(self, source_config: Dict, max_posts: int = 5) -> List[Article]:
        """XのRSSフィードから投稿を収集"""
        articles = []
        
        try:
            print(f"🐦 X収集中: {source_config['source_name']}...")
            
            # 動作するURLを取得
            working_url = self.get_working_x_url(source_config)
            if not working_url:
                print(f"  ⚠️ 利用可能なURL無し: {source_config['source_name']}")
                return articles
            
            headers = {
                'User-Agent': 'DailyAINews/1.0 (Educational Project)',
                'Accept': 'application/rss+xml, application/xml, text/xml',
                'Accept-Language': 'en,ja;q=0.9'
            }
            
            response = requests.get(working_url, headers=headers, timeout=20)
            
            if response.status_code != 200:
                print(f"  ⚠️ HTTP {response.status_code}: {source_config['source_name']}")
                return articles
            
            # RSS解析
            feed = feedparser.parse(response.content)
            
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                print(f"  ⚠️ エントリー無し: {source_config['source_name']}")
                return articles
            
            print(f"  📄 {len(feed.entries)}個の投稿を発見")
            
            for entry in feed.entries[:max_posts]:
                try:
                    # 投稿日時
                    post_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        post_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        post_date = datetime(*entry.updated_parsed[:6])
                    else:
                        post_date = datetime.now()
                    
                    # 24時間以内の投稿のみ
                    if post_date < datetime.now() - timedelta(days=1):
                        continue
                    
                    # 投稿内容取得
                    content = ""
                    title = entry.title if hasattr(entry, 'title') else ""
                    
                    if hasattr(entry, 'summary'):
                        content = entry.summary
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    
                    # HTMLタグ削除
                    content = re.sub(r'<[^>]+>', '', content)
                    content = content.strip()
                    
                    # 短すぎる投稿はスキップ
                    if len(content) < 20:
                        continue
                    
                    # AI関連キーワードチェック
                    ai_keywords = [
                        'AI', 'artificial intelligence', 'machine learning', 'ML', 
                        'deep learning', 'neural network', 'ChatGPT', 'GPT',
                        'LLM', 'transformer', 'NLP', 'computer vision',
                        '人工知能', '機械学習', 'ディープラーニング', 'AI技術'
                    ]
                    
                    full_text = (title + " " + content).lower()
                    if not any(keyword.lower() in full_text for keyword in ai_keywords):
                        continue
                    
                    # RT（リツイート）はスキップ
                    if content.startswith('RT @') or 'RT @' in content[:10]:
                        continue
                    
                    # 記事オブジェクト作成
                    article = Article(
                        id=f"x_{source_config['source_name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}_{hash(entry.link) % 10000}",
                        title=title[:100] + "..." if len(title) > 100 else title,
                        url=entry.link,
                        source=source_config['source_name'],
                        source_tier=source_config['tier'],
                        published_date=post_date,
                        content=content[:300] + "..." if len(content) > 300 else content,
                        tags=['x_post', 'ai', source_config.get('category', 'general')]
                    )
                    
                    articles.append(article)
                    print(f"    ✅ 収集: {title[:40]}...")
                    
                except Exception as e:
                    print(f"    ⚠️ 投稿処理エラー: {str(e)[:50]}")
                    continue
            
            print(f"  ✅ {source_config['source_name']}: {len(articles)}投稿収集完了")
            
        except Exception as e:
            print(f"  ❌ {source_config['source_name']}収集エラー: {str(e)[:100]}")
        
        return articles
    
    def collect_all_x_posts(self) -> List[Article]:
        """全X（旧Twitter）ソースから収集"""
        all_posts = []
        
        print("🐦 X（旧Twitter）AI投稿収集開始")
        print("-" * 50)
        
        for source_key, config in self.x_sources.items():
            posts = self.collect_from_x_feed(config)
            all_posts.extend(posts)
            time.sleep(3)  # レート制限回避
        
        # 重複削除
        unique_posts = []
        seen_content = set()
        seen_urls = set()
        
        for post in all_posts:
            # URL重複チェック
            if post.url in seen_urls:
                continue
            
            # 内容類似度チェック（最初の50文字）
            content_key = post.content[:50].lower().replace(' ', '')
            if content_key in seen_content:
                continue
            
            seen_urls.add(post.url)
            seen_content.add(content_key)
            unique_posts.append(post)
        
        print(f"\n📊 X収集結果:")
        print(f"  • 総投稿数: {len(all_posts)}")
        print(f"  • 重複除去後: {len(unique_posts)}")
        
        return unique_posts

async def main():
    """メイン実行（日本語ソース + X投稿統合）"""
    print("🌐 Daily AI News - 日本語 + X投稿統合版")
    print("=" * 60)
    
    settings = Settings()
    
    # 1. 日本語ソース収集
    print("1️⃣ 日本語ソース収集中...")
    from collect_japanese_sources import JapaneseSourceCollector
    japanese_collector = JapaneseSourceCollector()
    japanese_articles = japanese_collector.collect_all_japanese()
    
    # 2. X投稿収集
    print("\n2️⃣ X（旧Twitter）投稿収集中...")
    x_collector = XPostCollector()
    x_posts = x_collector.collect_all_x_posts()
    
    # 3. 統合
    all_articles = japanese_articles + x_posts
    
    if not all_articles:
        print("❌ 記事・投稿が収集できませんでした")
        return False
    
    print(f"\n📈 統合結果:")
    print(f"  • 日本語記事: {len(japanese_articles)}件")
    print(f"  • X投稿: {len(x_posts)}件") 
    print(f"  • 総合計: {len(all_articles)}件")
    
    # 4. 評価
    for article in all_articles:
        content_lower = (article.title + " " + article.content).lower()
        
        # X投稿用の評価調整
        if 'x_post' in article.tags:
            base_score = 0.6  # X投稿はベーススコア高め
            tech_bonus = 0.2 if any(k in content_lower for k in ['github', 'code', 'paper', 'arxiv']) else 0.1
            business_bonus = 0.1 if any(k in content_lower for k in ['funding', 'startup', 'enterprise']) else 0.05
        else:
            # 通常記事の評価
            base_score = 0.5
            tech_bonus = 0.3 if 'ai' in content_lower else 0.1
            business_bonus = 0.2 if 'business' in content_lower else 0.1
        
        article.evaluation = {
            "engineer": {"total_score": min(1.0, base_score + tech_bonus)},
            "business": {"total_score": min(1.0, base_score + business_bonus)}
        }
        
        # メタデータ設定
        article.technical = TechnicalMetadata(
            implementation_ready='x_post' in article.tags,
            code_available='github' in content_lower,
            reproducibility_score=0.8 if 'x_post' in article.tags else 0.6
        )
        
        article.business = BusinessMetadata(
            market_size="グローバル" if 'x_post' in article.tags else "日本",
            growth_rate=article.evaluation["business"]["total_score"] * 100,
            implementation_cost=ImplementationCost.LOW if 'x_post' in article.tags else ImplementationCost.MEDIUM
        )
    
    # 5. ソート（スコア順）
    all_articles.sort(key=lambda x: (x.evaluation["engineer"]["total_score"] + x.evaluation["business"]["total_score"]) / 2, reverse=True)
    
    # 6. トップ記事表示
    print(f"\n🏆 トップ記事・投稿:")
    for i, article in enumerate(all_articles[:5]):
        eng_score = article.evaluation["engineer"]["total_score"]
        bus_score = article.evaluation["business"]["total_score"]
        post_type = "📱" if 'x_post' in article.tags else "📰"
        print(f"  {i+1}. {post_type} {article.title[:60]}")
        print(f"     ソース: {article.source}")
        print(f"     スコア: エンジニア {eng_score:.2f} | ビジネス {bus_score:.2f}")
        print()
    
    # 7. サイト生成
    try:
        generator = StaticSiteGenerator(settings)
        
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)
        
        # アセット生成
        css_content = generator.assets.generate_css()
        (docs_dir / "styles.css").write_text(css_content, encoding='utf-8')
        
        js_content = generator.assets.generate_javascript()
        (docs_dir / "script.js").write_text(js_content, encoding='utf-8')
        
        # HTML生成
        html_generator = generator.html_generator
        processed_articles = html_generator._process_articles(all_articles, "engineer")
        summary_stats = html_generator._generate_summary_stats(all_articles)
        
        articles_html = html_generator._render_articles_grid(processed_articles, "engineer")
        filters_html = html_generator._create_interactive_filters(html_generator._extract_filter_options(all_articles))
        stats_html = html_generator._render_summary_stats(summary_stats)
        
        dashboard_template = html_generator.template_engine.load_template("dashboard.html")
        dashboard_content = html_generator.template_engine.render(dashboard_template, {
            "articles": articles_html,
            "filters": filters_html,
            "summary_stats": stats_html
        })
        
        page_content = html_generator._generate_complete_page(
            dashboard_content,
            title="Daily AI News - 日本語 + X投稿統合版",
            description="日本語AIニュース + X（旧Twitter）投稿の統合ダッシュボード",
            persona="engineer"
        )
        
        index_file = docs_dir / "index.html"
        index_file.write_text(page_content, encoding='utf-8')
        
        print(f"\n✅ 統合AIニュースサイト生成完了!")
        print(f"📂 場所: {index_file.absolute()}")
        print(f"🌐 日本語記事 + X投稿が統合されました！")
        
        return True
        
    except Exception as e:
        print(f"❌ サイト生成エラー: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 日本語AIニュース + X投稿の統合サイトが完成しました！")
        print("💡 X投稿は📱アイコンで、記事は📰アイコンで表示されます")
    else:
        print("\n⚠️ 実行に問題がありました")
    
    input("\nEnterを押して終了...")