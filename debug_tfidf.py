#!/usr/bin/env python3
from src.basemem.storage.db import StorageManager
from src.basemem.retrieval.bm25 import BM25Retriever

db = StorageManager("basemem.db")
retriever = BM25Retriever(db)

print(f"TF-IDF vectors:")
for i, (node, vector) in enumerate(zip(retriever.corpus, retriever.doc_vectors)):
    print(f"\n{i}. {node.id}")
    print(f"   Vector: {vector}")

# Test search
query = "knowledge graph system"
query_tokens = query.lower().split()
print(f"\n\nQuery: {query}")
print(f"Query tokens: {query_tokens}")

scores = []
for doc_idx, doc_vector in enumerate(retriever.doc_vectors):
    score = 0.0
    for token in query_tokens:
        if token in doc_vector:
            score += doc_vector[token]
    scores.append(score)
    print(f"Doc {doc_idx} score: {score}")
