"""Hybrid search engine combining multiple search methods."""

import asyncio
import numpy as np
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from collections import defaultdict

from src.config.settings import Settings
from src.models.article import Article


@dataclass
class SearchResult:
    """Search result with metadata."""
    article_id: str
    score: float
    relevance_type: str  # 'keyword', 'semantic', 'entity', 'graph'
    matched_terms: List[str] = None
    explanation: str = ""


class HybridSearchEngine:
    """Hybrid search engine combining BM25, semantic, and entity-based search."""
    
    def __init__(self, settings: Settings):
        """Initialize search engine."""
        self.settings = settings
        self.articles: Dict[str, Article] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self.inverted_index: Dict[str, List[str]] = defaultdict(list)
        self.entity_index: Dict[str, List[str]] = defaultdict(list)
        
        # Initialize models (mock for now)
        self.embedding_model = None
        self.reranker_model = None
    
    async def index_articles(self, articles: List[Article]):
        """Index articles for search."""
        for article in articles:
            self.articles[article.id] = article
            await self._index_article(article)
    
    async def _index_article(self, article: Article):
        """Index a single article."""
        # Build inverted index for keyword search
        content = f"{article.title} {article.content}".lower()
        words = self._tokenize(content)
        
        for word in set(words):  # Use set to avoid duplicates
            self.inverted_index[word].append(article.id)
        
        # Index entities
        for entity in article.entities.companies + article.entities.technologies:
            entity_lower = entity.lower()
            self.entity_index[entity_lower].append(article.id)
    
    def _tokenize(self, text: str) -> List[str]:
        """Basic tokenization."""
        import re
        # Simple tokenization - split on non-alphanumeric, remove short words
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if len(w) >= 3]
    
    async def search(self, query: str, filters: Optional[Dict] = None, persona: Optional[str] = None) -> List[SearchResult]:
        """Main search function combining multiple methods."""
        if not query.strip():
            return []
        
        # 1. BM25 keyword search
        keyword_results = self.bm25_search(query)
        
        # 2. Semantic search (mock implementation)
        semantic_results = await self.semantic_search(query)
        
        # 3. Entity-based search
        entities = self.extract_entities(query)
        entity_results = await self.entity_search(entities)
        
        # 4. Merge and combine results
        combined_results = self.merge_results({
            "keyword": keyword_results,
            "semantic": semantic_results,
            "entity": entity_results
        })
        
        # 5. Apply persona optimization
        if persona:
            combined_results = self.apply_persona_optimization(combined_results, persona)
        
        # 6. Apply filters
        if filters:
            combined_results = self._apply_filters(combined_results, filters)
        
        # 7. Rerank results
        final_results = await self.rerank(combined_results, query)
        
        return final_results[:self.settings.search_top_k]
    
    def bm25_search(self, query: str, documents: Optional[List[Dict]] = None) -> List[SearchResult]:
        """BM25 keyword search implementation."""
        query_terms = self._tokenize(query)
        
        if documents is None:
            # Search in indexed articles
            candidate_docs = set()
            for term in query_terms:
                if term in self.inverted_index:
                    candidate_docs.update(self.inverted_index[term])
            documents = [{"id": doc_id, "content": ""} for doc_id in candidate_docs]
        
        scores = {}
        k1, b = 1.5, 0.75  # BM25 parameters
        
        # Calculate document frequencies
        total_docs = len(self.articles) if self.articles else len(documents)
        
        for doc in documents:
            doc_id = doc["id"]
            if doc_id in self.articles:
                article = self.articles[doc_id]
                doc_text = f"{article.title} {article.content}".lower()
            else:
                doc_text = doc.get("content", "").lower()
            
            doc_terms = self._tokenize(doc_text)
            doc_length = len(doc_terms)
            
            score = 0
            for term in query_terms:
                if term in doc_terms:
                    tf = doc_terms.count(term)
                    df = len(self.inverted_index.get(term, []))
                    if df > 0:
                        idf = np.log((total_docs - df + 0.5) / (df + 0.5))
                        score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_length / 50))
            
            if score > 0:
                scores[doc_id] = score
        
        # Convert to SearchResult objects
        results = [
            SearchResult(
                article_id=doc_id,
                score=min(1.0, score / 10),  # Normalize score
                relevance_type="keyword",
                matched_terms=query_terms,
                explanation=f"BM25 match for terms: {', '.join(query_terms)}"
            )
            for doc_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return results
    
    async def semantic_search(self, query: str) -> List[SearchResult]:
        """Semantic search using embeddings (mock implementation)."""
        # Mock implementation - would use actual embedding model
        results = []
        
        # Simulate semantic similarity
        for article_id, article in self.articles.items():
            # Simple heuristic: check for semantic similarity indicators
            similarity = self._calculate_mock_similarity(query, article)
            
            if similarity > 0.3:
                results.append(SearchResult(
                    article_id=article_id,
                    score=similarity,
                    relevance_type="semantic",
                    explanation=f"Semantic similarity: {similarity:.3f}"
                ))
        
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    def _calculate_mock_similarity(self, query: str, article: Article) -> float:
        """Mock semantic similarity calculation."""
        query_lower = query.lower()
        content_lower = f"{article.title} {article.content}".lower()
        
        # Simple overlap-based similarity
        query_words = set(self._tokenize(query_lower))
        content_words = set(self._tokenize(content_lower))
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(content_words))
        similarity = overlap / len(query_words)
        
        # Boost for title matches
        title_words = set(self._tokenize(article.title.lower()))
        title_overlap = len(query_words.intersection(title_words))
        if title_overlap > 0:
            similarity += 0.3 * (title_overlap / len(query_words))
        
        return min(1.0, similarity)
    
    async def entity_search(self, entities: Dict[str, List[str]]) -> List[SearchResult]:
        """Entity-based search."""
        results = []
        
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                entity_lower = entity.lower()
                if entity_lower in self.entity_index:
                    for article_id in self.entity_index[entity_lower]:
                        results.append(SearchResult(
                            article_id=article_id,
                            score=0.8,  # High score for entity matches
                            relevance_type="entity",
                            matched_terms=[entity],
                            explanation=f"Entity match: {entity} ({entity_type})"
                        ))
        
        return results
    
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract entities from query (basic implementation)."""
        entities = {
            "companies": [],
            "technologies": [],
            "people": [],
            "concepts": []
        }
        
        # Simple entity recognition based on capitalization and known terms
        words = query.split()
        
        # Known companies
        known_companies = ["openai", "google", "microsoft", "meta", "anthropic", "deepmind"]
        for company in known_companies:
            if company.lower() in query.lower():
                entities["companies"].append(company.title())
        
        # Known technologies
        known_tech = ["gpt", "bert", "transformer", "pytorch", "tensorflow", "llm", "nlp", "cv"]
        for tech in known_tech:
            if tech.lower() in query.lower():
                entities["technologies"].append(tech.upper())
        
        # Capitalized words that might be proper nouns
        for word in words:
            if word[0].isupper() and len(word) > 3:
                if word.lower() not in ["the", "and", "for", "with"]:
                    entities["concepts"].append(word)
        
        return entities
    
    def merge_results(self, results_by_type: Dict[str, List[SearchResult]]) -> List[SearchResult]:
        """Merge results from different search methods."""
        merged = {}
        
        for search_type, results in results_by_type.items():
            for result in results:
                article_id = result.article_id
                
                if article_id not in merged:
                    merged[article_id] = SearchResult(
                        article_id=article_id,
                        score=0.0,
                        relevance_type="combined",
                        matched_terms=[],
                        explanation=""
                    )
                
                # Combine scores with weights
                weight = self.settings.search_hybrid_weight if search_type == "keyword" else (1 - self.settings.search_hybrid_weight) / 2
                merged[article_id].score += weight * result.score
                
                if result.matched_terms:
                    merged[article_id].matched_terms.extend(result.matched_terms)
                
                if merged[article_id].explanation:
                    merged[article_id].explanation += f"; {result.explanation}"
                else:
                    merged[article_id].explanation = result.explanation
        
        # Remove duplicates from matched_terms
        for result in merged.values():
            if result.matched_terms:
                result.matched_terms = list(set(result.matched_terms))
        
        return sorted(merged.values(), key=lambda x: x.score, reverse=True)
    
    def apply_persona_optimization(self, results: List[SearchResult], persona: str) -> List[SearchResult]:
        """Apply persona-specific optimization."""
        for result in results:
            if result.article_id in self.articles:
                article = self.articles[result.article_id]
                boost = self._calculate_persona_boost(article, persona)
                result.score *= boost
        
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    def _calculate_persona_boost(self, article: Article, persona: str) -> float:
        """Calculate persona-specific boost factor."""
        if persona == "engineer":
            boost = 1.0
            if article.technical.implementation_ready:
                boost += 0.2
            if article.technical.code_available:
                boost += 0.3
            if article.technical.paper_link:
                boost += 0.1
            return boost
        
        elif persona == "business":
            boost = 1.0
            if article.business.roi_indicators:
                boost += 0.3
            if article.business.case_studies:
                boost += 0.2
            if article.business.funding_info:
                boost += 0.1
            return boost
        
        return 1.0
    
    def _apply_filters(self, results: List[SearchResult], filters: Dict) -> List[SearchResult]:
        """Apply search filters."""
        filtered = []
        
        for result in results:
            if result.article_id not in self.articles:
                continue
            
            article = self.articles[result.article_id]
            
            # Source tier filter
            if "source_tier" in filters and article.source_tier != filters["source_tier"]:
                continue
            
            # Minimum score filter
            if "min_score" in filters and result.score < filters["min_score"]:
                continue
            
            # Date range filter
            if "date_range" in filters:
                # Implementation would check article.published_date
                pass
            
            filtered.append(result)
        
        return filtered
    
    async def rerank(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Rerank results using cross-encoder (mock implementation)."""
        # Mock reranking - would use actual cross-encoder model
        # For now, just return results sorted by score
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    # Additional utility methods for comprehensive search functionality
    
    def get_related_articles(self, article_id: str, limit: int = 5) -> List[SearchResult]:
        """Find articles related to the given article."""
        if article_id not in self.articles:
            return []
        
        article = self.articles[article_id]
        
        # Use article title and entities as query
        query_parts = [article.title]
        query_parts.extend(article.entities.companies)
        query_parts.extend(article.entities.technologies)
        
        query = " ".join(query_parts)
        
        # Search and filter out the original article
        results = asyncio.run(self.search(query))
        filtered_results = [r for r in results if r.article_id != article_id]
        
        return filtered_results[:limit]
    
    def get_trending_topics(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get trending topics based on recent articles."""
        from collections import Counter
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_articles = [
            article for article in self.articles.values()
            if article.published_date and article.published_date > cutoff_date
        ]
        
        # Count entity occurrences
        all_entities = []
        for article in recent_articles:
            all_entities.extend(article.entities.companies)
            all_entities.extend(article.entities.technologies)
            all_entities.extend(article.entities.concepts)
        
        trending = Counter(all_entities).most_common(10)
        
        return [{"topic": topic, "count": count} for topic, count in trending]