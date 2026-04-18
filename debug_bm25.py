#!/usr/bin/env python3
from src.basemem.storage.db import StorageManager

db = StorageManager("basemem.db")
corpus = db.get_all_nodes()

print("Nodes and their tokenization:")
for i, node in enumerate(corpus):
    tokens = (node.title.lower().split() + 
             node.content.lower().split() + 
             [k.lower() for k in node.keywords])
    print(f"\n{i}. {node.id}")
    print(f"   Tokens: {tokens}")
    print(f"   Token count: {len(tokens)}")

# Now test BM25
from rank_bm25 import BM25Okapi

tokenized = []
for node in corpus:
    tokens = (node.title.lower().split() + 
             node.content.lower().split() + 
             [k.lower() for k in node.keywords])
    tokenized.append(tokens)

bm25 = BM25Okapi(tokenized)

query = "knowledge graph system"
query_tokens = query.lower().split()
print(f"\n\nQuery: {query}")
print(f"Query tokens: {query_tokens}")

scores = bm25.get_scores(query_tokens)
print(f"\nBM25 scores:")
for i, score in enumerate(scores):
    print(f"  {i}: {score:.6f}")
