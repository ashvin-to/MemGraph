#!/usr/bin/env python3
from src.basemem.storage.db import StorageManager
from src.basemem.retrieval.bm25 import BM25Retriever
from src.basemem.retrieval.vector import VectorRetriever

db = StorageManager("basemem.db")
bm25 = BM25Retriever(db)
vector = VectorRetriever(db)

query = "knowledge graph system"

bm25_results = bm25.search(query, top_k=50)
vector_results = vector.search(query, top_k=50)

print(f"Query: {query}\n")
print("BM25 results:")
for node_id, score in bm25_results:
    print(f"  {node_id}: {score:.4f}")

print("\nVector results:")
for node_id, score in vector_results:
    print(f"  {node_id}: {score:.4f}")

print("\nMerging (50% BM25 + 50% Vector):")
bm25_dict = {node_id: score for node_id, score in bm25_results}
vector_dict = {node_id: score for node_id, score in vector_results}

max_bm25 = max(bm25_dict.values()) if bm25_dict else 1
max_vector = max(vector_dict.values()) if vector_dict else 1

print(f"  max_bm25: {max_bm25}")
print(f"  max_vector: {max_vector}")

all_ids = set(bm25_dict.keys()) | set(vector_dict.keys())
for node_id in all_ids:
    bm25_norm = bm25_dict.get(node_id, 0) / max_bm25 if max_bm25 > 0 else 0
    vector_norm = vector_dict.get(node_id, 0) / max_vector if max_vector > 0 else 0
    combined = 0.5 * bm25_norm + 0.5 * vector_norm
    print(f"  {node_id}: BM25={bm25_norm:.4f}, Vector={vector_norm:.4f}, Combined={combined:.4f}")
