#!/usr/bin/env python3
"""
統合版記事収集システム
X記事 + RSS記事の両方を統合表示
"""

import requests
import json
import csv
import feedparser
from io import StringIO
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import re
import html
from urllib.parse import urljoin, urlparse
import time
from evaluation_system import MultiLayerEvaluator


class IntegratedCollector:
    """X記事とRSS記事を統合収集するクラス"""
    
    def __init__(self):
        self.spreadsheet_url = "https://docs.google.com/spreadsheets/d/1uuLKCLIJw--a1vCcO6UGxSpBiLTtN8uGl2cdMb6wcfg/export?format=csv&gid=0"
        self.project_root = Path(__file__).parent
        self.docs_path = self.project_root / "docs"
        self.evaluator = MultiLayerEvaluator()
        
        # RSS フィード設定
        self.rss_feeds = {
            "MIT Technology Review AI": {
                "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
                "tier": 1
            },
            "Reddit MachineLearning": {
                "url": "https://www.reddit.com/r/MachineLearning/.rss",
                "tier": 1
            },
            "Reddit LocalLLaMA": {
                "url": "https://www.reddit.com/r/LocalLLaMA/.rss",
                "tier": 1
            },
            "VentureBeat AI": {
                "url": "https://venturebeat.com/ai/feed/",
                "tier": 1
            },
            "TechCrunch AI": {
                "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
                "tier": 1
            },
            "Hacker News AI": {
                "url": "https://hnrss.org/newest?q=AI+OR+machine+learning+OR+deep+learning",
                "tier": 2
            }
        }
    
    def translate_and_summarize(self, text, title=""):
        """英語記事を日本語要約に変換"""
        if not text or not text.strip():
            return text
        
        # 既に日本語の場合はそのまま返す
        if self.is_japanese(text):
            return text[:200] + "..." if len(text) > 200 else text
        
        try:
            # 簡易的な要約・翻訳処理
            # 実際のAI要約の代わりに、キーワードベースの要約を作成
            summary_jp = self.create_japanese_summary(text, title)
            return summary_jp
            
        except Exception as e:
            print(f"Translation error: {str(e)}")
            # フォールバック: 英語をそのまま使用
            return text[:200] + "..." if len(text) > 200 else text
    
    def is_japanese(self, text):
        """テキストが日本語かどうかを判定"""
        japanese_chars = sum(1 for c in text if '\u3040' <= c <= '\u309F' or '\u30A0' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FAF')
        return japanese_chars > len(text) * 0.1  # 10%以上日本語文字があれば日本語と判定
    
    def create_japanese_summary(self, english_text, title=""):
        """英語記事の日本語要約を作成"""
        # キーワードベースの翻訳・要約
        key_translations = {
            # AI関連用語
            "artificial intelligence": "人工知能",
            "machine learning": "機械学習", 
            "deep learning": "ディープラーニング",
            "neural network": "ニューラルネットワーク",
            "transformer": "トランスフォーマー",
            "language model": "言語モデル",
            "chatgpt": "ChatGPT",
            "gpt-4": "GPT-4",
            "gpt-5": "GPT-5", 
            "claude": "Claude",
            "openai": "OpenAI",
            "anthropic": "Anthropic",
            "google": "Google",
            "microsoft": "Microsoft",
            "meta": "Meta",
            "facebook": "Facebook",
            "research": "研究",
            "model": "モデル",
            "algorithm": "アルゴリズム",
            "data": "データ",
            "training": "トレーニング",
            "inference": "推論",
            "performance": "性能",
            "benchmark": "ベンチマーク",
            "breakthrough": "ブレークスルー",
            "innovation": "イノベーション",
            "technology": "技術",
            "development": "開発",
            "release": "リリース",
            "announcement": "発表",
            "improvement": "改善",
            "enhancement": "機能強化",
            "new": "新しい",
            "latest": "最新",
            "advanced": "高度な",
            "powerful": "強力な",
            "efficient": "効率的な",
            "accuracy": "精度",
            "capability": "能力",
            "feature": "機能",
            "tool": "ツール",
            "platform": "プラットフォーム",
            "system": "システム",
            "framework": "フレームワーク",
            "library": "ライブラリ",
            "api": "API",
            "application": "アプリケーション",
            "software": "ソフトウェア",
            "hardware": "ハードウェア",
            "chip": "チップ",
            "processor": "プロセッサ",
            "gpu": "GPU",
            "computing": "コンピューティング",
            "cloud": "クラウド",
            "edge": "エッジ",
            "mobile": "モバイル",
            "web": "ウェブ",
            "internet": "インターネット",
            "startup": "スタートアップ",
            "company": "企業",
            "business": "ビジネス",
            "industry": "業界",
            "market": "市場",
            "investment": "投資",
            "funding": "資金調達",
            "revenue": "収益",
            "growth": "成長",
            "user": "ユーザー",
            "customer": "顧客",
            "product": "製品",
            "service": "サービス",
            "solution": "ソリューション"
        }
        
        # テキストを小文字にして処理
        text_lower = english_text.lower()
        
        # 重要なキーワードを抽出
        found_keywords = []
        for eng, jp in key_translations.items():
            if eng in text_lower:
                found_keywords.append(jp)
        
        # タイトルからの要約
        title_summary = ""
        if title:
            title_lower = title.lower()
            for eng, jp in key_translations.items():
                title_lower = title_lower.replace(eng, jp)
            title_summary = title_lower
        
        # 要約文を生成
        if found_keywords:
            summary = f"{title_summary}に関する記事。" if title_summary else ""
            
            # AI関連の話題を特定
            if any(kw in found_keywords for kw in ["人工知能", "機械学習", "ディープラーニング", "ChatGPT", "GPT-4", "GPT-5", "Claude"]):
                summary += "AI技術の"
                
                if any(kw in found_keywords for kw in ["新しい", "最新", "リリース", "発表"]):
                    summary += "最新動向や新機能について報告。"
                elif any(kw in found_keywords for kw in ["研究", "ブレークスルー", "イノベーション"]):
                    summary += "研究成果や技術革新について解説。"
                elif any(kw in found_keywords for kw in ["性能", "改善", "機能強化"]):
                    summary += "性能向上や改善に関する内容。"
                elif any(kw in found_keywords for kw in ["ビジネス", "企業", "市場", "投資"]):
                    summary += "ビジネス面での動きや市場動向について。"
                else:
                    summary += "開発や応用に関する情報。"
            
            # 企業名が含まれる場合
            companies = [kw for kw in found_keywords if kw in ["OpenAI", "Anthropic", "Google", "Microsoft", "Meta"]]
            if companies:
                summary += f" {', '.join(companies)}が関連する"
                
                if "発表" in found_keywords or "リリース" in found_keywords:
                    summary += "新しい発表やリリースについて。"
                elif "研究" in found_keywords:
                    summary += "研究開発の取り組みについて。"
                else:
                    summary += "動向について。"
            
            return summary
        else:
            # キーワードが見つからない場合は汎用的な要約
            return f"AI・技術分野に関する{title_summary}の記事。最新の動向や技術開発について。"
    
    def collect_x_articles(self):
        """X記事を収集"""
        print("Collecting X articles...")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.spreadsheet_url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"X articles fetch failed: {response.status_code}")
                return []
            
            # 文字エンコーディング処理
            try:
                csv_text = response.content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    csv_text = response.content.decode('iso-8859-1')
                except UnicodeDecodeError:
                    csv_text = response.content.decode('shift-jis', errors='ignore')
            
            # CSVを解析
            reader = csv.reader(StringIO(csv_text))
            headers = next(reader)  # ヘッダー行をスキップ
            
            x_articles = []
            processed_count = 0
            
            for row in reader:
                if len(row) < 5:
                    continue
                    
                processed_count += 1
                
                # データを抽出
                created_at = row[0].strip()
                username = row[1].strip().replace('@', '')
                content = row[2].strip()
                first_link = row[3].strip() if len(row) > 3 else ""
                tweet_link = row[4].strip() if len(row) > 4 else ""
                
                # HTML エンティティをデコード
                content = html.unescape(content)
                username = html.unescape(username)
                
                # URLフィルタリング
                article_url = None
                if first_link and self.is_valid_url(first_link):
                    article_url = first_link
                elif tweet_link and self.is_valid_url(tweet_link):
                    article_url = tweet_link
                else:
                    article_url = f"https://twitter.com/{username}"
                
                # AI関連チェック
                if not self.is_ai_related(content):
                    continue
                
                # 記事データ作成
                article = {
                    'id': f"x_{hashlib.md5(f'{username}_{content}'.encode()).hexdigest()[:8]}",
                    'title': self.extract_title(content),
                    'url': article_url,
                    'source': f'X(@{username})',
                    'source_tier': 2,
                    'published_date': self.parse_date(created_at),
                    'content': content[:200] + "..." if len(content) > 200 else content,
                    'tags': ['x_post', 'ai_2025', 'community']
                }
                
                # 多層評価システムで評価
                engineer_eval = self.evaluator.evaluate_article(article, 'engineer')
                business_eval = self.evaluator.evaluate_article(article, 'business')
                
                article['evaluation'] = {
                    'engineer': engineer_eval,
                    'business': business_eval
                }
                article['total_score'] = engineer_eval['total_score']  # デフォルトはエンジニア向け
                
                x_articles.append(article)
                
                if len(x_articles) >= 30:  # X記事は30件まで
                    break
            
            print(f"X articles collected: {len(x_articles)}")
            return x_articles
            
        except Exception as e:
            print(f"X articles collection error: {str(e)}")
            return []
    
    def collect_rss_articles(self):
        """RSS記事を収集"""
        print("Collecting RSS articles...")
        
        rss_articles = []
        cutoff_date = datetime.now() - timedelta(days=7)  # 7日以内の記事のみ
        
        for source_name, feed_config in self.rss_feeds.items():
            try:
                print(f"Fetching from {source_name}...")
                
                # フィードを取得
                feed = feedparser.parse(feed_config["url"])
                
                if not hasattr(feed, 'entries') or not feed.entries:
                    print(f"No entries found for {source_name}")
                    continue
                
                for entry in feed.entries[:10]:  # 各ソースから最大10記事
                    try:
                        # 日付チェック
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6])
                            if pub_date < cutoff_date:
                                continue
                            date_str = pub_date.strftime('%Y-%m-%d')
                        else:
                            date_str = datetime.now().strftime('%Y-%m-%d')
                        
                        # タイトルと内容を取得
                        title = getattr(entry, 'title', 'No Title')
                        url = getattr(entry, 'link', '')
                        
                        # 内容を抽出
                        content = ''
                        if hasattr(entry, 'summary'):
                            content = entry.summary
                        elif hasattr(entry, 'description'):
                            content = entry.description
                        else:
                            content = title
                        
                        # HTMLタグを除去
                        content = re.sub(r'<[^>]+>', '', content)
                        content = html.unescape(content).strip()
                        
                        # AI関連チェック
                        if not self.is_ai_related(f"{title} {content}"):
                            continue
                        
                        # 日本語要約を生成
                        japanese_summary = self.translate_and_summarize(content, title)
                        
                        # 記事データ作成
                        article = {
                            'id': f"rss_{hashlib.md5(f'{source_name}_{title}'.encode()).hexdigest()[:8]}",
                            'title': title,
                            'url': url,
                            'source': source_name,
                            'source_tier': feed_config["tier"],
                            'published_date': date_str,
                            'content': japanese_summary,
                            'original_content': content[:200] + "..." if len(content) > 200 else content,
                            'tags': ['rss_feed', 'ai_2025', 'tech_media']
                        }
                        
                        # 多層評価システムで評価
                        engineer_eval = self.evaluator.evaluate_article(article, 'engineer')
                        business_eval = self.evaluator.evaluate_article(article, 'business')
                        
                        article['evaluation'] = {
                            'engineer': engineer_eval,
                            'business': business_eval
                        }
                        article['total_score'] = engineer_eval['total_score']  # デフォルトはエンジニア向け
                        
                        rss_articles.append(article)
                        
                    except Exception as entry_error:
                        print(f"Error processing entry from {source_name}: {str(entry_error)}")
                        continue
                        
            except Exception as feed_error:
                print(f"Error fetching {source_name}: {str(feed_error)}")
                continue
        
        print(f"RSS articles collected: {len(rss_articles)}")
        return rss_articles
    
    def is_valid_url(self, url):
        """URLの有効性をチェック"""
        if not url:
            return False
        
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    def is_ai_related(self, content):
        """AI関連コンテンツかどうか判定"""
        text = content.lower()
        ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
            'chatgpt', 'gpt-4', 'gpt-5', 'claude', 'gemini', 'llm', 'openai', 'anthropic',
            'neural network', 'transformer', 'diffusion', 'rag', 'embedding',
            '人工知能', 'AI', '機械学習', 'ディープラーニング', '生成AI', 'チャットGPT',
            'pytorch', 'tensorflow', 'hugging face', 'langchain', 'vector database',
            'fine-tuning', 'prompt engineering', 'multimodal', 'computer vision'
        ]
        
        return any(keyword in text for keyword in ai_keywords)
    
    def extract_title(self, content):
        """コンテンツからタイトルを抽出"""
        sentences = re.split(r'[.!?。！？\n]', content)
        if sentences and len(sentences[0]) <= 80:
            return sentences[0].strip()
        return content[:50] + "..." if len(content) > 50 else content
    
    def parse_date(self, date_string):
        """日付文字列を解析"""
        try:
            if 'T' in date_string:
                if date_string.endswith('Z'):
                    date_string = date_string[:-1] + '+00:00'
                dt = datetime.fromisoformat(date_string)
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                return dt.strftime('%Y-%m-%d')
            else:
                return datetime.now().strftime('%Y-%m-%d')
        except:
            return datetime.now().strftime('%Y-%m-%d')
    
    def generate_html(self, all_articles):
        """統合記事データからHTMLを生成"""
        print(f"Generating integrated HTML... ({len(all_articles)} articles total)")
        
        # 記事は既にソート済み（念のため再度ソート）
        all_articles.sort(key=lambda x: x.get('total_score', 0.0), reverse=True)
        
        # 上位記事のスコアを確認
        print(f"Top 3 articles by score:")
        for i, article in enumerate(all_articles[:3]):
            score = article.get('total_score', 0)
            print(f"{i+1}. {article['title'][:40]}... - Score: {score:.3f}")
        
        # 統計情報を計算
        x_count = len([a for a in all_articles if a['source'].startswith('X(')])
        rss_count = len([a for a in all_articles if not a['source'].startswith('X(')])
        tier1_count = len([a for a in all_articles if a['source_tier'] == 1])
        
        articles_json = json.dumps(all_articles, ensure_ascii=False, indent=2)
        
        html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily AI News - 統合版</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 0; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 10px; font-weight: 700; }}
        .header p {{ font-size: 1.1rem; opacity: 0.9; }}
        .stats {{ background: white; margin: 20px 0; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 25px; }}
        .stat-item {{ text-align: center; }}
        .stat-value {{ font-size: 2.2rem; font-weight: bold; color: #667eea; margin-bottom: 5px; }}
        .stat-label {{ color: #6b7280; font-size: 0.9rem; font-weight: 500; }}
        .filters {{ background: white; margin: 20px 0; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .filter-group {{ display: flex; flex-wrap: wrap; gap: 15px; align-items: center; }}
        .filter-item {{ display: flex; flex-direction: column; }}
        .filter-item label {{ font-size: 0.9rem; font-weight: 500; margin-bottom: 5px; color: #374151; }}
        .filter-item select, .filter-item input {{ padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.9rem; }}
        .articles-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 25px; margin: 20px 0; }}
        .article-card {{ background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; transition: all 0.3s; }}
        .article-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
        .article-header {{ padding: 20px; }}
        .article-title {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 12px; line-height: 1.4; }}
        .article-title a {{ color: #1a202c; text-decoration: none; }}
        .article-title a:hover {{ color: #667eea; }}
        .article-meta {{ display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: #6b7280; margin-bottom: 15px; }}
        .source {{ padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 500; }}
        .source.tier-1 {{ background: #10b981; color: white; }}
        .source.tier-2 {{ background: #3b82f6; color: white; }}
        .article-content {{ padding: 0 20px 15px; color: #4b5563; line-height: 1.6; }}
        .summary-note {{ padding: 0 20px 15px; font-size: 0.85rem; color: #9ca3af; font-style: italic; }}
        .evaluation-panel {{ padding: 15px 20px; background: #f8fafc; border-top: 1px solid #f3f4f6; }}
        .score-display {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }}
        .total-score {{ font-size: 1.8rem; font-weight: bold; color: #10b981; }}
        .persona-toggle {{ display: flex; gap: 8px; }}
        .persona-btn {{ padding: 4px 12px; border: 1px solid #d1d5db; border-radius: 6px; background: white; cursor: pointer; font-size: 0.8rem; transition: all 0.2s; }}
        .persona-btn.active {{ background: #667eea; color: white; border-color: #667eea; }}
        .score-breakdown {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-top: 10px; }}
        .score-item {{ text-align: center; padding: 6px 4px; background: white; border-radius: 4px; border: 1px solid #e5e7eb; }}
        .score-value {{ font-size: 0.9rem; font-weight: bold; color: #374151; }}
        .score-label {{ font-size: 0.7rem; color: #6b7280; }}
        .recommendation {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 500; margin-top: 8px; }}
        .rec-must_read {{ background: #dcfce7; color: #16a34a; }}
        .rec-recommended {{ background: #dbeafe; color: #2563eb; }}
        .rec-consider {{ background: #fef3c7; color: #d97706; }}
        .rec-skip {{ background: #fee2e2; color: #dc2626; }}
        .article-actions {{ padding: 20px; border-top: 1px solid #f3f4f6; }}
        .read-more {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 500; display: inline-block; transition: all 0.3s; }}
        .read-more:hover {{ transform: translateY(-2px); box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }}
        .footer {{ background: #1a202c; color: white; text-align: center; padding: 40px 20px; margin-top: 40px; }}
        @media (max-width: 768px) {{
            .articles-grid {{ grid-template-columns: 1fr; }}
            .header h1 {{ font-size: 2rem; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>Daily AI News - 統合版</h1>
            <p>X記事 + RSS記事を統合した最新AI情報</p>
        </div>
    </header>

    <div class="container">
        <div class="stats">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value">{len(all_articles)}</div>
                    <div class="stat-label">総記事数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{x_count}</div>
                    <div class="stat-label">X記事</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{rss_count}</div>
                    <div class="stat-label">RSS記事</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{tier1_count}</div>
                    <div class="stat-label">Tier1記事</div>
                </div>
            </div>
        </div>

        <div class="filters">
            <div class="filter-group">
                <div class="filter-item">
                    <label>ソース種別</label>
                    <select id="source-type-filter">
                        <option value="all">すべて</option>
                        <option value="x">X記事のみ</option>
                        <option value="rss">RSS記事のみ</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label>Tier</label>
                    <select id="tier-filter">
                        <option value="all">すべて</option>
                        <option value="1">Tier 1</option>
                        <option value="2">Tier 2</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label>検索</label>
                    <input type="text" id="search-input" placeholder="キーワードで検索...">
                </div>
            </div>
        </div>

        <div class="articles-grid" id="articles-container">
            <!-- 記事はJavaScriptで動的生成 -->
        </div>
    </div>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 Daily AI News - X記事 + RSS記事統合版</p>
        </div>
    </footer>

    <script>
        const articles = {articles_json};
        let filteredArticles = [...articles];
        
        function renderArticles() {{
            const container = document.getElementById('articles-container');
            container.innerHTML = '';
            
            filteredArticles.forEach(article => {{
                const card = document.createElement('div');
                card.className = 'article-card';
                
                const escapeHtml = (text) => {{
                    const div = document.createElement('div');
                    div.textContent = text;
                    return div.innerHTML;
                }};
                
                const tierClass = `tier-${{article.source_tier}}`;
                const isRssArticle = !article.source.startsWith('X(');
                const evaluation = article.evaluation || {{}};
                const engineerEval = evaluation.engineer || {{}};
                const businessEval = evaluation.business || {{}};
                
                // デフォルトは engineer 評価を使用
                let currentEval = engineerEval;
                let currentPersona = 'engineer';
                
                const getRecommendationText = (rec) => {{
                    const texts = {{
                        'must_read': '必読',
                        'recommended': '推奨',
                        'consider': '検討',
                        'skip': 'スキップ'
                    }};
                    return texts[rec] || rec;
                }};
                
                card.innerHTML = `
                    <div class="article-header">
                        <h3 class="article-title">
                            <a href="${{encodeURI(article.url)}}" target="_blank" rel="noopener noreferrer">
                                ${{escapeHtml(article.title)}}
                            </a>
                        </h3>
                        <div class="article-meta">
                            <span class="source ${{tierClass}}">${{escapeHtml(article.source)}}</span>
                            <span>${{article.published_date}}</span>
                        </div>
                    </div>
                    <div class="article-content">
                        ${{escapeHtml(article.content)}}
                    </div>
                    ${{isRssArticle ? '<div class="summary-note">※ この記事は日本語要約版です</div>' : ''}}
                    <div class="evaluation-panel">
                        <div class="score-display">
                            <div class="total-score" data-score="${{(currentEval.total_score || 0).toFixed(2)}}">${{Math.round((currentEval.total_score || 0) * 100)}}</div>
                            <div class="persona-toggle">
                                <button class="persona-btn active" data-persona="engineer">エンジニア</button>
                                <button class="persona-btn" data-persona="business">ビジネス</button>
                            </div>
                        </div>
                        <div class="score-breakdown">
                            <div class="score-item">
                                <div class="score-value">${{Math.round((currentEval.breakdown?.quality || 0) * 100)}}</div>
                                <div class="score-label">品質</div>
                            </div>
                            <div class="score-item">
                                <div class="score-value">${{Math.round((currentEval.breakdown?.relevance || 0) * 100)}}</div>
                                <div class="score-label">関連性</div>
                            </div>
                            <div class="score-item">
                                <div class="score-value">${{Math.round((currentEval.breakdown?.temporal || 0) * 100)}}</div>
                                <div class="score-label">時間的価値</div>
                            </div>
                            <div class="score-item">
                                <div class="score-value">${{Math.round((currentEval.breakdown?.trust || 0) * 100)}}</div>
                                <div class="score-label">信頼性</div>
                            </div>
                            <div class="score-item">
                                <div class="score-value">${{Math.round((currentEval.breakdown?.actionability || 0) * 100)}}</div>
                                <div class="score-label">実行性</div>
                            </div>
                        </div>
                        <div class="recommendation rec-${{currentEval.recommendation || 'consider'}}">
                            ${{getRecommendationText(currentEval.recommendation || 'consider')}}
                        </div>
                    </div>
                    <div class="article-actions">
                        <a href="${{encodeURI(article.url)}}" class="read-more" target="_blank">
                            ${{isRssArticle ? '元記事を読む（英語）' : '記事を読む'}}
                        </a>
                    </div>
                `;
                
                // ペルソナ切り替えイベント
                const personaBtns = card.querySelectorAll('.persona-btn');
                personaBtns.forEach(btn => {{
                    btn.addEventListener('click', () => {{
                        const persona = btn.dataset.persona;
                        const evalData = persona === 'engineer' ? engineerEval : businessEval;
                        
                        // ボタンの状態更新
                        personaBtns.forEach(b => b.classList.remove('active'));
                        btn.classList.add('active');
                        
                        // スコア表示更新
                        const scoreDisplay = card.querySelector('.total-score');
                        scoreDisplay.textContent = Math.round((evalData.total_score || 0) * 100);
                        
                        // 内訳スコア更新
                        const scoreItems = card.querySelectorAll('.score-item .score-value');
                        const breakdown = evalData.breakdown || {{}};
                        scoreItems[0].textContent = Math.round((breakdown.quality || 0) * 100);
                        scoreItems[1].textContent = Math.round((breakdown.relevance || 0) * 100);
                        scoreItems[2].textContent = Math.round((breakdown.temporal || 0) * 100);
                        scoreItems[3].textContent = Math.round((breakdown.trust || 0) * 100);
                        scoreItems[4].textContent = Math.round((breakdown.actionability || 0) * 100);
                        
                        // 推奨レベル更新
                        const recElement = card.querySelector('.recommendation');
                        recElement.className = `recommendation rec-${{evalData.recommendation || 'consider'}}`;
                        recElement.textContent = getRecommendationText(evalData.recommendation || 'consider');
                    }});
                }});
                
                container.appendChild(card);
            }});
        }}
        
        function applyFilters() {{
            const sourceTypeFilter = document.getElementById('source-type-filter').value;
            const tierFilter = document.getElementById('tier-filter').value;
            const searchQuery = document.getElementById('search-input').value.toLowerCase();
            
            filteredArticles = articles.filter(article => {{
                // ソース種別フィルター
                if (sourceTypeFilter === 'x' && !article.source.startsWith('X(')) return false;
                if (sourceTypeFilter === 'rss' && article.source.startsWith('X(')) return false;
                
                // Tierフィルター
                if (tierFilter !== 'all' && article.source_tier !== parseInt(tierFilter)) return false;
                
                // 検索フィルター
                if (searchQuery && 
                    !article.title.toLowerCase().includes(searchQuery) &&
                    !article.content.toLowerCase().includes(searchQuery) &&
                    !article.source.toLowerCase().includes(searchQuery)) return false;
                
                return true;
            }});
            
            renderArticles();
        }}
        
        // イベントリスナーを設定
        document.getElementById('source-type-filter').addEventListener('change', applyFilters);
        document.getElementById('tier-filter').addEventListener('change', applyFilters);
        document.getElementById('search-input').addEventListener('input', applyFilters);
        
        // ページ読み込み時に記事を表示
        document.addEventListener('DOMContentLoaded', renderArticles);
    </script>
</body>
</html>"""
        
        return html_content
    
    def save_html(self, html_content):
        """HTMLファイルを保存"""
        output_path = self.docs_path / "index.html"
        
        try:
            self.docs_path.mkdir(exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                f.write(html_content)
            print(f"HTML file saved: {output_path}")
            return True
        except Exception as e:
            print(f"HTML save error: {str(e)}")
            return False
    
    def run(self):
        """統合収集実行"""
        print("Starting integrated article collection...")
        
        # X記事を収集
        x_articles = self.collect_x_articles()
        
        # RSS記事を収集
        rss_articles = self.collect_rss_articles()
        
        # 統合
        all_articles = x_articles + rss_articles
        
        if not all_articles:
            print("No articles collected")
            return False
        
        # 全記事の評価スコアを確認・設定
        for article in all_articles:
            if 'total_score' not in article:
                engineer_eval = article.get('evaluation', {}).get('engineer', {})
                article['total_score'] = engineer_eval.get('total_score', 0.0)
        
        # デバッグ: 評価スコアを表示
        print(f"\nArticle scores (before sorting):")
        for i, article in enumerate(all_articles[:5]):
            print(f"{i+1}. {article['title'][:50]}... - Score: {article.get('total_score', 0):.3f}")
        
        # 評価順でソート
        all_articles.sort(key=lambda x: x.get('total_score', 0.0), reverse=True)
        
        # デバッグ: ソート後のスコアを表示
        print(f"\nArticle scores (after sorting):")
        for i, article in enumerate(all_articles[:5]):
            print(f"{i+1}. {article['title'][:50]}... - Score: {article.get('total_score', 0):.3f}")
        
        # HTML生成
        html_content = self.generate_html(all_articles)
        
        # HTMLファイル保存
        if self.save_html(html_content):
            print(f"\nIntegrated collection completed!")
            print(f"Total articles: {len(all_articles)}")
            print(f"X articles: {len(x_articles)}")
            print(f"RSS articles: {len(rss_articles)}")
            print("Please open docs/index.html in browser")
            return True
        
        return False


def main():
    collector = IntegratedCollector()
    success = collector.run()
    
    if success:
        print("\nIntegrated collection completed successfully")
    else:
        print("\nCollection failed")


if __name__ == "__main__":
    main()