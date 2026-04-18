"""Add test nodes with different types to the database"""

from src.basemem.storage.db import StorageManager
from src.basemem.models import Node, NodeType, Edge, EdgeType
from datetime import datetime

# Initialize storage
storage = StorageManager("basemem.db")

# Create test nodes with different types
test_nodes = [
    Node(
        id="test_concept_1",
        title="Machine Learning",
        content="Machine learning is a subset of artificial intelligence that enables systems to learn from data without being explicitly programmed.",
        node_type=NodeType.CONCEPT,
        keywords=["machine learning", "AI", "data", "algorithms"],
        weight=1.5,
    ),
    Node(
        id="test_fact_1",
        title="Python was created in 1991",
        content="Python is a high-level programming language created by Guido van Rossum in 1991.",
        node_type=NodeType.FACT,
        keywords=["python", "programming", "1991"],
        weight=1.2,
    ),
    Node(
        id="test_summary_1",
        title="Overview of Deep Learning",
        content="Deep learning uses neural networks with multiple layers to process and learn from data automatically.",
        node_type=NodeType.SUMMARY,
        keywords=["deep learning", "neural networks", "overview"],
        weight=1.3,
    ),
    Node(
        id="test_task_1",
        title="Implement a decision tree classifier",
        content="Task: Build a decision tree model that can classify iris flowers based on features.",
        node_type=NodeType.TASK,
        keywords=["decision tree", "classification", "iris"],
        weight=1.0,
    ),
    Node(
        id="test_question_1",
        title="How do neural networks learn?",
        content="Question: Explain the mechanisms by which neural networks update weights and biases to minimize loss.",
        node_type=NodeType.QUESTION,
        keywords=["neural networks", "learning", "weights"],
        weight=1.1,
    ),
    Node(
        id="test_example_1",
        title="Example: Image classification with CNN",
        content="Example: Using a Convolutional Neural Network to classify images from the CIFAR-10 dataset.",
        node_type=NodeType.EXAMPLE,
        keywords=["CNN", "image classification", "CIFAR-10"],
        weight=1.0,
    ),
    Node(
        id="test_concept_2",
        title="Graph Theory",
        content="Graph theory is the mathematical study of graphs, which are structures used to model pairwise relations between objects.",
        node_type=NodeType.CONCEPT,
        keywords=["graph", "theory", "networks", "nodes", "edges"],
        weight=1.4,
    ),
]

# Add nodes to storage
print("Adding test nodes with different types...")
for node in test_nodes:
    storage.add_node(node)
    print(f"✓ Added {node.node_type.value.upper():12} - {node.title}")

# Create some edges between nodes
edges = [
    Edge(from_id="test_concept_1", to_id="test_summary_1", edge_type=EdgeType.IS_A, weight=0.9),
    Edge(from_id="test_fact_1", to_id="test_concept_2", edge_type=EdgeType.RELATED_TO, weight=0.7),
    Edge(from_id="test_question_1", to_id="test_example_1", edge_type=EdgeType.RELATED_TO, weight=0.8),
    Edge(from_id="test_task_1", to_id="test_concept_1", edge_type=EdgeType.DEPENDS_ON, weight=0.9),
    Edge(from_id="test_example_1", to_id="test_fact_1", edge_type=EdgeType.DERIVED_FROM, weight=0.6),
]

print("\nAdding edges...")
for edge in edges:
    storage.add_edge(edge)
    print(f"✓ Added edge: {edge.from_id} -> {edge.to_id} ({edge.edge_type.value})")

print("\n✓ Test nodes added successfully!")
print("\nRefresh your browser to see the new colored nodes:")
print("  file:///mnt/Storage/BaseMem/graph_visualization.html")
