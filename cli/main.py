"""Main CLI interface using Click"""

import click
import asyncio
import json
from pathlib import Path
import logging

from storage.db import StorageManager
from retrieval.engine import RetrievalEngine
from graph.engine import GraphEngine
from orchestrator.context import ContextOrchestrator
from processing.pipeline import ProcessingPipeline
from visualization.terminal import TerminalGraphVisualizer
from modelsimport NodeType

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@click.group()
@click.option('--db', default='basemem.db', help='Database file path')
@click.pass_context
def cli(ctx, db):
    """BaseMem: AI Knowledge Base System"""
    ctx.ensure_object(dict)
    ctx.obj['db'] = db
    ctx.obj['storage'] = StorageManager(db)


@cli.command()
@click.argument('text')
@click.option('--source', default='cli', help='Source of the text')
@click.pass_context
def add(ctx, text, source):
    """Add text to knowledge base"""
    storage = ctx.obj['storage']
    graph_engine = GraphEngine(storage)
    pipeline = ProcessingPipeline(storage)

    async def process():
        nodes = await pipeline.ingest_text(text, source=source)
        
        # Auto-link new nodes (lowered threshold to 0.2 for better connectivity)
        total_edges = 0
        for node in nodes:
            edges = graph_engine.auto_link_nodes(node.id, threshold=0.2)
            total_edges += len(edges)
        
        click.echo(f"✓ Added {len(nodes)} nodes")
        for node in nodes:
            click.echo(f"  - {node.id[:8]}: {node.title}")
        
        if total_edges > 0:
            click.echo(f"✓ Auto-linked {total_edges} relationships")

    asyncio.run(process())


@cli.command()
@click.argument('query')
@click.option('--top-k', default=10, help='Number of results')
@click.pass_context
def search(ctx, query, top_k):
    """Search knowledge base"""
    storage = ctx.obj['storage']
    retrieval = RetrievalEngine(storage)

    results = retrieval.retrieve(query, top_k=top_k)

    if not results:
        click.echo("No results found")
        return

    click.echo(f"\n📚 Found {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        click.echo(f"{i}. [{result.source.upper()}] {result.node.title}")
        click.echo(f"   Score: {result.score:.3f} | Type: {result.node.node_type.value}")
        click.echo(f"   {result.node.content[:80]}...")
        click.echo()


@cli.command()
@click.argument('query')
@click.option('--token-budget', default=2000, help='Token budget for context')
@click.pass_context
def ask(ctx, query, token_budget):
    """Ask a question (RAG pipeline)"""
    storage = ctx.obj['storage']
    orchestrator = ContextOrchestrator(storage, token_budget=token_budget)

    context = orchestrator.orchestrate(query)

    click.echo(f"\n🔍 Query: {query}\n")
    click.echo("📖 Context:")
    click.echo(context.to_prompt_format())
    click.echo(f"\n📊 Stats: {len(context.source_nodes)} nodes, {context.token_count} tokens")


@cli.command()
@click.argument('node-id')
@click.option('--depth', default=1, help='Depth of neighbors to retrieve')
@click.pass_context
def graph(ctx, node_id, depth):
    """Explore graph around a node"""
    storage = ctx.obj['storage']
    graph_engine = GraphEngine(storage)

    node = storage.get_node(node_id)
    if not node:
        click.echo(f"Node not found: {node_id}")
        return

    click.echo(f"\n🔗 Graph for: {node.title}\n")
    click.echo(f"Node Type: {node.node_type.value}")
    click.echo(f"Weight: {node.weight} | Decay: {node.decay_score}\n")

    neighbors_dict = graph_engine.get_neighbors(node_id, depth=depth)

    if not neighbors_dict:
        click.echo("No neighbors found")
        return

    click.echo(f"Neighbors (depth={depth}):\n")
    for neighbor_id, neighbor in neighbors_dict.items():
        click.echo(f"  - {neighbor.title[:50]}")
        click.echo(f"    Type: {neighbor.node_type.value}")
        click.echo()


@cli.command()
@click.argument('concept')
@click.pass_context
def explain(ctx, concept):
    """Explain a concept using knowledge base"""
    storage = ctx.obj['storage']
    orchestrator = ContextOrchestrator(storage)

    context = orchestrator.orchestrate(concept)

    click.echo(f"\n📚 Explaining: {concept}\n")
    click.echo(context.to_prompt_format())


@cli.command()
@click.pass_context
def stats(ctx):
    """Show knowledge base statistics"""
    storage = ctx.obj['storage']

    nodes = storage.get_all_nodes()
    edges = storage.get_edges()

    click.echo("\n📊 Knowledge Base Statistics\n")
    click.echo(f"Total Nodes: {len(nodes)}")

    # Count by type
    type_counts = {}
    for node in nodes:
        node_type = node.node_type.value
        type_counts[node_type] = type_counts.get(node_type, 0) + 1

    click.echo("\nNodes by Type:")
    for node_type, count in sorted(type_counts.items()):
        click.echo(f"  {node_type}: {count}")

    click.echo(f"\nTotal Edges: {len(edges)}")

    # Count by edge type
    if edges:
        edge_type_counts = {}
        for edge in edges:
            edge_type = edge.edge_type.value
            edge_type_counts[edge_type] = edge_type_counts.get(edge_type, 0) + 1

        click.echo("\nEdges by Type:")
        for edge_type, count in sorted(edge_type_counts.items()):
            click.echo(f"  {edge_type}: {count}")

    # Average node weight
    avg_weight = sum(n.weight for n in nodes) / len(nodes) if nodes else 0
    click.echo(f"\nAverage Node Weight: {avg_weight:.3f}")


@cli.command()
@click.pass_context
def clear(ctx):
    """Clear the knowledge base"""
    if click.confirm("Are you sure you want to clear the knowledge base?"):
        storage = ctx.obj['storage']
        for node in storage.get_all_nodes():
            storage.delete_node(node.id)
        click.echo("✓ Knowledge base cleared")


@cli.command()
@click.pass_context
def show(ctx):
    """Show graph visualization (terminal)"""
    storage = ctx.obj['storage']
    graph_engine = GraphEngine(storage)
    viz = TerminalGraphVisualizer(storage, graph_engine)
    
    click.echo(viz.visualize_graph_summary())


@cli.command()
@click.argument('node-id')
@click.option('--depth', default=2, help='Depth of neighbors')
@click.pass_context
def view(ctx, node_id, depth):
    """View a node and its neighborhood"""
    storage = ctx.obj['storage']
    graph_engine = GraphEngine(storage)
    viz = TerminalGraphVisualizer(storage, graph_engine)
    
    click.echo(viz.visualize_node(node_id, depth=depth))


@cli.command()
@click.argument('from-id')
@click.argument('to-id')
@click.pass_context
def path(ctx, from_id, to_id):
    """Find shortest path between two nodes"""
    storage = ctx.obj['storage']
    graph_engine = GraphEngine(storage)
    viz = TerminalGraphVisualizer(storage, graph_engine)
    
    click.echo(viz.visualize_path(from_id, to_id))


@cli.command()
@click.option('--port', default=5000, help='Port to run server on')
@click.pass_context
def serve(ctx, port):
    """Start web server for graph visualization"""
    try:
        from serverimport app
        click.echo(f"🌐 Starting BaseMem server on http://localhost:{port}")
        click.echo(f"📊 Open http://localhost:{port}/../../graph_visualization.html")
        click.echo("Press Ctrl+C to stop")
        app.run(host="0.0.0.0", port=port, debug=False)
    except ImportError:
        click.echo("Error: Flask not installed. Install with: pip install flask")


if __name__ == '__main__':
    cli()
