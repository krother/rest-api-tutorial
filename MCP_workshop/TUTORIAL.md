# MCP RAG Workshop: Complete Tutorial

A comprehensive, hands-on guide to building and running a RAG (Retrieval-Augmented Generation) server using the Model Context Protocol (MCP).

---

## Table of Contents

1. [What You'll Build](#1-what-youll-build)
2. [Understanding the Technologies](#2-understanding-the-technologies)
3. [Architecture Deep Dive](#3-architecture-deep-dive)
4. [Environment Setup](#4-environment-setup)
5. [Configuration](#5-configuration)
6. [Ingesting Documents](#6-ingesting-documents)
7. [Running the Server](#7-running-the-server)
8. [Testing Your Setup](#8-testing-your-setup)
9. [Connecting to AI Clients](#9-connecting-to-ai-clients)
10. [Code Walkthrough](#10-code-walkthrough)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. What You'll Build

This workshop creates an **MCP server** that allows AI assistants (Claude, ChatGPT, Cursor, VS Code) to search through your documents and get intelligent, cited answers.

### The Complete Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Your PDFs/    │───▶│   ingest.py     │───▶│   ChromaDB      │
│   Documents     │    │   (one-time)    │    │   (vector DB)   │
└─────────────────┘    └─────────────────┘    └────────┬────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌────────▼────────┐
│   AI Client     │◀──▶│   server.py     │◀──▶│   Claude API    │
│   (Cursor/etc)  │    │   (MCP server)  │    │   (summarize)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**What happens when you ask a question:**

1. Your question goes to the MCP server
2. Server converts your question to a vector (embedding)
3. ChromaDB finds the most similar document chunks
4. Claude reads those chunks and writes a summarized answer
5. Answer with citations returns to your AI client

---

## 2. Understanding the Technologies

### 2.1 MCP (Model Context Protocol)

**What is it?** A standard protocol that lets AI assistants use external tools. Think of it as a "USB port" for AI—any tool that speaks MCP can plug into any AI client that supports it.

**Why use it?** Instead of building custom integrations for each AI (Claude, ChatGPT, Cursor), you build one MCP server and it works everywhere.

**In this project:** We create an MCP server that exposes three tools:
- `search_cats` — Search documents and get summarized answers
- `fetch_file` — Retrieve full content of a specific file
- `deep_research` — Placeholder for future research capabilities

### 2.2 RAG (Retrieval-Augmented Generation)

**What is it?** A technique where an AI retrieves relevant information from a database before generating an answer. This grounds the AI's response in your actual data.

**Why use it?** LLMs have knowledge cutoffs and can't access your private documents. RAG lets them answer questions about your specific content.

**The RAG process:**
```
Question: "What do cats eat?"
    │
    ▼
[1. Embed] Convert question to vector: [0.23, -0.45, 0.12, ...]
    │
    ▼
[2. Retrieve] Find similar vectors in database → "Cats are carnivorous..."
    │
    ▼
[3. Generate] Claude reads context + question → "Cats primarily eat meat..."
```

### 2.3 ChromaDB

**What is it?** An open-source vector database that runs locally. It stores document chunks along with their vector embeddings.

**Where is it stored?** In a folder called `./chroma_db` within your project. This is a SQLite-based persistent database—your data survives restarts.

**Key concepts:**
| Term | Meaning |
|------|---------|
| Collection | A named group of documents (like a database table) |
| Document | A text chunk stored in the collection |
| Embedding | A vector representation of the text |
| Metadata | Extra info attached to each document (filename, chunk index) |

### 2.4 Sentence Transformers

**What is it?** A Python library that converts text into vectors (embeddings) using neural networks. Runs 100% locally—no API calls needed.

**Model used:** `all-MiniLM-L6-v2`
- Size: ~90MB (downloaded on first run)
- Output: 384-dimensional vectors
- Speed: Very fast on CPU

**Why local embeddings?** No API costs, no rate limits, works offline, and keeps your data private.

### 2.5 FastMCP

**What is it?** A Python framework for building MCP servers quickly. Uses decorators to turn functions into MCP tools.

**Example:**
```python
@mcp.tool
def search_cats(query: str) -> str:
    """This docstring becomes the tool description."""
    return "Results here"
```

### 2.6 Anthropic Claude (via Azure Foundry)

**What is it?** Claude is Anthropic's AI model. In this workshop, we access it through Azure AI Foundry, which provides a hosted endpoint.

**API differences from OpenAI:**
| Aspect | OpenAI | Anthropic |
|--------|--------|-----------|
| System prompt | In messages array | Separate `system` parameter |
| Response | `choices[0].message.content` | `content[0].text` |
| Max tokens | Optional | **Required** |

---

## 3. Architecture Deep Dive

### 3.1 Project Structure

```
MCP_workshop/
├── server.py           # Main MCP server (always running)
├── ingest.py           # Document ingestion (run once per document)
├── pyproject.toml      # Python dependencies
├── .env                # Your API credentials (create from .env.example)
├── .env.example        # Template for .env
├── .cursor/mcp.json    # Cursor IDE configuration
├── .vscode/mcp.json    # VS Code configuration
├── chroma_db/          # Vector database (created after first ingest)
│   ├── chroma.sqlite3  # Main database file
│   └── ...             # Index files
└── TUTORIAL.md         # This file
```

### 3.2 Data Flow Diagram

```
                    INGESTION (one-time)
                    ════════════════════

    ┌──────────┐    ┌─────────────────┐    ┌──────────────┐
    │ cats.pdf │───▶│ extract_text()  │───▶│ "Cats are    │
    └──────────┘    │ (pypdf)         │    │ small furry  │
                    └─────────────────┘    │ mammals..."  │
                                           └──────┬───────┘
                                                  │
                    ┌─────────────────┐           │
                    │ chunk_text()    │◀──────────┘
                    │ (500 chars,     │
                    │  50 overlap)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ SentenceTransf. │
                    │ .encode()       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ ChromaDB        │
                    │ collection.add()│
                    └─────────────────┘


                    QUERYING (every request)
                    ════════════════════════

    ┌──────────────┐    ┌─────────────────┐
    │ "What are    │───▶│ SentenceTransf. │
    │  cats?"      │    │ .encode()       │
    └──────────────┘    └────────┬────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ ChromaDB                │
                    │ collection.query()      │
                    │ → Returns top-k chunks  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ Claude API              │
                    │ "Summarize these chunks │
                    │  to answer the question"│
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ "Cats are domesticated  │
                    │  mammals known for..."  │
                    │                         │
                    │ Citations: cats.pdf     │
                    └─────────────────────────┘
```

### 3.3 Transport Modes

MCP supports multiple ways for clients to communicate with servers:

| Mode | How it works | Use case |
|------|--------------|----------|
| `stdio` | Standard input/output pipes | IDE integrations (Cursor, VS Code) |
| `sse` | Server-Sent Events over HTTP | Web clients, ChatGPT |
| `http` | REST API | Custom integrations |

**stdio (default):** The IDE starts the server as a subprocess and communicates via stdin/stdout. No network ports needed.

**SSE:** Server runs as a web service on port 9001. Clients connect via HTTP and receive streaming responses.

---

## 4. Environment Setup

### 4.1 Prerequisites

- **Python 3.11+** (check with `python3 --version`)
- **uv** (modern Python package manager) — [Install here](https://docs.astral.sh/uv/getting-started/installation/)
- **ngrok** (for external access) — [Install here](https://ngrok.com/download)

### 4.2 Step-by-Step Setup

```bash
# 1. Navigate to the workshop folder
cd MCP_workshop

# 2. Create a virtual environment
uv venv

# 3. Activate the virtual environment
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# 4. Install all dependencies
uv pip install -e .
```

**What gets installed:**

| Package | Purpose |
|---------|---------|
| `fastmcp` | MCP server framework |
| `anthropic` | Claude API client |
| `chromadb` | Vector database |
| `sentence-transformers` | Local embeddings |
| `python-dotenv` | Load .env files |
| `pypdf` | PDF text extraction |

### 4.3 First Run: Model Download

On first run, `sentence-transformers` downloads the embedding model:

```
Loading embedding model (all-MiniLM-L6-v2)...
Downloading: 100%|██████████| 90.9M/90.9M
```

This is cached at `~/.cache/huggingface/` and won't download again.

---

## 5. Configuration

### 5.1 Create Your .env File

```bash
cp .env.example .env
```

### 5.2 Environment Variables Explained

```bash
# ═══════════════════════════════════════════════════════════
# ANTHROPIC API CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Your API key (required)
ANTHROPIC_API_KEY=your_key_here

# Azure Foundry endpoint (for workshop)
ANTHROPIC_BASE_URL=https://mwb-fastapi-foundry-training.services.ai.azure.com/anthropic/

# Model deployment name
ANTHROPIC_MODEL=claude-opus-4-5

# ═══════════════════════════════════════════════════════════
# MCP SERVER CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Transport: stdio (IDE), sse (web), or http (REST)
MCP_TRANSPORT=stdio

# Host and port for sse/http modes
MCP_HOST=0.0.0.0
MCP_PORT=9001

# ═══════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Where ChromaDB stores data (default: ./chroma_db)
# CHROMA_DB_PATH=./chroma_db
```

### 5.3 Using Direct Anthropic API (Alternative)

If you have a direct Anthropic API key instead of Azure:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
# Leave ANTHROPIC_BASE_URL empty or remove it
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

---

## 6. Ingesting Documents

Before searching, you must add documents to the vector database.

### 6.1 Basic Usage

```bash
# Single file
python ingest.py document.pdf

# Multiple files
python ingest.py doc1.pdf doc2.txt notes.md
```

### 6.2 What Happens During Ingestion

```
$ python ingest.py cats.pdf

Initializing ChromaDB at: ./chroma_db
Loading embedding model (all-MiniLM-L6-v2)...
Processing: cats.pdf
  Extracted 12543 characters, created 28 chunks
  Generating embeddings...
  Added 28 chunks to vector store

==================================================
Ingestion complete!
  Total chunks added: 28
  Total documents in collection: 28
  Database location: ./chroma_db
```

### 6.3 How Chunking Works

Documents are split into overlapping chunks for better retrieval:

```
Original text (1500 chars):
"Cats are small furry domesticated carnivorous mammals. They are
often called house cats when kept as indoor pets. Cats have been
associated with humans for at least 9,500 years..."

Chunk 1 (chars 0-500):
"Cats are small furry domesticated carnivorous mammals. They are
often called house cats when kept as indoor pets..."

Chunk 2 (chars 450-950):  ← 50 char overlap
"...indoor pets. Cats have been associated with humans for at
least 9,500 years. They are known for their ability..."

Chunk 3 (chars 900-1400):
"...ability to hunt vermin and for their companionship..."
```

**Why overlap?** Ensures context isn't lost at chunk boundaries. A question about "indoor pets and history" can find the relevant chunk even if the answer spans a boundary.

### 6.4 Supported File Formats

| Format | Extension | Handler |
|--------|-----------|---------|
| PDF | `.pdf` | pypdf library |
| Plain text | `.txt` | Direct read |
| Markdown | `.md` | Direct read |
| CSV | `.csv` | Direct read |
| JSON | `.json` | Direct read |
| HTML | `.html` | Direct read |

### 6.5 Re-ingesting Files

If you update a document and re-ingest it, the old chunks are automatically removed:

```
Processing: cats.pdf
  Removing 28 existing chunks for this file
  Extracted 15000 characters, created 32 chunks
  Added 32 chunks to vector store
```

---

## 7. Running the Server

### 7.1 For IDE Use (Cursor/VS Code)

The IDE handles server startup automatically. Just configure the MCP settings:

**For Cursor:** The file `.cursor/mcp.json` is already configured:
```json
{
  "mcpServers": {
    "cats-rag": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "${workspaceFolder}/MCP_workshop",
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

**For VS Code:** Same configuration in `.vscode/mcp.json`.

After configuring, restart your IDE. The server starts automatically when you use MCP features.

### 7.2 For External Clients (SSE Mode)

```bash
# Start the server
MCP_TRANSPORT=sse python server.py
```

You'll see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9001
```

### 7.3 Exposing via ngrok

To make your local server accessible from the internet:

```bash
# In another terminal
ngrok http 9001
```

Output:
```
Session Status                online
Forwarding                    https://abc123.ngrok.io -> http://localhost:9001
```

Use the ngrok URL with `/sse` appended: `https://abc123.ngrok.io/sse`

---

## 8. Testing Your Setup

### 8.1 Test the API Endpoint (SSE Mode)

```bash
curl -v http://127.0.0.1:9001/sse
```

Expected: Connection stays open (SSE stream). Press Ctrl+C to exit.

### 8.2 Test ChromaDB Directly

```python
import chromadb
from sentence_transformers import SentenceTransformer

# Connect to database
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("cats_rag")

# Check document count
print(f"Documents in database: {collection.count()}")

# Test a search
model = SentenceTransformer("all-MiniLM-L6-v2")
query_vec = model.encode(["What are cats?"]).tolist()
results = collection.query(query_embeddings=query_vec, n_results=3)
print(results["documents"])
```

### 8.3 Test the Full Pipeline

```python
import os
os.environ['ANTHROPIC_API_KEY'] = 'your_key'
os.environ['ANTHROPIC_BASE_URL'] = 'https://...'
os.environ['ANTHROPIC_MODEL'] = 'claude-opus-4-5'

# Import after setting env vars
from server import search_cats

# Note: search_cats is wrapped by FastMCP, so for direct testing,
# run the internal logic separately (see test script in README)
```

### 8.4 Test via Cursor

1. Open Cursor in the project folder
2. Ensure MCP is configured (check `.cursor/mcp.json`)
3. Open chat and ask: "Use search_cats to find information about cats"
4. Cursor should invoke the tool and return results

---

## 9. Connecting to AI Clients

### 9.1 Cursor IDE

1. Ensure `.cursor/mcp.json` exists with the configuration
2. Restart Cursor
3. The "cats-rag" server appears in MCP tools
4. Use in chat: "Search for [topic] in the documents"

### 9.2 VS Code

1. Ensure `.vscode/mcp.json` exists
2. Install the MCP extension if required
3. Restart VS Code
4. Use MCP tools in the chat interface

### 9.3 ChatGPT (via Actions)

1. Start server in SSE mode: `MCP_TRANSPORT=sse python server.py`
2. Expose via ngrok: `ngrok http 9001`
3. In ChatGPT, create a Custom GPT with an Action
4. Set the server URL to: `https://your-ngrok-url.ngrok.io/sse`
5. ChatGPT can now use your MCP tools

### 9.4 Claude Desktop

1. Add server to Claude's MCP configuration
2. Use stdio transport for local connection
3. Restart Claude Desktop

---

## 10. Code Walkthrough

### 10.1 server.py — Main Server

**Initialization (lines 1-35):**
```python
from fastmcp import FastMCP
from anthropic import Anthropic
import chromadb
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Initialize ChromaDB (persistent storage)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="cats_rag")

# Initialize embedding model (runs locally)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Create MCP server
mcp = FastMCP("Cats RAG")
```

**The search_cats Tool (lines 48-138):**
```python
@mcp.tool
def search_cats(query: str, k: int = 5) -> str:
    """Semantic search over documents, then summarize with Claude."""

    # Step 1: Convert query to vector
    query_embedding = embedding_model.encode([query]).tolist()

    # Step 2: Find similar chunks in ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

    # Step 3: Build context from retrieved chunks
    context_block = format_results(results)

    # Step 4: Ask Claude to summarize
    response = client.messages.create(
        model="claude-opus-4-5",
        system="You are a helpful RAG assistant...",
        messages=[{"role": "user", "content": f"Question: {query}\n\nContext:\n{context_block}"}],
        max_tokens=1024
    )

    return response.content[0].text
```

**Transport Selection (lines 198-211):**
```python
if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=9001)
    elif transport == "http":
        mcp.run(transport="http", host="0.0.0.0", port=8000)
    else:
        mcp.run(transport="stdio")  # Default for IDEs
```

### 10.2 ingest.py — Document Ingestion

**Chunking Strategy (lines 75-108):**
```python
def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at sentence boundary
        for sep in [". ", ".\n", "\n\n"]:
            boundary = text.rfind(sep, start, end)
            if boundary > start:
                end = boundary + len(sep)
                break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap  # Overlap with previous chunk

    return chunks
```

**Embedding and Storage (lines 142-164):**
```python
# Generate embeddings for all chunks
embeddings = embedding_model.encode(chunks).tolist()

# Store in ChromaDB with metadata
collection.add(
    ids=["file_chunk_0", "file_chunk_1", ...],
    embeddings=embeddings,
    documents=chunks,
    metadatas=[
        {"file_id": "cats_abc123", "filename": "cats.pdf", "chunk_idx": 0},
        {"file_id": "cats_abc123", "filename": "cats.pdf", "chunk_idx": 1},
        ...
    ]
)
```

---

## 11. Troubleshooting

### Problem: "No documents in the vector store"

**Cause:** You haven't ingested any documents yet.

**Solution:**
```bash
python ingest.py your_document.pdf
```

### Problem: "Anthropic API key not configured"

**Cause:** The `.env` file is missing or `ANTHROPIC_API_KEY` is not set.

**Solution:**
```bash
cp .env.example .env
# Edit .env and add your API key
```

### Problem: "DeploymentNotFound" error

**Cause:** The model name doesn't match the Azure deployment.

**Solution:** Verify `ANTHROPIC_MODEL` matches exactly what's deployed:
```bash
ANTHROPIC_MODEL=claude-opus-4-5  # Must match deployment name
```

### Problem: Embedding model download is slow

**Cause:** First-time download of the 90MB model.

**Solution:** Wait for download to complete. It's cached for future runs.

### Problem: ChromaDB errors on startup

**Cause:** Corrupted database or version mismatch.

**Solution:**
```bash
rm -rf chroma_db/
python ingest.py your_document.pdf  # Re-ingest
```

### Problem: Port 9001 already in use

**Cause:** Another process is using the port.

**Solution:**
```bash
# Find and kill the process
lsof -i :9001
kill -9 <PID>

# Or use a different port
MCP_PORT=9002 MCP_TRANSPORT=sse python server.py
```

### Problem: ngrok connection refused

**Cause:** Server isn't running or wrong port.

**Solution:**
1. Ensure server is running: `MCP_TRANSPORT=sse python server.py`
2. Test locally first: `curl http://127.0.0.1:9001/sse`
3. Then run ngrok: `ngrok http 9001`

---

## Next Steps

After completing this workshop, you can:

1. **Add more documents** — Ingest your own PDFs, documentation, or knowledge base
2. **Customize the prompt** — Modify the system prompt in `search_cats()` for your use case
3. **Add new tools** — Create additional MCP tools for other functionality
4. **Deploy to production** — Run on a cloud server with proper authentication
5. **Upgrade embeddings** — Switch to Voyage AI or OpenAI embeddings for better quality

---

## Quick Reference Card

```bash
# Setup
cd MCP_workshop
uv venv && source .venv/bin/activate
uv pip install -e .
cp .env.example .env  # Edit with your API key

# Ingest documents
python ingest.py document.pdf

# Run server (IDE)
python server.py

# Run server (external)
MCP_TRANSPORT=sse python server.py

# Expose publicly
ngrok http 9001
```

**MCP Tools Available:**
| Tool | Description |
|------|-------------|
| `search_cats(query, k=5)` | Search documents, get summarized answer |
| `fetch_file(file_id)` | Get full content of a specific file |
| `deep_research(topic)` | Placeholder for research API |

---

*Workshop created for hands-on learning of MCP, RAG, and vector databases.*
