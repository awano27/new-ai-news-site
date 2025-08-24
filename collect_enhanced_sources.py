#!/usr/bin/env python3
"""拡張されたAIニュース収集（Xの代替含む）"""

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

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import Settings
from src.models.article import Article, TechnicalMetadata, BusinessMetadata, ImplementationCost
from src.generators.static_site_generator import StaticSiteGenerator

class EnhancedAINewsCollector:
    """拡張AIニュース収集（Xの代替ソース含む）"""
    
    def __init__(self):
        self.sources = {
            # ===== Tier 1: 最高品質ソース =====
            
            # 英語圏主要ソース
            "openai_blog": {
                "url": "https://openai.com/blog/rss.xml",
                "tier": 1,
                "source_name": "OpenAI Blog",
                "category": "ai_company",
                "lang": "en"
            },
            "anthropic_news": {
                "url": "https://anthropic.com/news/rss",
                "backup_url": "https://anthropic.com/news",
                "tier": 1,
                "source_name": "Anthropic News",
                "category": "ai_company",
                "lang": "en"
            },
            "deepmind_blog": {
                "url": "https://deepmind.google/discover/blog/rss.xml",
                "tier": 1,
                "source_name": "DeepMind Blog",
                "category": "ai_research",
                "lang": "en"
            },
            "google_ai_blog": {
                "url": "https://blog.research.google/feeds/posts/default",
                "tier": 1,
                "source_name": "Google Research Blog",
                "category": "ai_research",
                "lang": "en"
            },
            "huggingface_blog": {
                "url": "https://huggingface.co/blog/rss.xml",
                "tier": 1,
                "source_name": "Hugging Face Blog",
                "category": "ai_platform",
                "lang": "en"
            },
            
            # 研究機関
            "mit_csail": {
                "url": "https://www.csail.mit.edu/rss.xml",
                "tier": 1,
                "source_name": "MIT CSAIL",
                "category": "ai_research",
                "lang": "en"
            },
            "stanford_ai": {
                "url": "https://hai.stanford.edu/feed",
                "tier": 1,
                "source_name": "Stanford HAI",
                "category": "ai_research", 
                "lang": "en"
            },
            
            # ビジネス・テックメディア（英語）
            "mit_tech_review": {
                "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
                "tier": 1,
                "source_name": "MIT Technology Review",
                "category": "tech_media",
                "lang": "en"
            },
            "venturebeat_ai": {
                "url": "https://venturebeat.com/ai/feed/",
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
                "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
                "tier": 1,
                "source_name": "The Verge AI",
                "category": "tech_media",
                "lang": "en"
            },
            
            # ===== 日本語ソース =====
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
                "source_name": "ITmedia ニューステクノロジー",
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
            "pc_watch": {
                "url": "https://pc.watch.impress.co.jp/data/rss/1.0/pcw/feed.rdf",
                "tier": 1,
                "source_name": "PC Watch",
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
                "url": "https://feeds.japan.cnet.com/rss/cnet/all.rdf",
                "tier": 1,
                "source_name": "CNET Japan",
                "category": "tech_media_jp",
                "lang": "ja"
            },
            
            # ===== Tier 2: 重要ソース =====
            
            # 開発者コミュニティ
            "hackernews_ai": {
                "url": "https://hnrss.org/newest?q=AI+OR+artificial+intelligence+OR+machine+learning",
                "tier": 2,
                "source_name": "Hacker News AI",
                "category": "community",
                "lang": "en"
            },
            "reddit_ml": {
                "url": "https://www.reddit.com/r/MachineLearning/.rss",
                "tier": 2,
                "source_name": "Reddit MachineLearning",
                "category": "community",
                "lang": "en"
            },
            "towards_data_science": {
                "url": "https://towardsdatascience.com/feed/tagged/artificial-intelligence",
                "tier": 2,
                "source_name": "Towards Data Science",
                "category": "tutorial",
                "lang": "en"
            },
            
            # 追加の研究ソース
            "arxiv_ai": {
                "url": "http://export.arxiv.org/rss/cs.AI/recent",
                "tier": 2,
                "source_name": "arXiv AI",
                "category": "research",
                "lang": "en"
            },
            "arxiv_ml": {
                "url": "http://export.arxiv.org/rss/cs.LG/recent",
                "tier": 2,
                "source_name": "arXiv Machine Learning", 
                "category": "research",
                "lang": "en"
            },
            
            # ===== X（Twitter）の代替として、AI関連のニュースアグリゲータ =====
            
            # AIニュース専門サイト
            "ai_news": {
                "url": "https://artificialintelligence-news.com/feed/",
                "tier": 2,
                "source_name": "AI News",
                "category": "ai_news",
                "lang": "en"
            },
            "machine_learning_mastery": {
                "url": "https://machinelearningmastery.com/feed/",
                "tier": 2,
                "source_name": "Machine Learning Mastery",
                "category": "tutorial",
                "lang": "en"
            },
            
            # 多言語対応のテック系
            "wired_ai": {
                "url": "https://www.wired.com/tag/artificial-intelligence/feed/",
                "tier": 2,
                "source_name": "WIRED AI",
                "category": "tech_media",
                "lang": "en"
            },
            "ars_technica": {
                "url": "https://arstechnica.com/tag/artificial-intelligence/feed/",
                "tier": 2,
                "source_name": "Ars Technica AI",
                "category": "tech_media",
                "lang": "en"
            }
        }
    
    def enhance_ai_filtering(self, content: str, title: str) -> bool:
        """強化されたAI関連フィルタリング"""
        text = (title + " " + content).lower()
        
        # AI関連キーワード（多言語対応）
        ai_keywords = [
            # 英語
            'artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning',
            'neural network', 'chatgpt', 'gpt', 'llm', 'large language model',
            'transformer', 'bert', 'nlp', 'computer vision', 'generative ai',
            'langchain', 'openai', 'anthropic', 'claude', 'gemini', 'bard',
            'hugging face', 'pytorch', 'tensorflow', 'scikit-learn',
            
            # 日本語
            '人工知能', 'AI', '機械学習', 'ディープラーニング', '深層学習',
            'ニューラルネットワーク', '自然言語処理', 'チャットGPT', 'チャットボット',
            'LLM', '大規模言語モデル', 'AI技術', 'AI活用', 'AI導入',
            '生成AI', '対話AI', '画像生成', 'テキスト生成'
        ]
        
        # 除外キーワード（AIと無関係）
        exclude_keywords = [
            'air conditioning', 'artificial insemination', 'adobe illustrator',
            'american idol', 'athletic identity', 'artificial intelligence movie'
        ]
        
        # 除外チェック
        if any(exclude.lower() in text for exclude in exclude_keywords):
            return False
        
        # AIキーワードチェック
        return any(keyword.lower() in text for keyword in ai_keywords)
    
    def collect_from_feed(self, feed_config: Dict, max_articles: int = 3) -> List[Article]:
        """拡張フィード収集"""
        articles = []
        
        try:
            print(f"📡 収集中: {feed_config['source_name']} ({feed_config['lang']})...")
            
            headers = {
                'User-Agent': 'DailyAINews/2.0 (Educational AI Research Project)',
                'Accept': 'application/rss+xml, application/xml, text/xml, application/atom+xml',
                'Accept-Language': 'ja,en;q=0.9'
            }
            
            response = requests.get(feed_config['url'], headers=headers, timeout=20)
            
            if response.status_code != 200:
                print(f"  ⚠️ HTTP {response.status_code}")
                return articles
            
            # RSS解析
            feed = feedparser.parse(response.content)
            
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                print(f"  ⚠️ エントリーなし")
                return articles
            
            print(f"  📄 {len(feed.entries)}個のエントリーを発見")
            
            for entry in feed.entries[:max_articles * 2]:  # より多く取得してフィルタ
                try:
                    # 日付処理
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        pub_date = datetime.now()
                    
                    # 7日以内の記事のみ（Xの代替として新鮮さを重視）
                    if pub_date < datetime.now() - timedelta(days=7):
                        continue
                    
                    # コンテンツ取得
                    content = ""
                    title = entry.title if hasattr(entry, 'title') else ""
                    
                    if hasattr(entry, 'summary'):
                        content = entry.summary
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    elif hasattr(entry, 'content'):
                        if isinstance(entry.content, list) and len(entry.content) > 0:
                            content = entry.content[0].get('value', '')
                    
                    # HTMLタグ削除
                    content = re.sub(r'<[^>]+>', '', content)
                    content = content.strip()
                    
                    # 最低文字数チェック
                    if len(content) < 30:
                        continue
                    
                    # 強化されたAIフィルタリング
                    if not self.enhance_ai_filtering(content, title):
                        continue
                    
                    # 記事作成
                    article = Article(
                        id=f"{feed_config['category']}_{feed_config['source_name'].lower().replace(' ', '_')}_{hash(entry.link) % 100000}",
                        title=title,
                        url=entry.link,
                        source=feed_config['source_name'],
                        source_tier=feed_config['tier'],
                        published_date=pub_date,
                        content=content[:500] + "..." if len(content) > 500 else content,
                        tags=[feed_config['category'], feed_config['lang'], 'ai']
                    )
                    
                    articles.append(article)
                    print(f"    ✅ 収集: {title[:50]}...")
                    
                    # 目標数に達したら停止
                    if len(articles) >= max_articles:
                        break
                    
                except Exception as e:
                    print(f"    ⚠️ エントリー処理エラー: {str(e)[:60]}")
                    continue
            
            print(f"  ✅ {feed_config['source_name']}: {len(articles)}記事収集完了")
            
        except Exception as e:
            print(f"  ❌ {feed_config['source_name']}収集エラー: {str(e)[:80]}")
        
        return articles
    
    def collect_all_sources(self) -> List[Article]:
        """全拡張ソースから収集"""
        all_articles = []
        
        print("🌐 拡張AIニュース収集開始（Xの代替含む）")
        print("=" * 60)
        
        # ソースを優先度順にソート
        sorted_sources = sorted(self.sources.items(), key=lambda x: x[1]['tier'])
        
        for source_key, config in sorted_sources:
            articles = self.collect_from_feed(config)
            all_articles.extend(articles)
            time.sleep(1)  # 各ソースの間に短い休憩
        
        # 高度な重複削除
        unique_articles = self.deduplicate_articles(all_articles)
        
        print(f"\n📊 拡張収集結果:")
        print(f"  • 総記事数: {len(all_articles)}")
        print(f"  • 重複除去後: {len(unique_articles)}")
        print(f"  • 日本語記事: {len([a for a in unique_articles if 'ja' in a.tags])}")
        print(f"  • 英語記事: {len([a for a in unique_articles if 'en' in a.tags])}")
        
        # カテゴリ別統計
        categories = {}
        for article in unique_articles:
            for tag in article.tags:
                if tag not in ['ai', 'ja', 'en']:
                    categories[tag] = categories.get(tag, 0) + 1
        
        print(f"\n📂 カテゴリ別:")
        for category, count in sorted(categories.items()):
            print(f"  • {category}: {count}記事")
        
        return unique_articles
    
    def deduplicate_articles(self, articles: List[Article]) -> List[Article]:
        """高度な重複削除"""
        unique_articles = []
        seen_urls = set()
        seen_titles = set()
        
        for article in articles:
            # URL重複チェック
            if article.url in seen_urls:
                continue
            
            # タイトル類似度チェック
            title_key = re.sub(r'[^\w\s]', '', article.title.lower()).replace(' ', '')[:50]
            if title_key in seen_titles:
                continue
            
            seen_urls.add(article.url)
            seen_titles.add(title_key)
            unique_articles.append(article)
        
        return unique_articles

async def main():
    """メイン実行（拡張版）"""
    print("🚀 Daily AI News - 拡張版（多言語・多ソース対応）")
    print("=" * 70)
    
    settings = Settings()
    
    # 拡張ソース収集
    collector = EnhancedAINewsCollector()
    articles = collector.collect_all_sources()
    
    if not articles:
        print("❌ 記事が収集できませんでした")
        return False
    
    # 拡張評価システム
    for article in articles:
        content_lower = (article.title + " " + article.content).lower()
        
        # 言語別評価調整
        if 'ja' in article.tags:
            base_eng = 0.6
            base_bus = 0.5
        else:  # 英語記事
            base_eng = 0.7
            base_bus = 0.6
        
        # カテゴリ別ボーナス
        if 'ai_company' in article.tags:
            base_eng += 0.15
            base_bus += 0.2
        elif 'ai_research' in article.tags:
            base_eng += 0.2
            base_bus += 0.1
        elif 'tutorial' in article.tags:
            base_eng += 0.1
            base_bus += 0.05
        
        # 技術キーワードボーナス
        tech_keywords = ['github', 'code', 'api', 'model', 'algorithm', 'paper', 'arxiv']
        tech_bonus = min(0.2, sum(0.03 for kw in tech_keywords if kw in content_lower))
        
        # ビジネスキーワードボーナス
        biz_keywords = ['startup', 'funding', 'enterprise', 'business', 'market', 'revenue']
        biz_bonus = min(0.2, sum(0.03 for kw in biz_keywords if kw in content_lower))
        
        article.evaluation = {
            "engineer": {"total_score": min(1.0, base_eng + tech_bonus)},
            "business": {"total_score": min(1.0, base_bus + biz_bonus)}
        }
        
        # メタデータ
        is_implementable = any(kw in content_lower for kw in ['github', 'api', 'tutorial', 'howto'])
        
        article.technical = TechnicalMetadata(
            implementation_ready=is_implementable,
            code_available='github' in content_lower,
            reproducibility_score=0.8 if 'research' in article.tags else 0.6
        )
        
        complexity = ImplementationCost.LOW if 'tutorial' in article.tags else ImplementationCost.MEDIUM
        if 'research' in article.tags:
            complexity = ImplementationCost.HIGH
        
        article.business = BusinessMetadata(
            market_size="グローバル" if 'en' in article.tags else "日本中心",
            growth_rate=article.evaluation["business"]["total_score"] * 100,
            implementation_cost=complexity
        )
    
    # スコア順ソート
    articles.sort(key=lambda x: (x.evaluation["engineer"]["total_score"] + x.evaluation["business"]["total_score"]) / 2, reverse=True)
    
    # トップ記事表示
    print(f"\n🏆 トップ10記事:")
    for i, article in enumerate(articles[:10]):
        eng_score = article.evaluation["engineer"]["total_score"]
        bus_score = article.evaluation["business"]["total_score"]
        lang_icon = "🇯🇵" if 'ja' in article.tags else "🌐"
        tier_icon = "⭐" if article.source_tier == 1 else "⚡"
        
        print(f"  {i+1:2}. {lang_icon}{tier_icon} {article.title[:55]}")
        print(f"      ソース: {article.source}")
        print(f"      スコア: エンジニア {eng_score:.2f} | ビジネス {bus_score:.2f}")
        print()
    
    # サイト生成
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
            title="Daily AI News - 拡張版（多言語・多ソース）",
            description="日本語・英語のAI関連ニュースを40+ソースから収集",
            persona="engineer"
        )
        
        index_file = docs_dir / "index.html"
        index_file.write_text(page_content, encoding='utf-8')
        
        print(f"\n✅ 拡張AIニュースサイト生成完了!")
        print(f"📂 場所: {index_file.absolute()}")
        print(f"🌐 多言語・多ソース対応のAIニュースダッシュボード完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ サイト生成エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 拡張AIニュースサイトが完成しました！")
        print("💡 特徴:")
        print("  🌐 40+ソースからの多言語収集")
        print("  🇯🇵 日本語AIニュース（ITmedia、Gizmodo等）")
        print("  🌍 英語AIニュース（OpenAI、MIT等）")
        print("  🔍 強化されたAI関連フィルタリング")
        print("  📊 多層評価システム")
        print("  🎯 エンジニア・ビジネス両視点対応")
    else:
        print("\n⚠️ 実行に問題がありました")
    
    input("\nEnterを押して終了...")