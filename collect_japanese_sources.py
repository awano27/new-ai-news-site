#!/usr/bin/env python3
"""日本語ソース特化のニュースコレクション"""

import sys
import asyncio
import requests
import feedparser
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import re

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import Settings
from src.models.article import Article, TechnicalMetadata, BusinessMetadata, ImplementationCost
from src.generators.static_site_generator import StaticSiteGenerator

class JapaneseSourceCollector:
    """日本語ソース専用コレクター"""
    
    def __init__(self):
        self.sources = {
            # 動作確認済み日本語ソース
            "itmedia_ai": {
                "url": "https://rss.itmedia.co.jp/rss/2.0/ait.xml",
                "alternative_url": "https://www.itmedia.co.jp/ait/",
                "tier": 1,
                "source_name": "ITmedia AI",
                "category": "japanese"
            },
            # 追加の日本語ソース（動作確認済み）
            "itmedia_news": {
                "url": "https://rss.itmedia.co.jp/rss/2.0/news_technology.xml",
                "alternative_url": "https://www.itmedia.co.jp/news/technology/",
                "tier": 1,
                "source_name": "ITmedia ニューステクノロジー",
                "category": "japanese"
            },
            "pc_watch": {
                "url": "https://pc.watch.impress.co.jp/data/rss/1.0/pcw/feed.rdf",
                "alternative_url": "https://pc.watch.impress.co.jp/",
                "tier": 1,
                "source_name": "PC Watch",
                "category": "japanese"
            },
            "internet_watch": {
                "url": "https://internet.watch.impress.co.jp/data/rss/1.0/iw/feed.rdf",
                "alternative_url": "https://internet.watch.impress.co.jp/",
                "tier": 1,
                "source_name": "INTERNET Watch",
                "category": "japanese"
            },
            "japan_cnet": {
                "url": "https://feeds.japan.cnet.com/rss/cnet/all.rdf",
                "alternative_url": "https://japan.cnet.com/",
                "tier": 1,
                "source_name": "CNET Japan",
                "category": "japanese"
            },
            "gizmodo_jp": {
                "url": "https://www.gizmodo.jp/index.xml",
                "alternative_url": "https://www.gizmodo.jp/",
                "tier": 1,
                "source_name": "Gizmodo Japan",
                "category": "japanese"
            },
            "techcrunch_jp": {
                "url": "https://jp.techcrunch.com/feed/",
                "alternative_url": "https://jp.techcrunch.com/",
                "tier": 1,
                "source_name": "TechCrunch Japan",
                "category": "japanese"
            },
            # 代替URL形式のソース
            "mynavi_tech": {
                "url": "https://news.mynavi.jp/rss/techplus",
                "alternative_url": "https://news.mynavi.jp/techplus/",
                "tier": 2,
                "source_name": "マイナビニューステック+",
                "category": "japanese"
            }
        }
    
    def test_feed_access(self, source_config: Dict) -> bool:
        """フィードアクセステスト"""
        try:
            headers = {
                'User-Agent': 'DailyAINews/1.0 (Educational Project)',
                'Accept': 'application/rss+xml, application/xml, text/xml'
            }
            
            response = requests.get(source_config['url'], headers=headers, timeout=10)
            if response.status_code == 200:
                return True
            
            # 代替URL試行
            if 'alternative_url' in source_config:
                response = requests.get(source_config['alternative_url'], headers=headers, timeout=10)
                return response.status_code == 200
                
            return False
        except:
            return False
    
    def collect_from_feed(self, feed_config: Dict, max_articles: int = 3) -> List[Article]:
        """日本語フィードから記事収集"""
        articles = []
        
        try:
            print(f"📡 日本語ソース収集中: {feed_config['source_name']}...")
            
            # アクセステスト
            if not self.test_feed_access(feed_config):
                print(f"⚠️ アクセス不可: {feed_config['source_name']}")
                return articles
            
            headers = {
                'User-Agent': 'DailyAINews/1.0 (Educational Project)',
                'Accept': 'application/rss+xml, application/xml, text/xml',
                'Accept-Language': 'ja,en;q=0.9'
            }
            
            response = requests.get(feed_config['url'], headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"⚠️ HTTP {response.status_code}: {feed_config['source_name']}")
                return articles
            
            # エンコーディング確認
            if 'charset' in response.headers.get('content-type', ''):
                encoding = response.headers['content-type'].split('charset=')[-1]
                response.encoding = encoding
            
            feed = feedparser.parse(response.content)
            
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                print(f"⚠️ エントリーなし: {feed_config['source_name']}")
                return articles
            
            print(f"📄 {len(feed.entries)}個のエントリーを発見")
            
            for entry in feed.entries[:max_articles]:
                try:
                    # 日付解析
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        pub_date = datetime.now()
                    
                    # 古い記事をスキップ
                    if pub_date < datetime.now() - timedelta(days=60):
                        continue
                    
                    # コンテンツ取得
                    content = ""
                    if hasattr(entry, 'summary'):
                        content = entry.summary
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    elif hasattr(entry, 'content'):
                        if isinstance(entry.content, list) and len(entry.content) > 0:
                            content = entry.content[0].get('value', '')
                        else:
                            content = str(entry.content)
                    
                    # HTMLタグを削除
                    content = re.sub(r'<[^>]+>', '', content)
                    content = content.strip()
                    
                    # 短いコンテンツをスキップ
                    if len(content) < 50:
                        continue
                    
                    # AI関連チェック
                    ai_keywords = ['AI', 'ai', '人工知能', '機械学習', 'ML', 'ディープラーニング', 'ChatGPT', 'GPT']
                    content_and_title = (entry.title + " " + content).lower()
                    
                    if not any(keyword.lower() in content_and_title for keyword in ai_keywords):
                        continue
                    
                    article = Article(
                        id=f"{feed_config['source_name'].lower().replace(' ', '_').replace('.', '_')}_{hash(entry.link) % 10000}",
                        title=entry.title,
                        url=entry.link,
                        source=feed_config['source_name'],
                        source_tier=feed_config['tier'],
                        published_date=pub_date,
                        content=content,
                        tags=['japanese', 'ai']
                    )
                    
                    articles.append(article)
                    print(f"  ✅ 収集: {entry.title[:40]}...")
                    
                except Exception as e:
                    print(f"  ⚠️ エントリー処理エラー: {str(e)[:50]}")
                    continue
            
            print(f"✅ {feed_config['source_name']}: {len(articles)}記事収集完了")
            
        except Exception as e:
            print(f"❌ {feed_config['source_name']}収集エラー: {str(e)[:100]}")
        
        return articles
    
    def collect_all_japanese(self) -> List[Article]:
        """全日本語ソースから収集"""
        all_articles = []
        
        print("🇯🇵 日本語AIニュース収集開始")
        print("-" * 40)
        
        for source_key, config in self.sources.items():
            articles = self.collect_from_feed(config)
            all_articles.extend(articles)
            time.sleep(2)  # サーバーに負荷をかけない
        
        # 重複削除
        unique_articles = []
        seen_urls = set()
        seen_titles = set()
        
        for article in all_articles:
            # URL重複チェック
            if article.url in seen_urls:
                continue
            
            # タイトル類似度チェック
            title_key = article.title.lower().replace(' ', '').replace('　', '')[:30]
            if title_key in seen_titles:
                continue
            
            seen_urls.add(article.url)
            seen_titles.add(title_key)
            unique_articles.append(article)
        
        print(f"\n📊 収集結果:")
        print(f"  • 総記事数: {len(all_articles)}")
        print(f"  • 重複除去後: {len(unique_articles)}")
        
        return unique_articles

async def main():
    """メイン実行"""
    print("🌸 日本語AIニュース特化コレクション")
    print("=" * 50)
    
    settings = Settings()
    collector = JapaneseSourceCollector()
    
    # 日本語記事収集
    japanese_articles = collector.collect_all_japanese()
    
    if not japanese_articles:
        print("❌ 日本語記事が収集できませんでした")
        return False
    
    # 簡単な評価
    for article in japanese_articles:
        content_lower = (article.title + " " + article.content).lower()
        
        # 日本語特有のキーワード
        tech_jp_keywords = ['技術', '開発', 'プログラミング', 'エンジニア', '実装']
        business_jp_keywords = ['ビジネス', '企業', '導入', '活用', '効果', '売上']
        
        tech_score = 0.5 + (sum(1 for k in tech_jp_keywords if k in content_lower) * 0.1)
        business_score = 0.5 + (sum(1 for k in business_jp_keywords if k in content_lower) * 0.1)
        
        article.evaluation = {
            "engineer": {"total_score": min(1.0, tech_score)},
            "business": {"total_score": min(1.0, business_score)}
        }
        
        # メタデータ
        article.technical = TechnicalMetadata(
            implementation_ready=any(k in content_lower for k in ['github', 'コード', '実装']),
            code_available=any(k in content_lower for k in ['github', 'コード']),
            reproducibility_score=0.7
        )
        
        article.business = BusinessMetadata(
            market_size="日本市場",
            growth_rate=business_score * 100,
            implementation_cost=ImplementationCost.MEDIUM
        )
    
    # ソート
    japanese_articles.sort(key=lambda x: (x.evaluation["engineer"]["total_score"] + x.evaluation["business"]["total_score"]) / 2, reverse=True)
    
    print(f"\n🏆 トップ日本語記事:")
    for i, article in enumerate(japanese_articles[:3]):
        eng_score = article.evaluation["engineer"]["total_score"]
        bus_score = article.evaluation["business"]["total_score"]
        print(f"  {i+1}. {article.title}")
        print(f"     ソース: {article.source}")
        print(f"     スコア: エンジニア {eng_score:.2f} | ビジネス {bus_score:.2f}")
        print()
    
    # 既存記事と統合してサイト生成
    try:
        generator = StaticSiteGenerator(settings)
        
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)
        
        # CSS/JS生成
        css_content = generator.assets.generate_css()
        (docs_dir / "styles.css").write_text(css_content, encoding='utf-8')
        
        js_content = generator.assets.generate_javascript()
        (docs_dir / "script.js").write_text(js_content, encoding='utf-8')
        
        # HTML生成
        html_generator = generator.html_generator
        processed_articles = html_generator._process_articles(japanese_articles, "engineer")
        summary_stats = html_generator._generate_summary_stats(japanese_articles)
        
        articles_html = html_generator._render_articles_grid(processed_articles, "engineer")
        filters_html = html_generator._create_interactive_filters(html_generator._extract_filter_options(japanese_articles))
        stats_html = html_generator._render_summary_stats(summary_stats)
        
        dashboard_template = html_generator.template_engine.load_template("dashboard.html")
        dashboard_content = html_generator.template_engine.render(dashboard_template, {
            "articles": articles_html,
            "filters": filters_html,
            "summary_stats": stats_html
        })
        
        page_content = html_generator._generate_complete_page(
            dashboard_content,
            title="Daily AI News - 日本語AIニュース特化",
            description="日本語AIニュースの多層評価システム",
            persona="engineer"
        )
        
        index_file = docs_dir / "index.html"
        index_file.write_text(page_content, encoding='utf-8')
        
        print(f"✅ 日本語AIニュースサイト生成完了!")
        print(f"📂 場所: {index_file.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"❌ サイト生成エラー: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n🎌 日本語AIニュース収集・サイト生成が完了しました！")
    else:
        print("\n⚠️ 実行に問題がありました")
    
    print(f"\n💡 サイトを開くには:")
    print(f"  C:\\Users\\yoshitaka\\new-ai-news-site\\docs\\index.html")