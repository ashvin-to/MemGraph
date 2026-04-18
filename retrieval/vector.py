"""Vector retriever for semantic search"""

from typing import List, Tuple, Optional
import numpy as np
import logging
from pathlib import Path

try:
    import faiss
except ImportError:
    faiss = None

from sentence_transformers import SentenceTransformer

from modelsimport Node
from storage.db import StorageManager

logger = logging.getLogger(__name__)


class VectorRetriever:
    """Vector-based retriever for semantic similarity search"""

    def __init__(self, storage: StorageManager, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize vector retriever
        
        Args:
            storage: StorageManager instance
            model_name: Sentence transformer model name
        """
        self.storage = storage
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_embedding_dimension()
        self.node_embeddings: Optional[np.ndarray] = None
        self.node_ids: List[str] = []
        self.index: Optional[faiss.IndexFlatL2] = None
        
        self._build_index()  # Always build embeddings for numpy fallback

    def _build_index(self):
        """Build FAISS index from node embeddings"""
        nodes = self.storage.get_all_nodes()
        
        if not nodes:
            logger.info("No nodes to index")
            return

        # Generate embeddings
        texts = [f"{n.title} {n.content}" for n in nodes]
        embeddings = self.model.encode(texts, convert_to_numpy=True)

        # Build FAISS index
        self.node_embeddings = embeddings.astype(np.float32)
        self.node_ids = [n.id for n in nodes]

        if faiss:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.index.add(self.node_embeddings)
            logger.info(f"Built FAISS index with {len(nodes)} documents")

    def search(self, query: str, top_k: int = 50) -> List[Tuple[str, float]]:
        """
        Search using vector similarity
        
        Returns list of (node_id, similarity_score) tuples
        """
        if not self.node_ids:
            return []

        # Encode query
        query_embedding = self.model.encode(query, convert_to_numpy=True).astype(np.float32)

        if faiss and self.index:
            # FAISS search (L2 distance)
            distances, indices = self.index.search(
                np.array([query_embedding]),
                min(top_k, len(self.node_ids))
            )

            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx >= 0:  # Valid result
                    # Convert L2 distance to similarity score (0-1)
                    similarity = 1.0 / (1.0 + distance)
                    results.append((self.node_ids[idx], similarity))

            logger.debug(f"Vector search returned {len(results)} results")
            return results
        else:
            # Fallback: numpy cosine similarity
            if self.node_embeddings is None:
                return []

            similarities = np.dot(self.node_embeddings, query_embedding) / (
                np.linalg.norm(self.node_embeddings, axis=1) * 
                np.linalg.norm(query_embedding) + 1e-8
            )

            # Get top k (sorted by similarity, highest first)
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                sim = float(similarities[idx])
                # Convert cosine similarity from [-1, 1] to [0, 1]
                normalized_sim = (sim + 1.0) / 2.0
                if normalized_sim > 0:
                    results.append((self.node_ids[idx], normalized_sim))

            return results

    def rebuild(self):
        """Rebuild index"""
        self._build_index()
