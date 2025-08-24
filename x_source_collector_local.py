#!/usr/bin/env python3
"""
X記事収集器 - ローカルCSVファイル読み込み版
"""

import re
import csv
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

class XSourceCollectorLocal:
    """ローカルCSVファイルからX記事を読み込み"""
    
    def __init__(self):
        self.csv_file_path = project_root / "参考" / "x_articles.csv"
        # デフォルトのサンプルデータ
        self.default_articles = self.create_sample_x_articles()
    
    def create_sample_x_articles(self) -> List[Article]:
        """サンプルX記事データ"""
        sample_data = [
            {
                "created_at": "2025-01-23T10:00:00Z",
                "username": "AndrewYNg",
                "content": "RAG (Retrieval Augmented Generation) is revolutionizing how AI systems handle knowledge. New paper shows 40% improvement in factual accuracy. This could be the key to solving hallucinations in LLMs. #AI #MachineLearning",
                "link": "https://arxiv.org/abs/2501.12345",
                "tweet_url": "https://twitter.com/AndrewYNg/status/123456789"
            },
            {
                "created_at": "2025-01-23T14:30:00Z", 
                "username": "ylecun",
                "content": "Multimodal AI models are showing incredible progress. New Claude can now understand complex diagrams and generate code from sketches. The future of human-AI interaction is visual. 🔥",
                "link": "https://github.com/anthropics/claude-multimodal",
                "tweet_url": "https://twitter.com/ylecun/status/123456790"
            },
            {
                "created_at": "2025-01-23T16:15:00Z",
                "username": "karpathy",
                "content": "AI Agents are the next frontier. OpenAI's new agent framework can autonomously debug code, manage tasks, and even write documentation. We're moving from tools to colleagues. Thread 🧵",
                "link": "https://openai.com/blog/ai-agents-2025",
                "tweet_url": "https://twitter.com/karpathy/status/123456791"
            }
        ]
        
        articles = []
        for data in sample_data:
            article = self.create_article_from_data(data)
            if article:
                articles.append(article)
        
        return articles
    
    def parse_x_articles(self) -> List[Article]:
        """X記事を取得・解析"""
        articles = []
        
        print("📡 X記事データを取得中...")
        
        # ローカルCSVファイルを確認
        if self.csv_file_path.exists():
            print(f"📂 ローカルファイルから読み込み: {self.csv_file_path}")
            articles = self.read_from_csv()
        else:
            print("📂 ローカルCSVファイルが見つかりません")
            print(f"💡 次の場所にCSVファイルを保存してください: {self.csv_file_path}")
            print("🔢 フォーマット: created_at,username,content,link,tweet_url")
            print("\n🎯 サンプルX記事データを使用します...")
            articles = self.default_articles
        
        if articles:
            print(f"✅ X記事収集完了: {len(articles)}記事")
        else:
            print("⚠️ X記事は取得できませんでした")
        
        return articles
    
    def read_from_csv(self) -> List[Article]:
        """CSVファイルからデータを読み込み"""
        articles = []
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    data = {
                        'created_at': row.get('created_at', ''),
                        'username': row.get('username', ''),
                        'content': row.get('content', ''),
                        'link': row.get('link', ''),
                        'tweet_url': row.get('tweet_url', '')
                    }
                    
                    article = self.create_article_from_data(data)
                    if article:
                        articles.append(article)
                        
        except Exception as e:
            print(f"❌ CSVファイル読み込みエラー: {str(e)}")
            
        return articles
    
    def create_article_from_data(self, data: Dict) -> Optional[Article]:
        """データからArticleオブジェクトを作成"""
        try:
            # 日付解析
            try:
                if 'T' in data['created_at']:
                    pub_date = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
                else:
                    pub_date = datetime.now()
            except:
                pub_date = datetime.now()
            
            # 3日以内の記事のみ
            if pub_date < datetime.now() - timedelta(days=3):
                return None
            
            content = data['content']
            username = data['username']
            
            # AIフィルタリング
            if not self.is_ai_related(content):
                return None
            
            # 記事作成
            article_id = f"x_{hashlib.md5((username + content).encode()).hexdigest()[:8]}"
            
            article = Article(
                id=article_id,
                title=self.extract_title_from_post(content),
                url=data['link'] or data['tweet_url'],
                source=f"X(@{username})",
                source_tier=2,  # X記事は信頼性tier 2
                published_date=pub_date,
                content=content[:300] + "..." if len(content) > 300 else content,
                tags=['x_post', 'community', 'ai_2025']
            )
            
            # メタデータ
            article.technical = TechnicalMetadata(
                implementation_ready='github' in content.lower() or 'code' in content.lower(),
                code_available='github.com' in content.lower(),
                reproducibility_score=0.6
            )
            
            article.business = BusinessMetadata(
                market_size="グローバル",
                growth_rate=70,
                implementation_cost=ImplementationCost.LOW
            )
            
            # 評価スコア
            ai_score = self.calculate_ai_relevance_score(content)
            article.evaluation = {
                "engineer": {"total_score": min(1.0, ai_score + 0.1)},
                "business": {"total_score": min(1.0, ai_score * 0.8)}
            }
            
            return article
            
        except Exception as e:
            print(f"⚠️ 記事作成エラー: {str(e)[:50]}")
            return None
    
    def is_ai_related(self, content: str) -> bool:
        """AI関連判定（2025年対応）"""
        text = content.lower()
        
        ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
            'neural network', 'llm', 'large language model', 'chatgpt', 'gpt-4', 'gpt-5',
            'claude', 'gemini', 'bard', 'llama', 'mistral', 'openai',
            'generative ai', 'gen ai', 'stable diffusion', 'midjourney', 'dall-e', 'sora',
            'rag', 'retrieval augmented generation', 'fine-tuning', 'multimodal',
            'ai agent', 'transformer', 'attention', 'foundation model'
        ]
        
        return any(keyword in text for keyword in ai_keywords)
    
    def extract_title_from_post(self, content: str) -> str:
        """投稿内容からタイトルを抽出"""
        sentences = re.split(r'[.!?。！？]', content)
        if sentences and len(sentences[0]) <= 100:
            return sentences[0].strip()
        return content[:50] + "..." if len(content) > 50 else content
    
    def calculate_ai_relevance_score(self, content: str) -> float:
        """AI関連度スコア計算"""
        text = content.lower()
        
        high_value_keywords = ['gpt-4', 'claude', 'gemini', 'rag', 'multimodal', 'ai agent']
        score = 0.6
        
        for keyword in high_value_keywords:
            if keyword in text:
                score += 0.08
        
        if 'http' in content:
            score += 0.05
        
        return min(1.0, score)
    
    def create_sample_csv(self):
        """サンプルCSVファイルを作成"""
        self.csv_file_path.parent.mkdir(exist_ok=True)
        
        sample_csv_content = '''created_at,username,content,link,tweet_url
2025-01-23T10:00:00Z,AndrewYNg,"RAG (Retrieval Augmented Generation) is revolutionizing how AI systems handle knowledge. New paper shows 40% improvement in factual accuracy. #AI",https://arxiv.org/abs/2501.12345,https://twitter.com/AndrewYNg/status/123456789
2025-01-23T14:30:00Z,ylecun,"Multimodal AI models are showing incredible progress. New Claude can now understand complex diagrams and generate code from sketches. 🔥",https://github.com/anthropics/claude-multimodal,https://twitter.com/ylecun/status/123456790
2025-01-23T16:15:00Z,karpathy,"AI Agents are the next frontier. OpenAI's new agent framework can autonomously debug code and manage tasks. Thread 🧵",https://openai.com/blog/ai-agents-2025,https://twitter.com/karpathy/status/123456791'''
        
        with open(self.csv_file_path, 'w', encoding='utf-8') as f:
            f.write(sample_csv_content)
        
        print(f"✅ サンプルCSVファイルを作成しました: {self.csv_file_path}")

def main():
    """テスト実行"""
    collector = XSourceCollectorLocal()
    
    # サンプルCSVファイル作成オプション
    if not collector.csv_file_path.exists():
        print("📝 サンプルCSVファイルを作成しますか？ (y/n): ", end="")
        if input().lower().startswith('y'):
            collector.create_sample_csv()
    
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