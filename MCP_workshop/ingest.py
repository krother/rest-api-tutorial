#!/usr/bin/env python3
"""Document ingestion script for ChromaDB vector store.

Supports PDF and text files. Chunks documents and stores embeddings locally.

Usage:
    python ingest.py document.pdf
    python ingest.py document.txt
    python ingest.py file1.pdf file2.txt file3.pdf
"""

import os
import sys
import hashlib
from pathlib import Path

from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()


# Configuration
CHUNK_SIZE = 500  # characters per chunk
CHUNK_OVERLAP = 50  # overlap between chunks
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")


def generate_file_id(filepath: str) -> str:
    """Generate a unique file ID based on filename and content hash."""
    path = Path(filepath)
    with open(filepath, "rb") as f:
        content_hash = hashlib.md5(f.read()).hexdigest()[:8]
    return f"{path.stem}_{content_hash}"


def extract_text_from_pdf(filepath: str) -> str:
    """Extract text content from a PDF file."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("Error: pypdf not installed. Run: pip install pypdf")
        sys.exit(1)

    reader = PdfReader(filepath)
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return "\n\n".join(text_parts)


def extract_text_from_file(filepath: str) -> str:
    """Extract text content from a file based on extension."""
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(filepath)
    elif suffix in {".txt", ".md", ".rst", ".csv", ".json", ".xml", ".html"}:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        # Try reading as text
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as exc:
            print(f"Warning: Could not read {filepath}: {exc}")
            return ""


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Try to break at sentence or word boundary (only if not at end)
        if end < text_len:
            # Look for sentence boundary in the last 100 chars of the chunk
            search_start = max(start, end - 100)
            best_boundary = -1
            
            for sep in [". ", ".\n", "! ", "!\n", "? ", "?\n", "\n\n"]:
                boundary = text.rfind(sep, search_start, end)
                if boundary > best_boundary:
                    best_boundary = boundary + len(sep)
            
            if best_boundary > start:
                end = best_boundary
            else:
                # Fall back to word boundary
                space = text.rfind(" ", search_start, end)
                if space > start:
                    end = space + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position - ensure we always make progress
        next_start = end - overlap
        if next_start <= start:
            next_start = end  # Ensure forward progress
        start = next_start if end < text_len else text_len

    return chunks


def ingest_file(filepath: str, collection, embedding_model) -> int:
    """Ingest a single file into the vector store. Returns number of chunks added."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}")
        return 0

    print(f"Processing: {path.name}")

    # Extract text
    text = extract_text_from_file(filepath)
    if not text:
        print(f"  Warning: No text extracted from {path.name}")
        return 0

    # Generate file ID and chunks
    file_id = generate_file_id(filepath)
    chunks = chunk_text(text)

    if not chunks:
        print(f"  Warning: No chunks created from {path.name}")
        return 0

    print(f"  Extracted {len(text)} characters, created {len(chunks)} chunks")

    # Check if file already exists and remove old chunks
    existing = collection.get(where={"file_id": file_id})
    if existing["ids"]:
        print(f"  Removing {len(existing['ids'])} existing chunks for this file")
        collection.delete(ids=existing["ids"])

    # Generate embeddings
    print("  Generating embeddings...")
    embeddings = embedding_model.encode(chunks).tolist()

    # Prepare data for ChromaDB
    ids = [f"{file_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "file_id": file_id,
            "filename": path.name,
            "chunk_idx": i,
            "total_chunks": len(chunks),
        }
        for i in range(len(chunks))
    ]

    # Add to collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    print(f"  Added {len(chunks)} chunks to vector store")
    return len(chunks)


def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <file1> [file2] [file3] ...")
        print("\nSupported formats: PDF, TXT, MD, and other text files")
        print("\nExample:")
        print("  python ingest.py cats.pdf")
        print("  python ingest.py doc1.pdf doc2.txt notes.md")
        sys.exit(1)

    # Initialize ChromaDB and embedding model
    print(f"Initializing ChromaDB at: {CHROMA_DB_PATH}")
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = chroma_client.get_or_create_collection(name="cats_rag")

    print("Loading embedding model (all-MiniLM-L6-v2)...")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    # Process each file
    total_chunks = 0
    for filepath in sys.argv[1:]:
        chunks = ingest_file(filepath, collection, embedding_model)
        total_chunks += chunks

    # Summary
    print(f"\n{'='*50}")
    print(f"Ingestion complete!")
    print(f"  Total chunks added: {total_chunks}")
    print(f"  Total documents in collection: {collection.count()}")
    print(f"  Database location: {CHROMA_DB_PATH}")


if __name__ == "__main__":
    main()
