#!/usr/bin/env python3
"""
URL フィルター方式での X 記事収集
有効な URL を持つ記事のみを収集・表示
"""

import requests
import json
import csv
from io import StringIO
from datetime import datetime
from pathlib import Path
import hashlib
import re


class URLFilteredCollector:
    """URL フィルター方式での記事収集器"""
    
    def __init__(self):
        self.spreadsheet_url = "https://docs.google.com/spreadsheets/d/1uuLKCLIJw--a1vCcO6UGxSpBiLTtN8uGl2cdMb6wcfg/export?format=csv&gid=0"
        self.project_root = Path(__file__).parent
        self.docs_path = self.project_root / "docs"
        
    def fetch_and_filter_articles(self):
        """Google Spreadsheetsからデータを取得し、有効URLのみフィルター"""
        print("Fetching data from Google Spreadsheets...")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.spreadsheet_url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"Data fetch failed: {response.status_code}")
                return []
            
            # 文字エンコーディングを正しく処理
            try:
                # まずUTF-8で試行
                csv_text = response.content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # UTF-8がだめならISO-8859-1で試行
                    csv_text = response.content.decode('iso-8859-1')
                except UnicodeDecodeError:
                    # それでもだめならShift-JISで試行
                    csv_text = response.content.decode('shift-jis', errors='ignore')
            
            print(f"Data fetch success: {len(csv_text)} chars")
            
            # CSVを解析
            reader = csv.reader(StringIO(csv_text))
            headers = next(reader)  # ヘッダー行をスキップ
            
            valid_articles = []
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
                import html
                content = html.unescape(content)
                username = html.unescape(username)
                
                # URLフィルタリング - 有効なURLがある記事のみ
                article_url = None
                if first_link and self.is_valid_url(first_link):
                    article_url = first_link
                elif tweet_link and self.is_valid_url(tweet_link):
                    article_url = tweet_link
                
                # 有効なURLがない場合はスキップ
                if not article_url:
                    continue
                
                # AI関連でない場合はスキップ
                if not self.is_ai_related(content):
                    continue
                
                # 記事データを作成
                article = {
                    'id': hashlib.md5(f"{username}_{content}".encode()).hexdigest()[:8],
                    'title': self.extract_title(content),
                    'url': article_url,
                    'source': f'X(@{username})',
                    'source_tier': 2,
                    'published_date': self.parse_date(created_at),
                    'content': content[:200] + "..." if len(content) > 200 else content,
                    'tags': ['x_post', 'ai_2025', 'community'],
                    'evaluation': {
                        'engineer': {'total_score': 0.75},
                        'business': {'total_score': 0.65}
                    }
                }
                
                valid_articles.append(article)
                print(f"Valid article: @{username} - {article['title'][:40]}...")
                
                if len(valid_articles) >= 50:  # 上限50記事
                    break
            
            print(f"\nProcessing results:")
            print(f"  - Processed rows: {processed_count}")
            print(f"  - Valid articles: {len(valid_articles)}")
            
            return valid_articles
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return []
    
    def is_valid_url(self, url):
        """URLの有効性をチェック"""
        if not url:
            return False
        
        # 基本的なURL形式チェック
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    def is_ai_related(self, content):
        """AI関連コンテンツかどうか判定"""
        text = content.lower()
        ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
            'chatgpt', 'gpt-4', 'claude', 'gemini', 'llm', 'openai', 'anthropic',
            'neural network', 'transformer', 'diffusion', 'rag',
            '人工知能', 'AI', '機械学習', 'ディープラーニング', '生成AI', 'チャットGPT'
        ]
        
        return any(keyword in text for keyword in ai_keywords)
    
    def extract_title(self, content):
        """コンテンツからタイトルを抽出"""
        # 最初の文または50文字以内
        sentences = re.split(r'[.!?。！？\n]', content)
        if sentences and len(sentences[0]) <= 80:
            return sentences[0].strip()
        return content[:50] + "..." if len(content) > 50 else content
    
    def parse_date(self, date_string):
        """日付文字列を解析"""
        try:
            if 'T' in date_string:
                # ISO形式
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
    
    def generate_html(self, articles):
        """記事データからHTMLを生成"""
        print(f"Generating HTML... ({len(articles)} articles)")
        
        articles_json = json.dumps(articles, ensure_ascii=False, indent=2)
        
        html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily AI News - URL フィルター版</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .header {{ background: #1a1a1a; color: white; padding: 20px 0; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .header h1 {{ font-size: 2rem; margin-bottom: 10px; }}
        .header p {{ opacity: 0.8; }}
        .stats {{ background: white; margin: 20px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .stat-item {{ text-align: center; }}
        .stat-value {{ font-size: 2rem; font-weight: bold; color: #2563eb; }}
        .stat-label {{ color: #6b7280; }}
        .articles-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; margin: 20px 0; }}
        .article-card {{ background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; transition: transform 0.2s; }}
        .article-card:hover {{ transform: translateY(-2px); }}
        .article-header {{ padding: 20px; }}
        .article-title {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 10px; line-height: 1.4; }}
        .article-title a {{ color: #1a1a1a; text-decoration: none; }}
        .article-title a:hover {{ color: #2563eb; }}
        .article-meta {{ display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; color: #6b7280; margin-bottom: 15px; }}
        .source {{ background: #2563eb; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; }}
        .article-content {{ padding: 0 20px 20px; color: #4b5563; line-height: 1.5; }}
        .article-actions {{ padding: 20px; border-top: 1px solid #e5e7eb; }}
        .read-more {{ background: #2563eb; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; }}
        .read-more:hover {{ background: #1d4ed8; }}
        .footer {{ background: #1a1a1a; color: white; text-align: center; padding: 40px 20px; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>Daily AI News - URL フィルター版</h1>
            <p>有効なURLを持つX記事のみを表示</p>
        </div>
    </header>

    <div class="container">
        <div class="stats">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value" id="total-count">{len(articles)}</div>
                    <div class="stat-label">総記事数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="url-valid">100%</div>
                    <div class="stat-label">有効URL率</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="ai-related">100%</div>
                    <div class="stat-label">AI関連度</div>
                </div>
            </div>
        </div>

        <div class="articles-grid" id="articles-container">
            <!-- 記事はJavaScriptで動的生成 -->
        </div>
    </div>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 Daily AI News - URL フィルター版</p>
        </div>
    </footer>

    <script>
        // 記事データ
        const articles = {articles_json};
        
        function renderArticles() {{
            const container = document.getElementById('articles-container');
            container.innerHTML = '';
            
            articles.forEach(article => {{
                const card = document.createElement('div');
                card.className = 'article-card';
                
                // HTMLエスケープ処理
                const escapeHtml = (text) => {{
                    const div = document.createElement('div');
                    div.textContent = text;
                    return div.innerHTML;
                }};
                
                card.innerHTML = `
                    <div class="article-header">
                        <h3 class="article-title">
                            <a href="${{encodeURI(article.url)}}" target="_blank" rel="noopener noreferrer">
                                ${{escapeHtml(article.title)}}
                            </a>
                        </h3>
                        <div class="article-meta">
                            <span class="source">${{escapeHtml(article.source)}}</span>
                            <span>${{article.published_date}}</span>
                        </div>
                    </div>
                    <div class="article-content">
                        ${{escapeHtml(article.content)}}
                    </div>
                    <div class="article-actions">
                        <a href="${{encodeURI(article.url)}}" class="read-more" target="_blank">記事を読む</a>
                    </div>
                `;
                
                container.appendChild(card);
            }});
        }}
        
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
            # ディレクトリが存在しない場合は作成
            self.docs_path.mkdir(exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                f.write(html_content)
            print(f"HTML file saved: {output_path}")
            return True
        except Exception as e:
            print(f"HTML save error: {str(e)}")
            return False
    
    def run(self):
        """メイン処理実行"""
        print("Starting URL filtered article collection...")
        
        # 記事を収集・フィルター
        articles = self.fetch_and_filter_articles()
        
        if not articles:
            print("No valid articles found")
            return False
        
        # HTML生成
        html_content = self.generate_html(articles)
        
        # HTMLファイル保存
        if self.save_html(html_content):
            print(f"\nCompleted! {len(articles)} valid articles displayed")
            print("Please open docs/index.html in browser")
            return True
        
        return False


def main():
    """メイン関数"""
    collector = URLFilteredCollector()
    success = collector.run()
    
    if success:
        print("\nURL filtered collection completed successfully")
    else:
        print("\nCollection failed")


if __name__ == "__main__":
    main()