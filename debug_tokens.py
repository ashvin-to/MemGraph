#!/usr/bin/env python3
from src.basemem.storage.db import StorageManager
from src.basemem.retrieval.bm25 import BM25Retriever

db = StorageManager("basemem.db")
retriever = BM25Retriever(db)

print(f"BM25 Index:")
print(f"  Corpus size: {len(retriever.corpus)}")
print(f"\nTokens in index:")
for i, node in enumerate(retriever.corpus):
    print(f"  {i}. {node.id}")
    print(f"     Title: {node.title}")
    print(f"     Content: {node.content}")
    print(f"     Keywords: {node.keywords}")

print(f"\nBM25 Index tokens:")
if hasattr(retriever.bm25, 'corpus'):
    for i, tokens in enumerate(retriever.bm25.corpus):
        print(f"  {i}: {tokens[:10]}...")  # Show first 10 tokens
