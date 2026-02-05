#!/usr/bin/env python3
"""Terminal chat interface that uses Claude API with MCP tools.

This demonstrates calling MCP tools directly via the Anthropic API,
simulating what Claude Desktop or Cursor do under the hood.

Usage:
    python chat.py
"""

import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

if not ANTHROPIC_API_KEY:
    print("Error: ANTHROPIC_API_KEY not set in .env file")
    exit(1)

# Initialize clients
print("Initializing...")
client_kwargs = {"api_key": ANTHROPIC_API_KEY}
if ANTHROPIC_BASE_URL:
    client_kwargs["base_url"] = ANTHROPIC_BASE_URL
anthropic = Anthropic(**client_kwargs)

# Initialize ChromaDB and embedding model
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(name="cats_rag")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print(f"Connected to ChromaDB with {collection.count()} documents")
print(f"Using model: {ANTHROPIC_MODEL}")
print("-" * 50)

# Define tools for Claude
TOOLS = [
    {
        "name": "search_cats",
        "description": "Semantic search over the local ChromaDB vector store. Returns relevant text chunks with relevance scores.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "k": {
                    "type": "integer",
                    "description": "Number of results to return (default 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "fetch_file",
        "description": "Fetch all chunks for a specific file from the vector store by file_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_id": {
                    "type": "string",
                    "description": "The file ID to fetch"
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum characters to return (default 50000)",
                    "default": 50000
                }
            },
            "required": ["file_id"]
        }
    }
]


def execute_tool(name: str, arguments: dict) -> str:
    """Execute an MCP tool and return the result."""
    
    if name == "search_cats":
        query = arguments.get("query", "")
        k = arguments.get("k", 5)
        
        if collection.count() == 0:
            return "No documents in the vector store."
        
        # Embed query and search
        query_embedding = embedding_model.encode([query]).tolist()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
        
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        if not documents:
            return "No results found."
        
        output_lines = [f"Search results for: {query}\n"]
        for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
            filename = meta.get("filename", "unknown")
            chunk_idx = meta.get("chunk_idx", 0)
            score = 1 / (1 + dist)
            preview = (doc or "").strip()[:500]
            output_lines.append(
                f"[Result {idx + 1}] file={filename} (chunk {chunk_idx}) score={score:.4f}\n{preview}\n"
            )
        
        return "\n".join(output_lines)
    
    elif name == "fetch_file":
        file_id = arguments.get("file_id", "")
        max_chars = arguments.get("max_chars", 50000)
        
        results = collection.get(
            where={"file_id": file_id},
            include=["documents", "metadatas"],
        )
        
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        
        if not documents:
            return f"No content found for file_id: {file_id}"
        
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
            "text": combined_text,
        })
    
    return f"Unknown tool: {name}"


def chat(user_message: str, conversation_history: list) -> str:
    """Send a message to Claude and handle tool calls."""
    
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    # Initial API call
    response = anthropic.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4096,
        system="You are a helpful assistant with access to a knowledge base about cats. Use the search_cats tool to find information when the user asks questions about cats. Be concise and cite your sources.",
        tools=TOOLS,
        messages=conversation_history
    )
    
    # Handle tool use loop
    while response.stop_reason == "tool_use":
        # Extract tool calls
        tool_calls = [block for block in response.content if block.type == "tool_use"]
        
        # Add assistant's response to history
        conversation_history.append({
            "role": "assistant",
            "content": response.content
        })
        
        # Execute tools and collect results
        tool_results = []
        for tool_call in tool_calls:
            print(f"  [Calling tool: {tool_call.name}]")
            result = execute_tool(tool_call.name, tool_call.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": result
            })
        
        # Add tool results to history
        conversation_history.append({
            "role": "user",
            "content": tool_results
        })
        
        # Continue the conversation
        response = anthropic.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4096,
            system="You are a helpful assistant with access to a knowledge base about cats. Use the search_cats tool to find information when the user asks questions about cats. Be concise and cite your sources.",
            tools=TOOLS,
            messages=conversation_history
        )
    
    # Extract final text response
    final_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            final_text += block.text
    
    # Add assistant's final response to history
    conversation_history.append({
        "role": "assistant",
        "content": response.content
    })
    
    return final_text


def main():
    print("\n🐱 Cats Knowledge Base Chat")
    print("Type 'quit' to exit, 'clear' to reset conversation\n")
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        
        if user_input.lower() == "clear":
            conversation_history = []
            print("Conversation cleared.\n")
            continue
        
        try:
            response = chat(user_input, conversation_history)
            print(f"\nAssistant: {response}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
