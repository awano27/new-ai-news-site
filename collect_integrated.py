#!/usr/bin/env python3
"""
統合版記事収集システム
X記事 + RSS記事の両方を統合表示
"""

import requests
import json
import csv
try:
    import feedparser  # optional; skip RSS if unavailable
except Exception:
    feedparser = None
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
            # Fallback to local CSV if Google Sheet returns nothing
            if len(x_articles) == 0:
                print("⚠️ No X articles from Google Sheet. Trying local CSV fallback…")
                fallback = self.collect_x_from_local_csv()
                if fallback:
                    print(f"✅ Fallback X articles: {len(fallback)}")
                    return fallback
            return x_articles
        
        except Exception as e:
            print(f"X articles collection error: {str(e)}")
            # Fallback on exception as well
            fallback = self.collect_x_from_local_csv()
            if fallback:
                print(f"✅ Fallback X articles after error: {len(fallback)}")
                return fallback
            return []

    def collect_x_from_local_csv(self):
        """参考/x_articles.csv または x_articles_backup.csv からX記事を読み込むフォールバック"""
        try:
            ref_dir = self.project_root / '参考'
            primary = ref_dir / 'x_articles.csv'
            backup = ref_dir / 'x_articles_backup.csv'
            csv_path = None
            if primary.exists() and primary.stat().st_size > 0:
                csv_path = primary
            elif backup.exists() and backup.stat().st_size > 0:
                csv_path = backup
            else:
                print("❌ No local CSV found for X articles fallback")
                return []

            print(f"📂 Reading X articles from local CSV: {csv_path}")
            rows = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                sample = f.read(2048)
                f.seek(0)
                # Determine if file has headers; use DictReader if so
                has_header = any(h in sample for h in ['created_at', 'username', 'tweet_url', 'content'])
                if has_header:
                    reader = csv.DictReader(f)
                    for r in reader:
                        rows.append([
                            r.get('created_at',''),
                            r.get('username',''),
                            r.get('content',''),
                            r.get('link',''),
                            r.get('tweet_url','')
                        ])
                else:
                    reader = csv.reader(f)
                    for r in reader:
                        rows.append(r)

            # Skip header if present in first row
            if rows and isinstance(rows[0][0], str) and rows[0][0].lower().startswith('created'):
                rows = rows[1:]

            x_articles = []
            for row in rows:
                if not row or len(row) < 3:
                    continue
                created_at = (row[0] or '').strip()
                username = (row[1] or '').strip().replace('@','')
                content = (row[2] or '').strip()
                first_link = (row[3] or '').strip() if len(row) > 3 else ''
                tweet_link = (row[4] or '').strip() if len(row) > 4 else ''

                if not content or not username:
                    continue

                # AI-related filter
                if not self.is_ai_related(content):
                    continue

                article_url = first_link or tweet_link or (f"https://twitter.com/{username}")
                article = {
                    'id': f"x_{hashlib.md5(f'{username}_{content}'.encode()).hexdigest()[:8]}",
                    'title': self.extract_title(content),
                    'url': article_url,
                    'source': f'X(@{username})',
                    'source_tier': 2,
                    'published_date': self.parse_date(created_at) if created_at else datetime.now().strftime('%Y-%m-%d'),
                    'content': content[:200] + "..." if len(content) > 200 else content,
                    'tags': ['x_post', 'ai_2025', 'community']
                }

                engineer_eval = self.evaluator.evaluate_article(article, 'engineer')
                business_eval = self.evaluator.evaluate_article(article, 'business')
                article['evaluation'] = { 'engineer': engineer_eval, 'business': business_eval }
                article['total_score'] = engineer_eval['total_score']

                x_articles.append(article)
                if len(x_articles) >= 30:
                    break

            print(f"Local CSV X articles collected: {len(x_articles)}")
            return x_articles
        except Exception as e:
            print(f"Fallback CSV read error: {e}")
            return []
    
    def collect_rss_articles(self):
        """RSS記事を収集"""
        print("Collecting RSS articles...")
        if feedparser is None:
            print("feedparser が利用できないため、RSS収集をスキップします")
            return []
        
        rss_articles = []
        cutoff_date = datetime.utcnow() - timedelta(hours=48)  # 48時間以内のみ（naive UTC基準）
        
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
        """統合記事データからHTMLを生成（改善版テンプレート使用）"""
        print(f"Generating integrated HTML... ({len(all_articles)} articles total)")
        
        # 記事は既にソート済み（念のため再度ソート）
        all_articles.sort(key=lambda x: x.get('total_score', 0.0), reverse=True)
        
        # 上位記事のスコアを確認
        print(f"Top 3 articles by score:")
        for i, article in enumerate(all_articles[:3]):
            score = article.get('total_score', 0)
            print(f"{i+1}. {article['title'][:40]}... - Score: {score:.3f}")
        
        # クリーンなHTMLテンプレートを読み込み
        template_path = self.project_root / "docs" / "index_clean.html"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 記事データをJSONとして挿入
            articles_json = json.dumps(all_articles, ensure_ascii=False, indent=2)
            
            # プレースホルダーを実際のデータで置換
            html_content = template_content.replace(
                'const articles = [];',
                f'const articles = {articles_json};'
            )
            
            return html_content
            
        except FileNotFoundError:
            print("Warning: Clean template not found, using fallback template")
            # フォールバック: 改善版テンプレートを直接作成
            articles_json = json.dumps(all_articles, ensure_ascii=False, indent=2)
            
            html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily AI News – 改良版</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- Header with title and persona toggle -->
    <header class="header">
        <div class="container">
            <h1>Daily AI News</h1>
            <p>X記事とRSS記事をまとめた最新AIニュース</p>
            <!-- Persona toggle integrated in header -->
            <div class="persona-toggle">
                <button class="active" data-persona="engineer">技術者向け</button>
                <button data-persona="business">ビジネス向け</button>
            </div>
        </div>
    </header>

    <!-- Summary statistics -->
    <section class="summary-stats">
        <div class="container">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="value" id="stat-total">0</div>
                    <div class="label">記事数</div>
                </div>
                <div class="stat-item">
                    <div class="value" id="stat-avg-score">0%</div>
                    <div class="label">平均スコア</div>
                </div>
                <div class="stat-item">
                    <div class="value" id="stat-tier1">0</div>
                    <div class="label">高信頼ソース</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Filter panel -->
    <section class="filters">
        <div class="container">
            <div class="filter-row">
                <div class="filter-group">
                    <label for="source-tier-filter">ソース種別</label>
                    <select id="source-tier-filter">
                        <option value="all">すべて</option>
                        <option value="1">高信頼ソース</option>
                        <option value="2">一般ソース</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="min-score-filter">最低スコア</label>
                    <input type="range" id="min-score-filter" min="0" max="1" step="0.1" value="0" />
                </div>
                <div class="search-box">
                    <input id="search-input" type="text" placeholder="キーワードで検索…" />
                </div>
            </div>
        </div>
    </section>

    <!-- Articles container -->
    <main>
        <div class="container">
            <div class="articles-grid" id="articles-container"></div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">© 2025 Daily AI News – 改良版</div>
    </footer>

    <script>
        // Persona-specific metric labels
        const metricLabels = {{
            engineer: ['技術的新規性', '実装可能性', '再現性', '実務寄与', '学習価値'],
            business: ['事業影響度', '投資判断材料', '戦略的価値', '実現可能性', 'リスク評価']
        }};

        const breakdownOrder = {{
            engineer: ['temporal', 'relevance', 'trust', 'quality', 'actionability'],
            business: ['quality', 'relevance', 'trust', 'temporal', 'actionability']
        }};

        // Current real-time articles data
        const articles = {articles_json};

        let filteredArticles = [...articles];
        let currentPersona = 'engineer';

        // Human-readable names for source tiers
        const tierTexts = {{
            1: '高信頼ソース',
            2: '一般ソース'
        }};

        function renderArticles() {{
            const container = document.getElementById('articles-container');
            container.innerHTML = '';
            
            // Sort by recommendation priority first then by score
            const recPriority = {{ must_read: 0, recommended: 1, consider: 2, skip: 3 }};
            const sorted = [...filteredArticles].sort((a, b) => {{
                const aRec = (a.evaluation && a.evaluation[currentPersona] && a.evaluation[currentPersona].recommendation) || 'consider';
                const bRec = (b.evaluation && b.evaluation[currentPersona] && b.evaluation[currentPersona].recommendation) || 'consider';
                if (recPriority[aRec] !== recPriority[bRec]) {{
                    return recPriority[aRec] - recPriority[bRec];
                }}
                return getPersonaScore(b) - getPersonaScore(a);
            }});
            
            // Group by recommendation and insert headings for clarity
            let lastRec = null;
            sorted.forEach(article => {{
                const evalData = article.evaluation && article.evaluation[currentPersona];
                const rec = (evalData && evalData.recommendation) || 'consider';
                if (rec !== lastRec) {{
                    const heading = document.createElement('h2');
                    heading.className = `rec-heading rec-${{rec}}`;
                    heading.textContent = getRecommendationText(rec);
                    container.appendChild(heading);
                    lastRec = rec;
                }}
                container.appendChild(createArticleCard(article));
            }});
        }}

        function createArticleCard(article) {{
            const card = document.createElement('div');
            card.className = 'article-card';
            const evaluation = article.evaluation || {{}};
            const personaEval = evaluation[currentPersona] || {{}};
            const breakdown = personaEval.breakdown || {{}};
            const totalPercentage = Math.round((personaEval.total_score || 0) * 100);
            
            // Determine the order of breakdown keys for this persona
            const order = breakdownOrder[currentPersona] || ['quality','relevance','temporal','trust','actionability'];
            
            // Build HTML for breakdown items in the desired order
            let breakdownHtml = '';
            order.forEach((key, idx) => {{
                const val = Math.round(((breakdown[key] || 0) * 100));
                const label = (metricLabels[currentPersona] && metricLabels[currentPersona][idx]) || key;
                breakdownHtml += `<div class="score-item"><div class="score-value">${{val}}</div><div class="score-label">${{label}}</div></div>`;
            }});
            
            card.innerHTML = `
                <span class="source-tier tier-${{article.source_tier}}">${{tierTexts[article.source_tier] || ''}}</span>
                <h3 class="article-title">
                    <a href="${{article.url}}" target="_blank" rel="noopener noreferrer">${{escapeHtml(article.title)}}</a>
                </h3>
                <div class="article-meta">
                    <span>${{escapeHtml(article.source)}}</span> • <span>${{article.published_date}}</span>
                </div>
                <div class="article-content">${{escapeHtml(article.content)}}</div>
                <div class="evaluation-panel">
                    <div class="score-display">
                        <div class="total-score">${{totalPercentage}}</div>
                        <div class="score-label-text">総合評価</div>
                        <div class="score-bar"><div class="score-bar-fill" style="width: ${{totalPercentage}}%"></div></div>
                    </div>
                    <div class="score-breakdown">
                        ${{breakdownHtml}}
                    </div>
                    <div class="recommendation rec-${{personaEval.recommendation || 'consider'}}">
                        ${{getRecommendationText(personaEval.recommendation || 'consider')}}
                    </div>
                </div>
            `;
            return card;
        }}

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        function getRecommendationText(rec) {{
            const texts = {{ must_read: '必読', recommended: '推奨', consider: '検討', skip: 'スキップ' }};
            return texts[rec] || rec;
        }}

        function getPersonaScore(article) {{
            const evalData = article.evaluation && article.evaluation[currentPersona];
            return evalData ? evalData.total_score : 0;
        }}

        function applyFilters() {{
            const tierFilter = document.getElementById('source-tier-filter').value;
            const minScore = parseFloat(document.getElementById('min-score-filter').value || 0);
            const searchQuery = document.getElementById('search-input').value.toLowerCase();
            
            filteredArticles = articles.filter(article => {{
                if (tierFilter !== 'all' && article.source_tier !== parseInt(tierFilter)) return false;
                if (getPersonaScore(article) < minScore) return false;
                if (searchQuery) {{
                    const haystack = (article.title + article.content + article.source).toLowerCase();
                    if (!haystack.includes(searchQuery)) return false;
                }}
                return true;
            }});
            
            renderArticles();
            updateSummaryStats();
        }}

        function updateSummaryStats() {{
            const totalEl = document.getElementById('stat-total');
            const avgEl = document.getElementById('stat-avg-score');
            const tier1El = document.getElementById('stat-tier1');
            
            totalEl.textContent = filteredArticles.length;
            const avgScore = filteredArticles.reduce((sum, art) => sum + getPersonaScore(art), 0) / (filteredArticles.length || 1);
            avgEl.textContent = Math.round(avgScore * 100) + '%';
            const tier1Count = filteredArticles.filter(a => a.source_tier === 1).length;
            tier1El.textContent = tier1Count;
        }}

        // Event listeners
        document.getElementById('source-tier-filter').addEventListener('change', applyFilters);
        document.getElementById('min-score-filter').addEventListener('input', applyFilters);
        document.getElementById('search-input').addEventListener('input', applyFilters);

        // Attach persona toggle events on header
        document.querySelectorAll('.header .persona-toggle button').forEach(btn => {{
            btn.addEventListener('click', () => {{
                // update active class
                document.querySelectorAll('.header .persona-toggle button').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                // update global persona
                currentPersona = btn.dataset.persona;
                // re-apply filters and re-render
                applyFilters();
            }});
        }});

        // Initial render
        document.addEventListener('DOMContentLoaded', () => {{
            renderArticles();
            updateSummaryStats();
        }});
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
