#!/usr/bin/env python3
from src.basemem.storage.db import StorageManager
from src.basemem.retrieval.bm25 import BM25Retriever

db = StorageManager("basemem.db")
retriever = BM25Retriever(db)

# Get raw scores
query = "knowledge graph system"
tokens = query.lower().split()
scores = retriever.bm25.get_scores(tokens)

print(f"Query: {query}")
print(f"Tokens: {tokens}")
print(f"\nRaw scores for each node:")
for i, (node, score) in enumerate(zip(retriever.corpus, scores)):
    print(f"  {i}. {node.id}: {score:.6f}")
