# BaseMem: AI Knowledge Base System

A lightweight knowledge graph plugin/middleware with token-optimized memory, hybrid retrieval (BM25 + Vector), and intelligent context packaging. **Designed as a plugin for existing chat interfaces** (Claude Code, Copilot, Gemini CLI, etc.) — not a standalone chat system.

## Quick Start

### Installation

```bash
pip install -e .
```

### Basic Usage

```bash
# Add knowledge to the base
kb add "Machine learning is a subset of artificial intelligence"

# Search for information
kb search "what is machine learning"

# Ask a question (full RAG pipeline)
kb ask "explain machine learning"

# Explore the knowledge graph
kb graph <node-id>

# View statistics
kb stats
```

## Architecture

### Core Components

1. **Storage Layer** (`storage/`)
   - SQLite + FTS5 for full-text search
   - Persistent node and edge storage
   - Usage statistics tracking

2. **Retrieval Engine** (`retrieval/`)
   - BM25 for keyword matching
   - Vector search for semantic similarity
   - Hybrid merging and ranking

3. **Graph Engine** (`graph/`)
   - Node and edge management
   - Graph traversal (neighbors, paths, subgraphs)
   - Community detection

4. **Context Orchestrator** (`orchestrator/`)
   - Token budgeting
   - Deduplication and ranking
   - Diversity control
   - Structured context formatting

5. **Processing Pipeline** (`processing/`)
   - Async text ingestion
   - Semantic chunking
   - Automatic linking
   - Keyword extraction

6. **CLI Interface** (`cli/`)
   - User-friendly command line interface
   - Commands: add, search, ask, graph, explain, stats

## Data Models

### Node
```python
@dataclass
class Node:
    id: str
    title: str
    content: str
    node_type: NodeType  # concept, fact, summary, conversation, task, question, example
    keywords: List[str]
    embedding: Optional[List[float]]
    weight: float
    created_at: datetime
    last_accessed: datetime
    decay_score: float
    metadata: Dict[str, Any]
```

### Edge
```python
@dataclass
class Edge:
    from_id: str
    to_id: str
    edge_type: EdgeType  # is_a, part_of, related_to, causes, depends_on, contradicts, derived_from
    weight: float
    confidence: float
    created_at: datetime
    metadata: Dict[str, Any]
```

## Retrieval Pipeline

```
Query
  ↓
BM25 search (keyword matching) → top 50 results
  ↓
Vector search (semantic similarity) → top 50 results
  ↓
Merge and deduplicate
  ↓
Rank by: similarity × weight × decay_score
  ↓
Token-aware context packing
  ↓
Structured output formatting
```

## Project Structure

```
BaseMem/
├── src/basemem/
│   ├── models.py              # Core data classes
│   ├── storage/
│   │   └── db.py              # SQLite storage manager
│   ├── retrieval/
│   │   ├── engine.py          # Hybrid retrieval
│   │   ├── bm25.py            # BM25 implementation
│   │   └── vector.py          # Vector search
│   ├── graph/
│   │   └── engine.py          # Graph operations
│   ├── orchestrator/
│   │   └── context.py         # Context orchestration
│   ├── processing/
│   │   ├── pipeline.py        # Main pipeline
│   │   └── workers.py         # Async workers
│   └── cli/
│       └── main.py            # CLI commands
├── tests/
│   └── test_basemem.py       # Unit tests
├── kb.py                       # Entry point
├── requirements.txt            # Dependencies
└── pyproject.toml             # Project metadata
```

## System Evolution

### Phase 1 (Current)
- ✅ SQLite + FTS5 storage
- ✅ BM25 keyword search
- ✅ Sentence transformer embeddings
- ✅ Basic vector search
- ✅ Graph traversal
- ✅ CLI interface
- ✅ Async processing pipeline

### Phase 2 (Planned)
- FAISS or Qdrant vector DB
- Cross-encoder reranking
- Hierarchical memory (Level 1-3)
- Decay-based forgetting system

### Phase 3 (Planned)
- Neo4j integration for larger graphs
- Multi-device synchronization
- Advanced visualization
- API server

## Configuration

Set environment variables:

```bash
export BASEMEM_DB_PATH="./data/basemem.db"
export BASEMEM_TOKEN_BUDGET="2000"
export BASEMEM_VECTOR_MODEL="all-MiniLM-L6-v2"
```

## Plugin Integration

Use BaseMem as middleware in your chat interface:

```python
# Example integration with any chat interface
from basemem.orchestrator.context import ContextOrchestrator
from basemem.storage.db import StorageManager

storage = StorageManager("knowledge.db")
orchestrator = ContextOrchestrator(storage, token_budget=2000)

# In your chat handler:
def handle_user_query(user_input, chat_history):
    # Get context from knowledge base
    context = orchestrator.orchestrate(user_input)
    
    # Augment prompt with context
    augmented_prompt = f"{context.to_prompt_format()}\n\nUser: {user_input}"
    
    # Send to your LLM (Claude, Copilot, etc.)
    response = your_llm.chat(augmented_prompt)
    
    return response
```

Works with:
- ✅ Claude (Claude.ai, Claude Code)
- ✅ GitHub Copilot & Copilot Chat
- ✅ Google Gemini CLI
- ✅ ChatGPT & OpenAI API
- ✅ Any LLM via custom integration

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
black src/
ruff check src/
mypy src/
```

## License

MIT

## Contributing

Contributions welcome! See CONTRIBUTING.md for guidelines.
