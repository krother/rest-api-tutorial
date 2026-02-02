# MCP RAG Workshop

A workshop-friendly MCP (Model Context Protocol) server that provides RAG (Retrieval-Augmented Generation) tools using:

- **Anthropic Claude** for summarization (via Azure Foundry or direct API)
- **ChromaDB** for local vector storage
- **Sentence Transformers** for embeddings (runs locally, no extra API keys)

## Quick Start

### 1. Setup Environment

```bash
cd MCP_workshop

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your API credentials:

```bash
# For Azure Foundry endpoint (workshop default):
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_BASE_URL=https://mwb-fastapi-foundry-training.services.ai.azure.com/anthropic/
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

### 3. Ingest Documents

Add documents to your vector store:

```bash
# Single file
uv run python ingest.py your_document.pdf

# Multiple files
uv run python ingest.py doc1.pdf doc2.txt notes.md
```

Supported formats: PDF, TXT, MD, and other text files.

### 4. Run the Server

**For Cursor/VS Code (stdio mode - default):**

The IDE will start the server automatically using the configuration in `.cursor/mcp.json` or `.vscode/mcp.json`.

**For external clients like ChatGPT (SSE mode):**

```bash
MCP_TRANSPORT=sse uv run python server.py
```

Then expose via ngrok:

```bash
ngrok http 9001
```

Use the ngrok HTTPS URL with `/sse` appended in ChatGPT connectors (e.g., `https://abc123.ngrok.io/sse`).

## Available MCP Tools

### `search_cats(query, k=5)`

Semantic search over your documents with Claude summarization.

- `query`: Your search question
- `k`: Number of results to retrieve (default: 5)

Returns a summarized answer with citations.

### `fetch_file(file_id, max_chars=50000)`

Retrieve full content for a specific file.

- `file_id`: The file ID (shown in search results)
- `max_chars`: Maximum characters to return

### `deep_research(topic)` (disabled by default)

Placeholder for deep research integration. Enable with `DEEP_RESEARCH_ENABLED=true`.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP_workshop/                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐     ┌──────────────┐                     │
│   │  ingest.py   │────▶│  ChromaDB    │◀────┐               │
│   │  (one-time)  │     │  (./chroma_db)│     │               │
│   └──────────────┘     └──────────────┘     │               │
│         │                     │              │               │
│         ▼                     ▼              │               │
│   ┌──────────────┐     ┌──────────────┐     │               │
│   │ sentence-    │     │  server.py   │─────┘               │
│   │ transformers │────▶│  (FastMCP)   │                     │
│   │ embeddings   │     └──────┬───────┘                     │
│   └──────────────┘            │                              │
│                               ▼                              │
│                        ┌──────────────┐                     │
│                        │ Claude API   │                     │
│                        │ (Azure)      │                     │
│                        └──────────────┘                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | API key for Claude | (required) |
| `ANTHROPIC_BASE_URL` | Base URL for API (Azure Foundry or direct) | (Anthropic default) |
| `ANTHROPIC_MODEL` | Claude model to use | `claude-sonnet-4-20250514` |
| `MCP_TRANSPORT` | Transport mode: `stdio`, `sse`, or `http` | `stdio` |
| `MCP_HOST` | Host for SSE/HTTP modes | `0.0.0.0` |
| `MCP_PORT` | Port for SSE/HTTP modes | `9001` |
| `CHROMA_DB_PATH` | Path to ChromaDB storage | `./chroma_db` |
| `DEEP_RESEARCH_ENABLED` | Enable deep_research tool | `false` |

## Transport Modes

| Mode | Use Case | Command |
|------|----------|---------|
| `stdio` | Cursor, VS Code | `python server.py` (default) |
| `sse` | ChatGPT, external clients | `MCP_TRANSPORT=sse python server.py` |
| `http` | REST API integration | `MCP_TRANSPORT=http python server.py` |

## Troubleshooting

### "No documents in the vector store"

Run the ingestion script first:

```bash
uv run python ingest.py your_document.pdf
```

### "Anthropic API key not configured"

Check your `.env` file has the correct `ANTHROPIC_API_KEY`.

### Connection issues with SSE

1. Verify the server is running: `curl -v http://127.0.0.1:9001/sse`
2. Check ngrok is forwarding correctly
3. Ensure your firewall allows connections on port 9001

### Embedding model download slow

The first run downloads the `all-MiniLM-L6-v2` model (~90MB). This is cached locally for subsequent runs.

## Development

### Project Structure

```
MCP_workshop/
├── server.py          # Main MCP server
├── ingest.py          # Document ingestion script
├── pyproject.toml     # Dependencies (uv/pip)
├── .env.example       # Environment template
├── .cursor/mcp.json   # Cursor IDE config
├── .vscode/mcp.json   # VS Code config
├── chroma_db/         # Vector store (created on ingest)
└── README.md          # This file
```

### Testing the Server

```bash
# Test SSE endpoint
curl -v http://127.0.0.1:9001/sse

# Test via Cursor
# 1. Copy .cursor/mcp.json config
# 2. Restart Cursor
# 3. Use search_cats("what is a cat?") in chat
```
