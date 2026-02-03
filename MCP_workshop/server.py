import os
import json
from typing import Optional

from dotenv import load_dotenv
from fastmcp import FastMCP
from anthropic import Anthropic
import chromadb
from sentence_transformers import SentenceTransformer


load_dotenv()


def get_env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# Initialize ChromaDB (persistent local storage)
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(name="cats_rag")

# Initialize embedding model (runs locally, no API key needed)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Anthropic client configuration
ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL: Optional[str] = os.getenv("ANTHROPIC_BASE_URL")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-5")

mcp = FastMCP("Cats RAG")


def get_anthropic_client() -> Anthropic:
    """Create Anthropic client with optional Azure Foundry base URL."""
    kwargs = {}
    if ANTHROPIC_API_KEY:
        kwargs["api_key"] = ANTHROPIC_API_KEY
    if ANTHROPIC_BASE_URL:
        kwargs["base_url"] = ANTHROPIC_BASE_URL
    return Anthropic(**kwargs)


@mcp.tool
def search_cats(query: str, k: int = 5) -> str:
    """Semantic search over the local ChromaDB vector store.

    Returns raw search results with relevance scores. No API key needed.
    Use this when the calling AI assistant can summarize the results.

    Args:
        query: The search query
        k: Number of results to return (default 5)
    """
    # Check if collection has any documents
    if collection.count() == 0:
        return (
            "No documents in the vector store. Run ingest.py first to add documents:\n"
            "  python ingest.py your_document.pdf"
        )

    # Embed the query and search ChromaDB
    try:
        query_embedding = embedding_model.encode([query]).tolist()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        return f"Vector store search failed: {exc}"

    # Extract snippets from results
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        return "No results found in the vector store for the given query."

    # Format results
    output_lines = [f"Search results for: {query}\n"]
    for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
        filename = meta.get("filename", "unknown")
        chunk_idx = meta.get("chunk_idx", 0)
        score = 1 / (1 + dist)  # Convert distance to similarity
        preview = (doc or "").strip()
        if len(preview) > 500:
            preview = preview[:500] + " ..."
        output_lines.append(
            f"[Result {idx + 1}] file={filename} (chunk {chunk_idx}) score={score:.4f}\n{preview}\n"
        )

    return "\n".join(output_lines)


@mcp.tool
def search_cats_summarized(query: str, k: int = 5) -> str:
    """Semantic search with Claude summarization (requires ANTHROPIC_API_KEY).

    Searches the vector store and uses Claude to summarize results with citations.
    Use this for autonomous RAG where you want a ready-to-use answer.

    Args:
        query: The search query
        k: Number of results to retrieve before summarization (default 5)
    """
    if not ANTHROPIC_API_KEY:
        return (
            "Anthropic API key not configured. Set ANTHROPIC_API_KEY in your .env file.\n"
            "Alternatively, use search_cats() which returns raw results without summarization."
        )

    # Check if collection has any documents
    if collection.count() == 0:
        return (
            "No documents in the vector store. Run ingest.py first to add documents:\n"
            "  python ingest.py your_document.pdf"
        )

    # Step 1: Embed the query and search ChromaDB
    try:
        query_embedding = embedding_model.encode([query]).tolist()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        return f"Vector store search failed: {exc}"

    # Extract snippets from results
    snippets = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
        file_id = meta.get("file_id", "unknown")
        filename = meta.get("filename", "unknown")
        chunk_idx = meta.get("chunk_idx", 0)
        # Convert distance to similarity score (ChromaDB uses L2 by default)
        score = 1 / (1 + dist)
        snippets.append({
            "index": idx,
            "file_id": file_id,
            "filename": filename,
            "chunk_idx": chunk_idx,
            "score": round(score, 4),
            "text": doc,
        })

    if not snippets:
        return "No results found in the vector store for the given query."

    # Compose a concise context block
    context_lines = []
    for s in snippets:
        preview = (s["text"] or "").strip()
        if len(preview) > 500:
            preview = preview[:500] + " ..."
        context_lines.append(
            f"[hit {s['index']}] file={s['filename']} (chunk {s['chunk_idx']}) score={s['score']}\n{preview}"
        )
    context_block = "\n\n".join(context_lines)

    # Step 2: Summarize with Claude
    client = get_anthropic_client()

    system_prompt = (
        "You are a helpful RAG assistant. ONLY use the provided context to answer. "
        "Be concise and include a short 'Citations' section listing filenames used."
    )

    user_message = (
        f"Question: {query}\n\nContext:\n{context_block}\n\n"
        "Answer succinctly using the context."
    )

    try:
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=1024,
            temperature=0.2,
        )
        return response.content[0].text
    except Exception as exc:
        # If summarization fails, at least return raw snippets
        fallback = "\n\n".join(context_lines)
        return f"Summarization failed: {exc}\n\nTop results:\n{fallback}"


@mcp.tool
def fetch_file(file_id: str, max_chars: int = 50000) -> str:
    """Fetch all chunks for a specific file from the ChromaDB vector store.

    Returns combined text content for the file with metadata.
    """
    # Query ChromaDB by file_id metadata
    try:
        results = collection.get(
            where={"file_id": file_id},
            include=["documents", "metadatas"],
        )
    except Exception as exc:
        return f"Could not fetch file content for {file_id}: {exc}"

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    if not documents:
        return f"No content found for file_id: {file_id}"

    # Sort chunks by chunk_idx and combine
    chunks = list(zip(documents, metadatas))
    chunks.sort(key=lambda x: x[1].get("chunk_idx", 0))

    filename = metadatas[0].get("filename", "unknown") if metadatas else "unknown"
    combined_text = "\n\n".join(doc for doc, _ in chunks)

    if len(combined_text) > max_chars:
        combined_text = combined_text[:max_chars] + "\n... [truncated]"

    return json.dumps({
        "file_id": file_id,
        "filename": filename,
        "num_chunks": len(chunks),
        "source": "chromadb",
        "text": combined_text,
    })


@mcp.tool
def deep_research(topic: str) -> str:
    """Optional: placeholder for Deep Research integration.

    Enable by setting DEEP_RESEARCH_ENABLED=true and implement per docs.
    """
    if not get_env_bool("DEEP_RESEARCH_ENABLED", False):
        return (
            "Deep Research is disabled. Set DEEP_RESEARCH_ENABLED=true in your .env and "
            "implement the API call per your preferred research API."
        )

    return (
        "Deep Research integration placeholder. Implement your research API call here."
    )


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    if transport == "sse":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "9001"))
        mcp.run(transport="sse", host=host, port=port)
    elif transport == "http":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        path = os.getenv("MCP_HTTP_PATH", "/mcp")
        mcp.run(transport="http", host=host, port=port, path=path)
    else:
        # Default for local IDE clients like Cursor is stdio
        mcp.run(transport="stdio")
