#!/usr/bin/env python3
from rank_bm25 import BM25Okapi

# Simple test
corpus = [
    ['my', 'name', 'is', 'ashvin'],
    ['basemem', 'is', 'a', 'knowledge', 'graph', 'system']
]

bm25 = BM25Okapi(corpus)

# Test different queries
queries = [
    ['knowledge'],
    ['graph'],
    ['ashvin'],
    ['is'],
    ['knowledge', 'graph'],
]

for query in queries:
    scores = bm25.get_scores(query)
    print(f"Query {query}: {scores}")
