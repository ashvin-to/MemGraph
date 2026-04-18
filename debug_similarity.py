#!/usr/bin/env python3
from src.basemem.storage.db import StorageManager
from src.basemem.graph.engine import GraphEngine

db = StorageManager("basemem.db")
graph = GraphEngine(db)

nodes = db.get_all_nodes()

# Manual similarity calculation
node1 = nodes[0]
node2 = nodes[1]

print(f"Node 1: {node1.title}")
print(f"  Keywords: {node1.keywords}")

print(f"\nNode 2: {node2.title}")
print(f"  Keywords: {node2.keywords}")

# Calculate keyword similarity manually
new_keywords = set(node2.keywords)
existing_keywords = set(node1.keywords)

print(f"\nKeyword overlap calculation:")
print(f"  New keywords: {new_keywords}")
print(f"  Existing keywords: {existing_keywords}")
print(f"  Intersection: {new_keywords & existing_keywords}")

overlap = len(new_keywords & existing_keywords)
max_keywords = max(len(new_keywords), len(existing_keywords))
keyword_similarity = overlap / max_keywords if max_keywords > 0 else 0

print(f"  Overlap: {overlap}, Max: {max_keywords}")
print(f"  Keyword similarity: {keyword_similarity:.2f} (weight 0.4 = {keyword_similarity * 0.4:.2f})")

# Token overlap
new_text = (node2.title + " " + node2.content).lower()
existing_text = (node1.title + " " + node1.content).lower()

new_tokens = set(new_text.split())
existing_tokens = set(existing_text.split())

print(f"\nToken overlap calculation:")
token_overlap = len(new_tokens & existing_tokens)
max_tokens = max(len(new_tokens), len(existing_tokens))
token_similarity = token_overlap / max_tokens if max_tokens > 0 else 0

print(f"  Overlap: {token_overlap}, Max: {max_tokens}")
print(f"  Token similarity: {token_similarity:.2f} (weight 0.3 = {token_similarity * 0.3:.2f})")

total_similarity = keyword_similarity * 0.4 + token_similarity * 0.3
print(f"\nTotal similarity: {total_similarity:.2f}")
print(f"Threshold: 0.4")
print(f"Would link: {total_similarity >= 0.4}")
