"""Async workers for the processing pipeline (Zero-Model Version)"""

import asyncio
import logging
import uuid
from typing import List, Optional

from modelsimport Node, NodeType, Edge, EdgeType
from storage.db import StorageManager
from graph.engine import GraphEngine

logger = logging.getLogger(__name__)

class IngestWorker:
    """Worker for ingesting and processing raw text into knowledge nodes (Pure SQLite)"""

    def __init__(self, storage: StorageManager):
        self.storage = storage
        self.graph = GraphEngine(storage)

    async def process_text(
        self,
        text: str,
        source: str = "user_input",
        node_type: NodeType = NodeType.CONVERSATION
    ) -> List[Node]:
        """
        Process raw text into knowledge nodes. 
        Uses Keyword-Gravity for linking (Zero RAM).
        """
        # Step 1: Semantic chunking (simple sentence split)
        chunks = self._chunk_text(text)
        logger.info(f"Created {len(chunks)} chunks from input text")

        created_nodes = []
        for i, chunk in enumerate(chunks):
            node_id = f"{source}_{uuid.uuid4().hex[:8]}"
            node = self._create_node(chunk, node_id, node_type)
            created_nodes.append(node)
            self.storage.add_node(node)
            
            # Step 2: Auto-link using Keyword Gravity
            self.graph.auto_link_nodes(node.id, threshold=0.25)

        logger.info(f"Created {len(created_nodes)} nodes")
        return created_nodes

    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into manageable chunks by length (No NLTK needed)"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1
            if current_length >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def _create_node(
        self,
        content: str,
        node_id: str,
        node_type: NodeType
    ) -> Node:
        """Create a node from content"""
        title = content[:50] if len(content) > 50 else content
        keywords = self._extract_keywords(content)

        node = Node(
            id=node_id,
            title=title,
            content=content,
            node_type=node_type,
            keywords=keywords,
        )
        return node

    @staticmethod
    def _extract_keywords(text: str, top_k: int = 8) -> List[str]:
        """Extract keywords from text (Dumb frequency-based approach)"""
        stop_words = {"the", "and", "this", "that", "with", "from", "your", "have", "been", "will"}
        words = [w.lower().strip(".,!?:;\"") for w in text.split()]
        keywords = [w for w in words if len(w) > 4 and w not in stop_words]
        
        # Return unique keywords
        return list(set(keywords))[:top_k]
