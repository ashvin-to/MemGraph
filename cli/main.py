"""Main CLI interface using Click"""

import click
import asyncio
import json
from pathlib import Path
import logging
import os

from storage.db import StorageManager
from retrieval.engine import RetrievalEngine
from graph.engine import GraphEngine
from orchestrator.context import ContextOrchestrator
from processing.pipeline import ProcessingPipeline
from visualization.terminal import TerminalGraphVisualizer
from modelsimport NodeType, EdgeType

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Helper to find the sessions folder
def get_session_dir():
    # Base BaseMem install directory
    base_dir = Path(__file__).parent.parent.parent.parent.absolute()
    session_dir = base_dir / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


@click.group()
@click.option('--db', help='Database file path')
@click.pass_context
def cli(ctx, db):
    """BaseMem: AI Knowledge Base System"""
    ctx.ensure_object(dict)
    ctx.obj['db'] = db
    ctx.obj['storage'] = StorageManager(db)


@cli.command()
@click.argument('text', required=False)
@click.option('--file', '-f', help='Path to a file to ingest')
@click.option('--source', default='cli', help='Source of the text')
@click.pass_context
def add(ctx, text, file, source):
    """Add text or file to knowledge base"""
    if not text and not file:
        click.echo("Error: Either TEXT argument or --file option must be provided.")
        return

    storage = ctx.obj['storage']
    graph_engine = GraphEngine(storage)
    pipeline = ProcessingPipeline(storage)

    if file:
        file_path = Path(file)
        if not file_path.exists():
            click.echo(f"Error: File {file} not found.")
            return
        with open(file_path, 'r') as f:
            content = f.read()
        source = source if source != 'cli' else file_path.name
    else:
        content = text

    async def process():
        nodes = await pipeline.ingest_text(content, source=source)
        
        # Auto-link new nodes
        total_edges = 0
        for node in nodes:
            edges = graph_engine.auto_link_nodes(node.id, threshold=0.2)
            total_edges += len(edges)
        
        click.echo(f"✓ Added {len(nodes)} nodes from {source}")
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

    context_packet = orchestrator.orchestrate(query)

    click.echo(f"\n🔍 Query: {query}\n")
    click.echo("📖 Context:")
    click.echo(context_packet.to_prompt_format())
    click.echo(f"\n📊 Stats: {len(context_packet.source_nodes)} nodes, {context_packet.token_count} tokens")


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

    context_packet = orchestrator.orchestrate(concept)

    click.echo(f"\n📚 Explaining: {concept}\n")
    click.echo(context_packet.to_prompt_format())


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
        click.echo(f"📊 Open http://localhost:{port} in your browser")
        click.echo("Press Ctrl+C to stop")
        app.run(host="0.0.0.0", port=port, debug=False)
    except ImportError:
        click.echo("Error: Flask not installed. Install with: pip install flask")


@cli.command()
@click.argument('topic')
@click.pass_context
def review(ctx, topic):
    """Review the current session summary and recent history"""
    from storage.sessions import SessionManager
    storage = ctx.obj['storage']
    manager = SessionManager(storage)
    
    session_node = manager.get_or_create_session(topic)
    history = manager.get_session_history(topic)
    
    click.echo(f"\n📋 Session Review: {topic}\n")
    click.echo("--- CURRENT SUMMARY ---")
    click.echo(session_node.content)
    
    click.echo("\n--- RECENT HISTORY ---")
    
    # Check if we have a "Main History" node
    main_history = next((n for n in history if n.metadata.get("is_main_history") or n.metadata.get("is_private_history")), None)
    
    if main_history:
        # Parse the entries
        entries = main_history.content.split("--- [")
        actual_entries = entries[1:] 
        
        for entry in actual_entries[-5:]: # Show last 5
            click.echo(f"--- [{entry.strip()}")
            click.echo("")
    else:
        # Fallback
        for chat in history[-5:]:
            agent_id = chat.metadata.get("agent_id", "unknown").upper()
            click.echo(f"[{agent_id}] {chat.content[:100]}...")


@cli.group()
def mcp():
    """Model Context Protocol (MCP) server commands"""
    pass


@mcp.command()
@click.option('--db', help='Database file path (overrides global db)')
@click.pass_context
def start(ctx, db):
    """Start the BaseMem MCP server"""
    db_path = db or ctx.obj['db']
    os.environ["BASEMEM_DB_PATH"] = str(Path(db_path).absolute())
    
    from ..mcp.server import mcp as mcp_server
    click.echo(f"🚀 Starting BaseMem MCP server (DB: {db_path})")
    mcp_server.run()


@cli.group()
def session():
    """Manage conversation sessions and summaries"""
    pass


@session.command()
@click.argument('topic', required=False)
@click.pass_context
def context(ctx, topic):
    """Retrieve the summary and participant registry for the current project (Centralized)"""
    if not topic or topic == ".":
        topic = Path.cwd().name
        
    from storage.sessions import SessionManager
    storage = ctx.obj['storage']
    manager = SessionManager(storage)
    
    session_node = manager.get_or_create_session(topic)
    peers = session_node.metadata.get("participating_agents", [])
    
    click.echo(f"\n🧠 Project Memory: {topic}\n")
    click.echo("--- CURRENT SUMMARY ---")
    click.echo(session_node.content)
    click.echo("\n--- PARTICIPATING AGENTS ---")
    if peers:
        for peer in peers:
            click.echo(f"- {peer} (Read with: `kb session read \"{topic}\" --agent-id \"{peer}\" --last 5`)")
    else:
        click.echo("No previous agents recorded for this topic.")
    click.echo(f"\n*Last System Sync: {session_node.last_accessed.isoformat()}*")


@session.command()
@click.argument('topic', required=False)
@click.argument('message')
@click.option('--summary', help='Direct summary text from AI')
@click.option('--keywords', help='Comma-separated keywords from AI')
@click.option('--agent-id', default='default', help='Unique ID for this AI session/agent')
@click.option('--sender', default='ai', help='Sender of the message')
@click.pass_context
def turn(ctx, topic, message, summary, keywords, agent_id, sender):
    """Log message and save AI-provided metadata (Centralized Mode)"""
    if not topic or topic == ".":
        topic = Path.cwd().name
        
    from storage.sessions import SessionManager
    storage = ctx.obj['storage']
    manager = SessionManager(storage)
    
    # 1. Log chat
    manager.log_chat(topic, message, sender=sender, agent_id=agent_id)
    
    # 2. Update the shared topic summary
    if summary:
        session_node = manager.update_summary(topic, summary)
        
        # 3. Centralized Export
        session_dir = get_session_dir()
        output_file = session_dir / f".basemem-{topic}-summary.md"
        peers = session_node.metadata.get("participating_agents", [])
        
        with open(output_file, "w") as f:
            f.write(f"# Session Summary: {topic}\n\n")
            f.write(summary)
            f.write("\n\n---\n")
            if peers:
                f.write(f"### 👥 Participating Agents (Histories available):\n")
                for peer in peers:
                    f.write(f"- `{peer}` (Read with: `kb session read \"{topic}\" --agent-id \"{peer}\"`)\n")
            f.write(f"\n*Last Updated: {session_node.last_accessed.isoformat()}*")
            
        click.echo(f"✓ Project Brain for '{topic}' updated and exported to {output_file.name}")
    
    click.echo(f"✓ Turn logged (Agent: {agent_id})")


@session.command()
@click.argument('topic', required=False)
@click.option('--agent-id', required=True, help='Your unique session/agent suffix')
@click.pass_context
def sync(ctx, topic, agent_id):
    """Automatically find and sync your FULL local chat history to the graph (Centralized)"""
    if not topic or topic == ".":
        topic = Path.cwd().name
        
    import json
    import glob
    
    pattern = f"/home/zoro/.gemini/tmp/*/chats/session-*-{agent_id}.json"
    files = glob.glob(pattern)
    
    if not files:
        click.echo(f"Error: Could not find a local chat file ending in '{agent_id}'")
        return
        
    chat_file = files[0]
    click.echo(f"⏳ Syncing from: {chat_file}")
    
    try:
        with open(chat_file, "r") as f:
            data = json.load(f)
            
        transcript = f"Full conversation history for topic: {topic}\n"
        messages = data.get("messages", [])
        if not messages and isinstance(data, list): messages = data

        for msg in messages:
            sender = msg.get("type", "unknown").upper()
            if sender == "INFO": continue
            content = msg.get("content", "")
            if isinstance(content, list):
                content = "\n".join([p["text"] for p in content if "text" in p])
            timestamp = msg.get("timestamp", "unknown")
            transcript += f"\n\n--- [{timestamp}] {sender} ---\n{content}"

        # Save
        from storage.sessions import SessionManager
        storage_instance = ctx.obj['storage']
        manager = SessionManager(storage_instance)
        manager.ingest_transcript(topic, transcript)
        
        # Meta Fix
        history_id = f"history-{agent_id}-{topic.lower().replace(' ', '-')}"
        old_id = f"full-transcript-{topic.lower().replace(' ', '-')}"
        
        node = storage_instance.get_node(old_id)
        if node:
            node.id = history_id
            node.title = f"History ({agent_id}): {topic}"
            node.metadata["agent_id"] = agent_id
            node.metadata["is_private_history"] = True
            storage_instance.add_node(node)
            storage_instance.delete_node(old_id)

        # Refresh the shared summary registry
        session_node = manager.update_summary(topic, manager.get_or_create_session(topic).content)
        
        # Centralized Export
        session_dir = get_session_dir()
        output_file = session_dir / f".basemem-{topic}-summary.md"
        peers = session_node.metadata.get("participating_agents", [])
        with open(output_file, "w") as f:
            f.write(f"# Session Summary: {topic}\n\n")
            f.write(session_node.content)
            f.write("\n\n---\n")
            if peers:
                f.write(f"### 👥 Participating Agents:\n")
                for peer in peers:
                    f.write(f"- `{peer}`\n")
            f.write(f"\n*Last Updated: {session_node.last_accessed.isoformat()}*")

        click.echo(f"✓ FULL high-fidelity history synced and summary exported.")
    except Exception as e:
        click.echo(f"Error during sync: {e}")


@session.command()
@click.argument('topic', required=False)
@click.option('--agent-id', default='default', help='AI agent history to read')
@click.option('--last', type=int, help='Number of recent entries to read')
@click.pass_context
def read(ctx, topic, agent_id, last):
    """Read history for a specific topic and agent"""
    if not topic or topic == ".":
        topic = Path.cwd().name
        
    storage = ctx.obj['storage']
    node_id = f"history-{agent_id}-{topic.lower().replace(' ', '-')}"
    node = storage.get_node(node_id)
    
    if node:
        click.echo(f"\n📖 History for '{topic}' (Agent: {agent_id}):\n")
        if last:
            entries = node.content.split("--- [")
            header = entries[0]
            actual_entries = entries[1:]
            click.echo(header.strip())
            for entry in actual_entries[-last:]:
                click.echo(f"--- [{entry.strip()}")
                click.echo("")
        else:
            click.echo(node.content)
    else:
        click.echo(f"No private history found for agent '{agent_id}'.")


@session.command()
@click.argument('topic', required=False)
@click.option('--path', default='.', help='Folder to bootstrap')
@click.pass_context
def bootstrap(ctx, topic, path):
    """Bootstrap a new project with AGENTS.md"""
    if not topic or topic == ".":
        topic = Path.cwd().name
        
    storage = ctx.obj['storage']
    from storage.sessions import SessionManager
    manager = SessionManager(storage)
    manager.get_or_create_session(topic)
    
    target_dir = Path(path).absolute()
    agents_file = target_dir / "AGENTS.md"
    
    content = f"""# 🧠 AI Agent Memory Protocol: {topic}

## 📥 START OF SESSION
Run: `kb session context` to see shared status.

## 📤 DURING SESSION
Log every turn: `kb session turn --agent-id "<your-id>" "<Short log>" --summary "<Full summary>" --sender ai`

## 💾 END OF SESSION
Sync full history: `kb session sync --agent-id "<your-id>"`
"""
    with open(agents_file, "w") as f:
        f.write(content)
        
    click.echo(f"🚀 Folder '{topic}' bootstrapped!")


if __name__ == '__main__':
    cli()
