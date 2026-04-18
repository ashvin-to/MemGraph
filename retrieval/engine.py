"""Hybrid retrieval engine combining BM25 and vector search"""

from typing import List, Dict, Set
import logging

from modelsimport Node, RetrievalResult
from storage.db import StorageManager
from .bm25 import BM25Retriever
from .vector import VectorRetriever

logger = logging.getLogger(__name__)


class RetrievalEngine:
    """Hybrid retrieval combining BM25 and semantic search"""

    def __init__(self, storage: StorageManager):
        """Initialize retrieval engine"""
        self.storage = storage
        self.bm25 = BM25Retriever(storage)
        self.vector = VectorRetriever(storage)

    def retrieve(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """
        Hybrid retrieval: BM25 + Vector search + Reranking
        
        Pipeline:
        1. BM25 search (top 50)
        2. Vector search (top 50)
        3. Merge and deduplicate
        4. Rerank (top 10)
        """
        # Step 1: BM25 search
        bm25_results = self.bm25.search(query, top_k=50)
        bm25_dict = {node_id: score for node_id, score in bm25_results}

        # Step 2: Vector search
        vector_results = self.vector.search(query, top_k=50)
        vector_dict = {node_id: score for node_id, score in vector_results}

        # Step 3: Merge and deduplicate
        merged = self._merge_results(bm25_dict, vector_dict)

        # Step 4: Rerank and get top k
        final_results = []
        for node_id, combined_score in sorted(
            merged.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]:
            node = self.storage.get_node(node_id)
            if node:
                source = "combined"
                if node_id in bm25_dict and node_id in vector_dict:
                    source = "combined"
                elif node_id in bm25_dict:
                    source = "bm25"
                else:
                    source = "vector"

                result = RetrievalResult(
                    node=node,
                    score=combined_score,
                    source=source,
                )
                final_results.append(result)

        logger.info(f"Retrieval returned {len(final_results)} results")
        return final_results

    @staticmethod
    def _merge_results(
        bm25_dict: Dict[str, float],
        vector_dict: Dict[str, float]
    ) -> Dict[str, float]:
        """Merge BM25 and vector search results"""
        all_ids = set(bm25_dict.keys()) | set(vector_dict.keys())
        merged = {}

        # Normalize scores to 0-1 range
        max_bm25 = max(bm25_dict.values()) if bm25_dict else 1
        max_vector = max(vector_dict.values()) if vector_dict else 1

        for node_id in all_ids:
            bm25_score = bm25_dict.get(node_id, 0) / max_bm25 if max_bm25 > 0 else 0
            vector_score = vector_dict.get(node_id, 0) / max_vector if max_vector > 0 else 0

            # Weighted combination (50-50)
            merged[node_id] = 0.5 * bm25_score + 0.5 * vector_score

        return merged

    def rebuild_indexes(self):
        """Rebuild all indexes (call after bulk ingestion)"""
        self.bm25.rebuild()
        self.vector.rebuild()
        logger.info("Rebuilt all retrieval indexes")
