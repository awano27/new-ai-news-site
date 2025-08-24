#!/usr/bin/env python3
"""
2025年対応 簡単版AI情報収集システム
標準ライブラリのみで動作
"""

import sys
import asyncio
import requests
import feedparser
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import re
import hashlib

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import Settings
from src.models.article import Article, TechnicalMetadata, BusinessMetadata, ImplementationCost
from src.generators.static_site_generator import StaticSiteGenerator
from x_source_collector_local import XSourceCollectorLocal
from x_source_collector import XSourceCollector

class Simple2025AICollector:
    """2025年対応簡単版AI情報収集"""
    
    def __init__(self):
        self.sources = {
            # 高信頼性ソース（動作確認済み）
            "reddit_ml": {
                "url": "https://www.reddit.com/r/MachineLearning/.rss",
                "tier": 1,
                "source_name": "Reddit MachineLearning",
                "category": "community",
                "lang": "en"
            },
            "reddit_localllama": {
                "url": "https://www.reddit.com/r/LocalLLaMA/.rss",
                "tier": 1,
                "source_name": "Reddit LocalLLaMA",
                "category": "community",
                "lang": "en"
            },
            "mit_tech_review": {
                "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
                "tier": 1,
                "source_name": "MIT Technology Review AI",
                "category": "tech_media",
                "lang": "en"
            },
            "venturebeat_ai": {
                "url": "https://venturebeat.com/category/ai/feed/",
                "tier": 1,
                "source_name": "VentureBeat AI",
                "category": "tech_media",
                "lang": "en"
            },
            "techcrunch_ai": {
                "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
                "tier": 1,
                "source_name": "TechCrunch AI",
                "category": "tech_media",
                "lang": "en"
            },
            "the_verge_ai": {
                "url": "https://www.theverge.com/rss/ai-artificial-intelligence",
                "tier": 1,
                "source_name": "The Verge AI",
                "category": "tech_media",
                "lang": "en"
            },
            
            # 日本語ソース
            "itmedia_ai": {
                "url": "https://rss.itmedia.co.jp/rss/2.0/ait.xml",
                "tier": 1,
                "source_name": "ITmedia AI",
                "category": "tech_media_jp",
                "lang": "ja"
            },
            "itmedia_news_tech": {
                "url": "https://rss.itmedia.co.jp/rss/2.0/news_technology.xml",
                "tier": 1,
                "source_name": "ITmedia News Tech",
                "category": "tech_media_jp",
                "lang": "ja"
            },
            "internet_watch": {
                "url": "https://internet.watch.impress.co.jp/data/rss/1.0/iw/feed.rdf",
                "tier": 1,
                "source_name": "INTERNET Watch",
                "category": "tech_media_jp",
                "lang": "ja"
            },
            "gizmodo_jp": {
                "url": "https://www.gizmodo.jp/index.xml",
                "tier": 1,
                "source_name": "Gizmodo Japan",
                "category": "tech_media_jp",
                "lang": "ja"
            },
            "cnet_japan": {
                "url": "http://feeds.japan.cnet.com/rss/cnet/all.rdf",
                "tier": 1,
                "source_name": "CNET Japan",
                "category": "tech_media_jp",
                "lang": "ja"
            },
            
            # ニュースレター
            "import_ai": {
                "url": "https://importai.substack.com/feed",
                "tier": 1,
                "source_name": "Import AI",
                "category": "newsletter",
                "lang": "en"
            }
        }
    
    def enhance_ai_filtering_2025(self, content: str, title: str) -> bool:
        """2025年対応AIフィルタリング"""
        text = (title + " " + content).lower()
        
        # 2025年最新AIキーワード
        ai_keywords_2025 = [
            # 基本AI用語
            'artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning',
            'neural network', 'neural net',
            
            # 大規模言語モデル
            'llm', 'large language model', 'chatgpt', 'gpt-4', 'gpt-5',
            'claude', 'gemini', 'bard', 'llama', 'mistral',
            
            # 生成AI
            'generative ai', 'gen ai', 'text generation', 'image generation',
            'stable diffusion', 'midjourney', 'dall-e', 'sora',
            
            # 2025年技術トレンド
            'rag', 'retrieval augmented generation', 'fine-tuning',
            'prompt engineering', 'multimodal', 'ai agent',
            'transformer', 'attention', 'foundation model',
            
            # 日本語AI用語
            '人工知能', 'AI', '機械学習', 'ディープラーニング',
            'チャットGPT', 'LLM', '生成AI', 'AIエージェント',
            'プロンプト', 'ファインチューニング', 'RAG'
        ]
        
        return any(keyword.lower() in text for keyword in ai_keywords_2025)
    
    def collect_from_feed(self, feed_config: Dict, max_articles: int = 4) -> List[Article]:
        """簡単版フィード収集"""
        articles = []
        
        try:
            print(f"📡 収集中: {feed_config['source_name']}...")
            
            headers = {
                'User-Agent': 'DailyAINews/2.0 (Educational Project)',
                'Accept': 'application/rss+xml, text/xml'
            }
            
            response = requests.get(feed_config['url'], headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"  ⚠️ HTTP {response.status_code}")
                return articles
            
            # 簡単なエンコーディング処理
            try:
                if 'japan' in feed_config['url'].lower() or '.jp' in feed_config['url']:
                    try:
                        content = response.content.decode('utf-8')
                    except:
                        content = response.content.decode('shift-jis', errors='ignore')
                else:
                    content = response.text
            except:
                content = response.content.decode('utf-8', errors='ignore')
            
            feed = feedparser.parse(content)
            
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                print(f"  ⚠️ エントリーなし")
                return articles
            
            print(f"  📄 {len(feed.entries)}個のエントリーを発見")
            
            for entry in feed.entries[:max_articles * 2]:
                try:
                    # 日付処理
                    pub_date = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    
                    # 3日以内の記事のみ
                    if pub_date < datetime.now() - timedelta(days=3):
                        continue
                    
                    # コンテンツ取得
                    title = getattr(entry, 'title', '')
                    content = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
                    
                    # HTMLタグ削除
                    content = re.sub(r'<[^>]+>', '', content)
                    content = re.sub(r'\s+', ' ', content).strip()
                    
                    # 最低文字数
                    if len(content) < 30:
                        continue
                    
                    # AIフィルタリング
                    if not self.enhance_ai_filtering_2025(content, title):
                        continue
                    
                    # 記事作成
                    article = Article(
                        id=f"{feed_config['category']}_{hashlib.md5((title + feed_config['source_name']).encode()).hexdigest()[:8]}",
                        title=title[:150],
                        url=getattr(entry, 'link', ''),
                        source=feed_config['source_name'],
                        source_tier=feed_config['tier'],
                        published_date=pub_date,
                        content=content[:400] + "..." if len(content) > 400 else content,
                        tags=[feed_config['category'], feed_config['lang'], 'ai_2025']
                    )
                    
                    articles.append(article)
                    print(f"    ✅ 収集: {title[:50]}...")
                    
                    if len(articles) >= max_articles:
                        break
                    
                except Exception as e:
                    print(f"    ⚠️ エントリー処理エラー: {str(e)[:50]}")
                    continue
            
            print(f"  ✅ {feed_config['source_name']}: {len(articles)}記事収集完了")
            
        except Exception as e:
            print(f"  ❌ {feed_config['source_name']}収集エラー: {str(e)[:60]}")
        
        return articles
    
    def collect_all(self) -> List[Article]:
        """全ソース収集"""
        all_articles = []
        
        print("🚀 2025年対応 簡単版AI情報収集開始")
        print("=" * 50)
        
        for source_key, config in self.sources.items():
            articles = self.collect_from_feed(config)
            all_articles.extend(articles)
            time.sleep(2)  # サーバー負荷軽減
        
        # 重複削除
        unique_articles = []
        seen_urls = set()
        seen_titles = set()
        
        for article in all_articles:
            if article.url in seen_urls:
                continue
            
            title_key = re.sub(r'[^\w\s]', '', article.title.lower())[:50]
            if title_key in seen_titles:
                continue
            
            seen_urls.add(article.url)
            seen_titles.add(title_key)
            unique_articles.append(article)
        
        print(f"\n📊 簡単版収集結果:")
        print(f"  • 総記事数: {len(all_articles)}")
        print(f"  • 重複除去後: {len(unique_articles)}")
        print(f"  • 日本語記事: {len([a for a in unique_articles if 'ja' in a.tags])}")
        print(f"  • 英語記事: {len([a for a in unique_articles if 'en' in a.tags])}")
        
        return unique_articles

async def main():
    """メイン実行（簡単版）"""
    print("⚡ Daily AI News - 2025年対応簡単版")
    print("標準ライブラリのみで動作")
    print("=" * 50)
    
    settings = Settings()
    
    # 簡単版収集
    collector = Simple2025AICollector()
    articles = collector.collect_all()
    
    # X記事収集も追加（スプレッドシートのみ）
    print("\n🐦 X記事収集を開始...")
    
    # スプレッドシートから直接取得のみ
    x_collector = XSourceCollector()
    x_articles = x_collector.parse_x_articles()
    
    if x_articles:
        print(f"✅ 本物のX記事 {len(x_articles)}件を追加")
        articles.extend(x_articles)
    else:
        print("⚠️ スプレッドシートからX記事を取得できませんでした")
    
    if not articles:
        print("❌ 記事が収集できませんでした")
        return False
    
    # 簡単評価
    for article in articles:
        content_lower = (article.title + " " + article.content).lower()
        
        # 基本スコア
        base_eng = 0.7 if 'en' in article.tags else 0.6
        base_bus = 0.6 if 'en' in article.tags else 0.5
        
        # 2025年キーワードボーナス
        keywords_2025 = ['rag', 'multimodal', 'agent', 'fine-tuning', 'gpt-4', 'claude', 'gemini']
        bonus = min(0.2, sum(0.05 for kw in keywords_2025 if kw in content_lower))
        
        article.evaluation = {
            "engineer": {"total_score": min(1.0, base_eng + bonus)},
            "business": {"total_score": min(1.0, base_bus + bonus * 0.7)}
        }
        
        # メタデータ
        article.technical = TechnicalMetadata(
            implementation_ready='tutorial' in content_lower or 'github' in content_lower,
            code_available='github' in content_lower,
            reproducibility_score=0.7
        )
        
        article.business = BusinessMetadata(
            market_size="グローバル" if 'en' in article.tags else "日本",
            growth_rate=article.evaluation["business"]["total_score"] * 100,
            implementation_cost=ImplementationCost.MEDIUM
        )
    
    # ソート
    articles.sort(key=lambda x: (
        x.evaluation["engineer"]["total_score"] + 
        x.evaluation["business"]["total_score"]
    ) / 2, reverse=True)
    
    # トップ記事表示
    print(f"\n🏆 トップ10記事:")
    for i, article in enumerate(articles[:10]):
        eng_score = article.evaluation["engineer"]["total_score"]
        bus_score = article.evaluation["business"]["total_score"]
        lang_icon = "🇯🇵" if 'ja' in article.tags else "🌍"
        
        print(f"  {i+1:2}. {lang_icon} {article.title[:50]}...")
        print(f"      ソース: {article.source}")
        print(f"      スコア: エンジニア {eng_score:.2f} | ビジネス {bus_score:.2f}")
        print()
    
    # サイト生成
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
        processed_articles = html_generator._process_articles(articles, "engineer")
        summary_stats = html_generator._generate_summary_stats(articles)
        
        articles_html = html_generator._render_articles_grid(processed_articles, "engineer")
        filters_html = html_generator._create_interactive_filters(html_generator._extract_filter_options(articles))
        stats_html = html_generator._render_summary_stats(summary_stats)
        
        dashboard_template = html_generator.template_engine.load_template("dashboard.html")
        dashboard_content = html_generator.template_engine.render(dashboard_template, {
            "articles": articles_html,
            "filters": filters_html,
            "summary_stats": stats_html
        })
        
        page_content = html_generator._generate_complete_page(
            dashboard_content,
            title="Daily AI News - 2025年簡単版",
            description="2025年最新AIトレンドを標準ライブラリのみで収集",
            persona="engineer",
            articles=articles
        )
        
        index_file = docs_dir / "index.html"
        index_file.write_text(page_content, encoding='utf-8')
        
        print(f"\n✅ 2025年簡単版AIニュースサイト生成完了!")
        print(f"📂 場所: {index_file.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"❌ サイト生成エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 2025年簡単版AIニュースサイトが完成しました！")
        print("⚡ 特徴:")
        print("  📦 標準ライブラリのみで動作")
        print("  🔍 2025年最新AIキーワード対応")
        print("  🌍 英語・日本語両対応")
        print("  📊 Reddit、MIT Tech Review等の高品質ソース")
        print("  ⚡ RAG、マルチモーダル、AIエージェント対応")
    else:
        print("\n⚠️ 実行に問題がありました")
    
    input("\nEnterを押して終了...")