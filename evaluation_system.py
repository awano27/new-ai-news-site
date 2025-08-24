#!/usr/bin/env python3
"""
多層評価システム - 要件書準拠版
5つの独立した評価軸による多角的スコアリング
"""

import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import math


class MultiLayerEvaluator:
    """多層評価システム"""
    
    def __init__(self):
        self.HALF_LIFE_HOURS = 72  # 記事の価値半減期（72時間）
        self.weights = {
            'quality': 0.25,
            'relevance': 0.30,
            'temporal': 0.20,
            'trust': 0.15,
            'actionability': 0.10
        }
        
    def evaluate_article(self, article: Dict[str, Any], persona: str = "engineer") -> Dict[str, Any]:
        """記事の有益性を多層的に評価"""
        
        # Layer 1: コンテンツ品質スコア
        quality_score = self.assess_quality(article)
        
        # Layer 2: ペルソナ別関連性スコア
        relevance_score = self.calculate_relevance(article, persona)
        
        # Layer 3: 時間的価値スコア
        temporal_score = self.calculate_temporal_value(article)
        
        # Layer 4: 信頼性スコア（E-E-A-T準拠）
        trust_score = self.calculate_trust_score(article)
        
        # Layer 5: アクショナビリティスコア
        action_score = self.calculate_actionability(article, persona)
        
        # 重み付き総合スコア
        total_score = self.weighted_sum({
            'quality': quality_score,
            'relevance': relevance_score,
            'temporal': temporal_score,
            'trust': trust_score,
            'actionability': action_score
        })
        
        return {
            'total_score': total_score,
            'breakdown': {
                'quality': quality_score,
                'relevance': relevance_score,
                'temporal': temporal_score,
                'trust': trust_score,
                'actionability': action_score
            },
            'difficulty_analysis': self.assess_difficulty(article),
            'roi_analysis': self.calculate_roi(article, persona),
            'bias_analysis': self.assess_bias(article),
            'recommendation': self.get_recommendation(total_score)
        }
    
    def assess_quality(self, article: Dict[str, Any]) -> float:
        """コンテンツ品質評価"""
        score = 0.0
        
        # 1. テキスト品質（30%）
        text = f"{article.get('title', '')} {article.get('content', '')}"
        
        # 文字数による品質推定
        length_score = min(len(text) / 500, 1.0) * 0.3
        score += length_score
        
        # 技術キーワードの密度（40%）
        tech_keywords = [
            'algorithm', 'model', 'neural', 'deep learning', 'machine learning',
            'transformer', 'gpu', 'performance', 'benchmark', 'sota',
            'implementation', 'code', 'github', 'paper', 'research',
            'アルゴリズム', 'モデル', 'ニューラル', 'ディープラーニング', '機械学習',
            'トランスフォーマー', '性能', 'ベンチマーク', '実装', 'コード', '研究'
        ]
        
        keyword_count = sum(1 for kw in tech_keywords if kw.lower() in text.lower())
        keyword_score = min(keyword_count / 10, 1.0) * 0.4
        score += keyword_score
        
        # ソースの権威性（30%）
        source_score = 0.3
        if article.get('source_tier') == 1:
            source_score = 0.3
        elif 'MIT' in article.get('source', '') or 'arXiv' in article.get('source', ''):
            source_score = 0.25
        elif 'Reddit' in article.get('source', ''):
            source_score = 0.15
        else:
            source_score = 0.1
        
        score += source_score
        
        return min(score, 1.0)
    
    def calculate_relevance(self, article: Dict[str, Any], persona: str) -> float:
        """ペルソナ別関連性スコア"""
        text = f"{article.get('title', '')} {article.get('content', '')}"
        
        if persona == "engineer":
            return self.calculate_engineer_relevance(text)
        elif persona == "business":
            return self.calculate_business_relevance(text)
        else:
            return 0.5  # デフォルト
    
    def calculate_engineer_relevance(self, text: str) -> float:
        """エンジニア向け関連性"""
        engineer_keywords = {
            'high_value': [  # 高価値キーワード（0.15点）
                'implementation', 'code', 'github', 'tensorflow', 'pytorch',
                'optimization', 'performance', 'benchmark', 'sota', 'model',
                'architecture', 'training', 'inference', 'gpu', 'cuda',
                'foundation model', 'transformer', 'routing', 'router',
                '実装', 'コード', '最適化', '性能', 'モデル', 'アーキテクチャ'
            ],
            'medium_value': [  # 中価値キーワード（0.08点）
                'algorithm', 'neural', 'deep', 'learning', 'ai', 'ml',
                'research', 'paper', 'dataset', 'evaluation', 'llm',
                'machine learning', 'artificial intelligence', 'fine-tuning',
                'アルゴリズム', 'ニューラル', 'ディープ', '学習', '研究', '論文'
            ],
            'low_value': [  # 低価値キーワード（0.04点）
                'technology', 'innovation', 'future', 'trend', 'discussion',
                'question', 'help', 'advice', 'recommendation',
                '技術', 'イノベーション', '未来', 'トレンド'
            ]
        }
        
        score = 0.0
        text_lower = text.lower()
        
        for kw in engineer_keywords['high_value']:
            if kw.lower() in text_lower:
                score += 0.15
        
        for kw in engineer_keywords['medium_value']:
            if kw.lower() in text_lower:
                score += 0.08
        
        for kw in engineer_keywords['low_value']:
            if kw.lower() in text_lower:
                score += 0.04
        
        # 基礎スコア（AIやML関連の記事であれば最低0.2点）
        if any(base_kw in text_lower for base_kw in ['ai', 'ml', 'machine learning', 'model', 'algorithm']):
            score = max(score, 0.2)
        
        return min(score, 1.0)
    
    def calculate_business_relevance(self, text: str) -> float:
        """ビジネス向け関連性"""
        business_keywords = {
            'high_value': [  # 高価値キーワード（0.1点）
                'roi', 'revenue', 'cost', 'profit', 'market', 'business',
                'customer', 'user', 'growth', 'scale', 'enterprise',
                'investment', 'funding', 'valuation', 'startup',
                'ROI', '収益', 'コスト', '利益', '市場', 'ビジネス',
                '顧客', 'ユーザー', '成長', '投資', '資金調達'
            ],
            'medium_value': [  # 中価値キーワード（0.05点）
                'efficiency', 'productivity', 'automation', 'strategy',
                'competitive', 'advantage', 'disruption', 'transformation',
                '効率', '生産性', '自動化', '戦略', '競争', '優位性', '変革'
            ],
            'low_value': [  # 低価値キーワード（0.02点）
                'company', 'industry', 'trend', 'innovation',
                '企業', '業界', 'トレンド', 'イノベーション'
            ]
        }
        
        score = 0.0
        text_lower = text.lower()
        
        for kw in business_keywords['high_value']:
            if kw.lower() in text_lower:
                score += 0.15
        
        for kw in business_keywords['medium_value']:
            if kw.lower() in text_lower:
                score += 0.08
        
        for kw in business_keywords['low_value']:
            if kw.lower() in text_lower:
                score += 0.04
        
        # 基礎スコア（ビジネス関連記事であれば最低0.15点）
        if any(base_kw in text_lower for base_kw in ['business', 'market', 'company', 'industry', 'strategy']):
            score = max(score, 0.15)
        
        return min(score, 1.0)
    
    def calculate_temporal_value(self, article: Dict[str, Any]) -> float:
        """時間的価値評価（鮮度と持続的価値のバランス）"""
        
        # 記事の日付を取得
        pub_date_str = article.get('published_date', '')
        if not pub_date_str:
            return 0.5  # デフォルト値
        
        try:
            pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d')
            hours_since_publish = (datetime.now() - pub_date).total_seconds() / 3600
        except:
            return 0.5
        
        # 1. 鮮度スコア（指数減衰）
        freshness = math.exp(-hours_since_publish / self.HALF_LIFE_HOURS)
        
        # 2. 持続的価値（エバーグリーン度）
        evergreen_score = self.assess_evergreen_potential(article)
        
        # 鮮度と持続的価値のバランス
        temporal_score = 0.6 * freshness + 0.4 * evergreen_score
        
        return min(temporal_score, 1.0)
    
    def assess_evergreen_potential(self, article: Dict[str, Any]) -> float:
        """持続的価値の評価"""
        text = f"{article.get('title', '')} {article.get('content', '')}"
        
        # 持続的価値の高いキーワード
        evergreen_keywords = [
            'tutorial', 'guide', 'how to', 'best practices', 'framework',
            'architecture', 'design pattern', 'methodology', 'technique',
            'チュートリアル', 'ガイド', '方法', 'ベストプラクティス', 'フレームワーク'
        ]
        
        # 時限的価値のキーワード
        time_sensitive_keywords = [
            'breaking', 'just released', 'today', 'this week', 'latest',
            'announcement', 'launched', 'breaking news',
            '速報', '今日', '今週', '最新', '発表', 'ローンチ'
        ]
        
        evergreen_count = sum(1 for kw in evergreen_keywords if kw.lower() in text.lower())
        time_sensitive_count = sum(1 for kw in time_sensitive_keywords if kw.lower() in text.lower())
        
        # エバーグリーン要素が多いほど高スコア
        evergreen_boost = min(evergreen_count * 0.2, 0.8)
        time_penalty = min(time_sensitive_count * 0.1, 0.4)
        
        base_score = 0.5
        return max(base_score + evergreen_boost - time_penalty, 0.0)
    
    def calculate_trust_score(self, article: Dict[str, Any]) -> float:
        """信頼性スコア（E-E-A-T準拠）"""
        score = 0.0
        
        # Experience（経験）- ソースの専門性
        source = article.get('source', '')
        if any(exp_source in source for exp_source in [
            'MIT', 'Stanford', 'arXiv', 'Nature', 'Science',
            'OpenAI', 'DeepMind', 'Anthropic'
        ]):
            score += 0.3
        elif article.get('source_tier') == 1:
            score += 0.2
        else:
            score += 0.1
        
        # Expertise（専門知識）- 技術的深度
        text = f"{article.get('title', '')} {article.get('content', '')}"
        expert_indicators = [
            'experiment', 'evaluation', 'methodology', 'results',
            'comparison', 'benchmark', 'analysis', 'implementation',
            '実験', '評価', '手法', '結果', '比較', '分析', '実装'
        ]
        
        expert_count = sum(1 for ind in expert_indicators if ind.lower() in text.lower())
        score += min(expert_count * 0.05, 0.3)
        
        # Authoritativeness（権威性）- 被引用性の推定
        if 'github.com' in article.get('url', ''):
            score += 0.2
        if any(domain in article.get('url', '') for domain in [
            'arxiv.org', 'openai.com', 'deepmind.com'
        ]):
            score += 0.2
        
        return min(score, 1.0)
    
    def calculate_actionability(self, article: Dict[str, Any], persona: str) -> float:
        """アクショナビリティスコア"""
        text = f"{article.get('title', '')} {article.get('content', '')}"
        
        if persona == "engineer":
            action_keywords = [
                'implementation', 'code', 'tutorial', 'how to', 'guide',
                'example', 'demo', 'github', 'colab', 'notebook',
                '実装', 'コード', 'チュートリアル', '方法', 'ガイド', '例'
            ]
        else:  # business
            action_keywords = [
                'strategy', 'implementation', 'case study', 'roi', 'how to',
                'guide', 'framework', 'process', 'step', 'action',
                '戦略', '実装', 'ケーススタディ', 'ROI', '方法', 'プロセス'
            ]
        
        action_count = sum(1 for kw in action_keywords if kw.lower() in text.lower())
        
        # URLがあるかどうかも評価
        has_url = bool(article.get('url', '').strip())
        url_boost = 0.2 if has_url else 0.0
        
        actionability = min(action_count * 0.1, 0.8) + url_boost
        
        return min(actionability, 1.0)
    
    def assess_difficulty(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """実装難易度の評価"""
        text = f"{article.get('title', '')} {article.get('content', '')}"
        
        # 難易度指標
        beginner_keywords = ['tutorial', 'introduction', 'getting started', 'basic']
        intermediate_keywords = ['implementation', 'example', 'guide', 'how to']
        advanced_keywords = ['optimization', 'advanced', 'research', 'novel']
        research_keywords = ['paper', 'arxiv', 'research', 'sota', 'breakthrough']
        
        scores = {
            'beginner': sum(1 for kw in beginner_keywords if kw.lower() in text.lower()),
            'intermediate': sum(1 for kw in intermediate_keywords if kw.lower() in text.lower()),
            'advanced': sum(1 for kw in advanced_keywords if kw.lower() in text.lower()),
            'research': sum(1 for kw in research_keywords if kw.lower() in text.lower())
        }
        
        # 最も高いスコアの難易度を選択
        difficulty_level = max(scores, key=scores.get)
        
        # 実装準備度
        implementation_ready = bool(
            'github' in text.lower() or 
            'code' in text.lower() or 
            'implementation' in text.lower()
        )
        
        return {
            'difficulty_level': difficulty_level,
            'implementation_ready': implementation_ready,
            'github_repo': 'github' in text.lower()
        }
    
    def calculate_roi(self, article: Dict[str, Any], persona: str) -> Dict[str, Any]:
        """ROI分析"""
        text = f"{article.get('title', '')} {article.get('content', '')}"
        
        # ROI指標の推定
        high_roi_keywords = ['efficiency', 'productivity', 'automation', 'scale', 'cost reduction']
        medium_roi_keywords = ['improvement', 'optimization', 'enhancement', 'upgrade']
        
        high_count = sum(1 for kw in high_roi_keywords if kw.lower() in text.lower())
        medium_count = sum(1 for kw in medium_roi_keywords if kw.lower() in text.lower())
        
        # 簡易ROI計算
        roi_potential = high_count * 0.3 + medium_count * 0.1
        confidence_score = min(roi_potential, 1.0)
        
        # ペルソナ別調整
        if persona == "engineer":
            payback_months = max(3, 12 - high_count * 2)
            roi_percentage = min(100 + high_count * 50, 500)
        else:  # business
            payback_months = max(6, 18 - high_count * 3)
            roi_percentage = min(150 + high_count * 75, 800)
        
        return {
            'confidence_score': confidence_score,
            'payback_months': int(payback_months),
            'roi_percentage': int(roi_percentage)
        }
    
    def assess_bias(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """バイアス評価"""
        text = f"{article.get('title', '')} {article.get('content', '')}"
        
        # バイアス検出パターン
        bias_patterns = {
            'promotional': ['best', 'revolutionary', 'breakthrough', 'amazing', 'incredible'],
            'sensational': ['shocking', 'unbelievable', 'game-changing', '驚くべき', '革命的'],
            'absolute': ['always', 'never', 'all', 'none', 'every', 'すべて', '絶対']
        }
        
        detected_biases = []
        bias_count = 0
        
        for bias_type, keywords in bias_patterns.items():
            for kw in keywords:
                if kw.lower() in text.lower():
                    detected_biases.append(bias_type)
                    bias_count += 1
                    break
        
        # 中立性スコア（バイアスが少ないほど高い）
        neutrality_score = max(0.2, 1.0 - bias_count * 0.2)
        
        # 品質スコア（技術的内容があるほど高い）
        quality_indicators = ['analysis', 'evaluation', 'comparison', 'methodology']
        quality_count = sum(1 for qi in quality_indicators if qi.lower() in text.lower())
        quality_score = min(0.5 + quality_count * 0.125, 1.0)
        
        return {
            'neutrality_score': neutrality_score,
            'bias_count': len(set(detected_biases)),
            'quality_score': quality_score
        }
    
    def get_recommendation(self, total_score: float) -> str:
        """スコアに基づく推奨レベル"""
        if total_score >= 0.8:
            return "must_read"
        elif total_score >= 0.6:
            return "recommended"
        elif total_score >= 0.4:
            return "consider"
        else:
            return "skip"
    
    def weighted_sum(self, scores: Dict[str, float]) -> float:
        """重み付き合計スコア計算"""
        total = 0.0
        for component, score in scores.items():
            weight = self.weights.get(component, 0.0)
            total += score * weight
        
        return min(total, 1.0)