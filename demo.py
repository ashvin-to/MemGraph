"""Demo script showing how to use BaseMem"""

import asyncio
from pathlib import Path

from src.basemem.storage.db import StorageManager
from src.basemem.models import Node, NodeType, Edge, EdgeType
from src.basemem.retrieval.engine import RetrievalEngine
from src.basemem.graph.engine import GraphEngine
from src.basemem.orchestrator.context import ContextOrchestrator
from src.basemem.processing.pipeline import ProcessingPipeline


async def main():
    """Run demo of BaseMem system"""

    # Initialize storage
    db_path = Path("demo_basemem.db")
    if db_path.exists():
        db_path.unlink()

    storage = StorageManager(str(db_path))

    print("=" * 60)
    print("BaseMem Demo")
    print("=" * 60)

    # 1. Add some initial knowledge
    print("\n📚 Adding knowledge...")
    pipeline = ProcessingPipeline(storage)

    texts = [
        "Binary search is an algorithm that finds a target value in a sorted array. "
        "It works by repeatedly dividing the search space in half.",
        "Machine learning is a subset of artificial intelligence that enables systems "
        "to learn from data without being explicitly programmed.",
        "Graph algorithms are essential in computer science for solving problems on networks "
        "like finding shortest paths and detecting cycles.",
        "Neural networks are computational models inspired by biological neurons. "
        "They form the backbone of modern deep learning.",
    ]

    all_nodes = []
    for i, text in enumerate(texts):
        nodes = await pipeline.ingest_text(text, source=f"demo_{i}")
        all_nodes.extend(nodes)

    print(f"✓ Created {len(all_nodes)} nodes")

    # 2. Test retrieval
    print("\n🔍 Testing Retrieval Engine...")
    retrieval = RetrievalEngine(storage)

    queries = [
        "What is binary search?",
        "Tell me about machine learning",
        "Graph algorithms",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        results = retrieval.retrieve(query, top_k=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. [{result.source}] {result.node.title[:50]}")
            print(f"     Score: {result.score:.3f}")

    # 3. Test graph operations
    print("\n🔗 Testing Graph Engine...")
    graph = GraphEngine(storage)

    if all_nodes:
        node_id = all_nodes[0].id
        neighbors = graph.get_neighbors(node_id, depth=1)
        print(f"Node: {all_nodes[0].title[:50]}")
        print(f"Neighbors: {len(neighbors)}")

    # 4. Test context orchestration
    print("\n📖 Testing Context Orchestrator...")
    orchestrator = ContextOrchestrator(storage, token_budget=1000)

    test_query = "What is machine learning and how does it work?"
    context = orchestrator.orchestrate(test_query)

    print(f"\nQuery: {test_query}")
    print("\nFormatted Context:")
    print(context.to_prompt_format())
    print(f"\nContext Stats: {len(context.source_nodes)} nodes, {context.token_count} tokens")

    # 5. Statistics
    print("\n📊 Database Statistics")
    nodes = storage.get_all_nodes()
    edges = storage.get_edges()

    print(f"Total Nodes: {len(nodes)}")
    print(f"Total Edges: {len(edges)}")

    node_types = {}
    for node in nodes:
        node_type = node.node_type.value
        node_types[node_type] = node_types.get(node_type, 0) + 1

    print("\nNodes by type:")
    for ntype, count in node_types.items():
        print(f"  {ntype}: {count}")

    storage.close()
    print("\n✓ Demo complete!")


if __name__ == "__main__":
    asyncio.run(main())
