#!/usr/bin/env python3
from src.basemem.storage.db import StorageManager
from src.basemem.graph.engine import GraphEngine

db = StorageManager("basemem.db")
graph = GraphEngine(db)

nodes = db.get_all_nodes()
print(f"Total nodes: {len(nodes)}")

for node in nodes:
    print(f"\nNode: {node.id}")
    print(f"  Title: {node.title}")
    print(f"  Keywords: {node.keywords}")

# Test auto-linking manually
if len(nodes) >= 2:
    print(f"\n\nTesting auto-linking for {nodes[1].id}")
    edges = graph.auto_link_nodes(nodes[1].id, threshold=0.3)
    print(f"Created {len(edges)} edges")
    for edge in edges:
        print(f"  {edge.from_id} -> {edge.to_id} ({edge.edge_type.value})")
