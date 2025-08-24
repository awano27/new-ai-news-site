#!/usr/bin/env python3
"""
X記事収集器 - Google Spreadsheetsからの日次データ取得
"""

import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib
from pathlib import Path
import sys

# プロジェクト設定
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
    from src.models.article import Article, TechnicalMetadata, BusinessMetadata, ImplementationCost
except ImportError:
    # フォールバック用の最小モデル
    class Article:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

class XSourceCollector:
    """Google Spreadsheetsからx記事を取得"""
    
    def __init__(self):
        self.spreadsheet_url = "https://docs.google.com/spreadsheets/d/1uuLKCLIJw--a1vCcO6UGxSpBiLTtN8uGl2cdMb6wcfg/edit?gid=0#gid=0"
        self.csv_export_url = "https://docs.google.com/spreadsheets/d/1uuLKCLIJw--a1vCcO6UGxSpBiLTtN8uGl2cdMb6wcfg/export?format=csv&gid=0&access_token=&headers=false"
    
    def parse_x_articles(self) -> List[Article]:
        """Google SpreadsheetsからX記事を取得・解析"""
        articles = []
        
        try:
            print("📡 X記事データを取得中...")
            print(f"🔗 URL: {self.csv_export_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/csv,text/plain,*/*',
                'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
            }
            
            # 複数のCSV取得方法を試行
            csv_urls = [
                self.csv_export_url,
                f"https://docs.google.com/spreadsheets/d/1uuLKCLIJw--a1vCcO6UGxSpBiLTtN8uGl2cdMb6wcfg/gviz/tq?tqx=out:csv&gid=0",
                f"https://docs.google.com/spreadsheets/d/1uuLKCLIJw--a1vCcO6UGxSpBiLTtN8uGl2cdMb6wcfg/export?format=csv"
            ]
            
            response = None
            for csv_url in csv_urls:
                try:
                    print(f"🔄 試行中: {csv_url}")
                    response = requests.get(csv_url, headers=headers, timeout=15, allow_redirects=True)
                    
                    # 詳細なエラー情報を表示
                    print(f"    ステータス: {response.status_code}")
                    print(f"    Content-Length: {len(response.content)} bytes")
                    print(f"    Content-Type: {response.headers.get('content-type', 'N/A')}")
                    
                    if response.status_code == 200 and len(response.text) > 10:
                        print("✅ データ取得成功")
                        
                        # エンコーディング情報
                        encoding = response.encoding or 'utf-8'
                        print(f"    検出エンコーディング: {encoding}")
                        
                        # 内容プレビュー
                        preview = response.text[:200].replace('\n', '\\n')
                        print(f"    内容プレビュー: {preview}...")
                        
                        # 文字化け検出と修正（より積極的）
                        if '�' in response.text or 'Ã' in response.text or 'ã' in response.text[:100]:
                            print("    ⚠️ 文字化けを検出、エンコーディングを修正中...")
                            encodings_to_try = ['utf-8', 'shift-jis', 'euc-jp', 'cp932', 'iso-2022-jp']
                            for enc in encodings_to_try:
                                try:
                                    corrected_content = response.content.decode(enc, errors='ignore')
                                    # 日本語文字が正しく表示されるかテスト
                                    if 'AI' in corrected_content and ('の' in corrected_content or '、' in corrected_content):
                                        print(f"    ✅ {enc}でのデコードが成功")
                                        # responseオブジェクトの内容を更新
                                        response.encoding = 'utf-8'
                                        response._content = corrected_content.encode('utf-8')
                                        break
                                except Exception as decode_error:
                                    print(f"    ⚠️ {enc}デコード失敗: {str(decode_error)[:30]}")
                                    continue
                        
                        break
                    else:
                        print(f"    ❌ 無効なレスポンス: {response.text[:100]}...")
                        
                except Exception as e:
                    print(f"  ❌ リクエストエラー: {str(e)}")
                    continue
            
            if not response or response.status_code != 200 or len(response.text) <= 10:
                print(f"❌ 全ての方法でSpreadsheets取得に失敗")
                
                # 代替手段の詳細な説明
                print("\n💡 手動でCSVをダウンロードしてください:")
                print("  1. スプレッドシートを開く")
                print("  2. 「ファイル」→「ダウンロード」→「カンマ区切り値(.csv)」")
                print(f"  3. ダウンロードしたファイルを以下に保存:")
                print(f"     {project_root / '参考' / 'x_articles.csv'}")
                print("  4. 再実行してください")
                
                return articles
            
            csv_content = response.text
            lines = csv_content.strip().split('\n')
            
            print(f"📄 {len(lines)}行のデータを取得")
            
            print(f"  📋 処理開始: ヘッダー行をスキップして解析...")
            processed_count = 0
            
            for i, line in enumerate(lines[1:], 1):  # ヘッダー行をスキップ
                try:
                    # 空行や短すぎる行をスキップ
                    if len(line.strip()) < 10:
                        continue
                        
                    # CSV解析（カンマ区切りも対応）
                    if '|' in line:
                        parts = [p.strip().strip('"') for p in line.split('|')]
                    else:
                        # 標準的なCSV解析
                        import csv
                        import io
                        csv_reader = csv.reader(io.StringIO(line))
                        try:
                            parts = next(csv_reader)
                        except:
                            continue
                    
                    if len(parts) < 3:  # 最低限のデータが必要
                        continue
                    
                    processed_count += 1
                    if processed_count % 50 == 0:
                        print(f"    📊 処理済み: {processed_count}行")
                    
                    created_at_str = parts[0].strip()
                    username = parts[1].strip().replace('@', '')
                    post_content = parts[2].strip()
                    first_link = parts[3].strip() if len(parts) > 3 else ""
                    tweet_link = parts[4].strip() if len(parts) > 4 else ""
                    
                    # X記事特有の文字エンコーディング処理
                    import html
                    post_content = html.unescape(post_content)
                    # UTF-8として正しく処理
                    try:
                        if isinstance(post_content, bytes):
                            post_content = post_content.decode('utf-8', errors='ignore')
                    except:
                        pass
                    
                    # 日付解析（timezone対応）
                    try:
                        if 'T' in created_at_str and created_at_str:
                            # ISO形式の日付処理
                            if created_at_str.endswith('Z'):
                                created_at_str = created_at_str[:-1] + '+00:00'
                            pub_date = datetime.fromisoformat(created_at_str)
                            # timezone-naiveに変換
                            if pub_date.tzinfo is not None:
                                pub_date = pub_date.replace(tzinfo=None)
                        else:
                            pub_date = datetime.now()
                    except Exception as e:
                        print(f"    ⚠️ 日付解析エラー: {created_at_str[:20]} - 現在日付を使用")
                        pub_date = datetime.now()
                    
                    # 7日以内の記事のみ（X記事は速報性重視）
                    if pub_date < datetime.now() - timedelta(days=7):
                        continue
                    
                    # AIフィルタリング
                    if not self.is_ai_related(post_content):
                        continue
                    
                    # 記事作成
                    article_id = f"x_{hashlib.md5((username + post_content).encode()).hexdigest()[:8]}"
                    
                    # URL処理 - 外部リンクがない場合はツイートリンクを使用
                    article_url = first_link if first_link else tweet_link
                    if not article_url:
                        # ツイートリンクもない場合は、ユーザー名から推測
                        article_url = f"https://twitter.com/{username}"
                    
                    article = Article(
                        id=article_id,
                        title=self.extract_title_from_post(post_content),
                        url=article_url,
                        source=f"X(@{username})",
                        source_tier=2,  # X記事は信頼性tier 2
                        published_date=pub_date,
                        content=post_content[:300] + "..." if len(post_content) > 300 else post_content,
                        tags=['x_post', 'community', 'ai_2025']
                    )
                    
                    # メタデータ
                    article.technical = TechnicalMetadata(
                        implementation_ready='github' in post_content.lower() or 'code' in post_content.lower(),
                        code_available='github.com' in post_content.lower(),
                        reproducibility_score=0.6  # X記事は中程度の再現性
                    )
                    
                    article.business = BusinessMetadata(
                        market_size="グローバル",
                        growth_rate=70,  # X記事は速報性が高い
                        implementation_cost=ImplementationCost.LOW
                    )
                    
                    # 評価スコア
                    ai_score = self.calculate_ai_relevance_score(post_content)
                    article.evaluation = {
                        "engineer": {"total_score": min(1.0, ai_score + 0.1)},  # X記事はエンジニア向け
                        "business": {"total_score": min(1.0, ai_score * 0.8)}  # ビジネス向けは少し低め
                    }
                    
                    articles.append(article)
                    print(f"  ✅ 収集: @{username} - {self.extract_title_from_post(post_content)[:40]}...")
                    
                except Exception as e:
                    print(f"  ⚠️ 行{i}処理エラー: {str(e)[:50]}")
                    continue
            
            print(f"✅ X記事収集完了: {len(articles)}記事")
            
            # デバッグ情報
            if len(articles) == 0:
                print(f"  🔍 デバッグ情報:")
                print(f"    • 処理済み行数: {processed_count}")
                print(f"    • AI関連でフィルタされた可能性があります")
                print(f"    • 日付フィルタ: 7日以内の記事のみ")
                
                # 最初の5行をサンプル表示
                if len(lines) > 5:
                    print(f"  📋 データサンプル（最初の3行）:")
                    for i, line in enumerate(lines[1:4]):
                        parts = line.split('|')
                        if len(parts) >= 3:
                            print(f"    {i+1}. ユーザー: {parts[1][:20]}... 内容: {parts[2][:30]}...")
                        else:
                            print(f"    {i+1}. 解析不可: {line[:50]}...")
            
        except Exception as e:
            print(f"❌ X記事収集エラー: {str(e)}")
        
        return articles
    
    def is_ai_related(self, content: str) -> bool:
        """AI関連判定（2025年対応）"""
        text = content.lower()
        
        ai_keywords = [
            # 基本AI用語
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
            'neural network', 'neural net', 'computer vision', 'nlp', 'natural language processing',
            
            # 大規模言語モデル
            'llm', 'large language model', 'chatgpt', 'gpt-4', 'gpt-5', 'gpt4', 'gpt5',
            'claude', 'gemini', 'bard', 'llama', 'mistral', 'openai', 'anthropic',
            
            # 生成AI
            'generative ai', 'gen ai', 'stable diffusion', 'midjourney', 'dall-e', 'sora',
            'diffusion', 'text-to-image', 'image generation', 'text generation',
            
            # 2025年技術トレンド
            'rag', 'retrieval augmented generation', 'fine-tuning', 'multimodal',
            'ai agent', 'ai agents', 'transformer', 'attention', 'foundation model',
            'prompt engineering', 'in-context learning', 'few-shot', 'zero-shot',
            
            # AI企業・プロダクト
            'microsoft copilot', 'github copilot', 'huggingface', 'nvidia', 'meta ai',
            'google ai', 'deepmind', 'pytorch', 'tensorflow', 'langchain',
            
            # 日本語AI用語
            '人工知能', 'AI', '機械学習', 'ディープラーニング', 'チャットGPT', 
            'LLM', '生成AI', 'AIエージェント', 'ファインチューニング', 'プロンプト'
        ]
        
        return any(keyword in text for keyword in ai_keywords)
    
    def extract_title_from_post(self, content: str) -> str:
        """投稿内容からタイトルを抽出"""
        # 最初の文または50文字以内
        sentences = re.split(r'[.!?。！？]', content)
        if sentences and len(sentences[0]) <= 100:
            return sentences[0].strip()
        return content[:50] + "..." if len(content) > 50 else content
    
    def calculate_ai_relevance_score(self, content: str) -> float:
        """AI関連度スコア計算"""
        text = content.lower()
        
        # 高価値キーワード
        high_value_keywords = ['gpt-4', 'claude', 'gemini', 'rag', 'multimodal', 'ai agent']
        score = 0.5
        
        for keyword in high_value_keywords:
            if keyword in text:
                score += 0.1
        
        # リンクがある場合はボーナス
        if 'http' in content:
            score += 0.05
        
        return min(1.0, score)

def main():
    """テスト実行"""
    collector = XSourceCollector()
    articles = collector.parse_x_articles()
    
    print(f"\n📊 X記事収集結果:")
    print(f"  • 総記事数: {len(articles)}")
    
    if articles:
        print(f"\n🏆 トップ5記事:")
        for i, article in enumerate(articles[:5]):
            print(f"  {i+1}. {article.source} - {article.title}")
            print(f"     スコア: {article.evaluation['engineer']['total_score']:.2f}")

if __name__ == "__main__":
    main()