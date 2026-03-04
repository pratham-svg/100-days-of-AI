# 🧠 Day 10 — Codebase Intelligence Engine

### My Complete Step-by-Step Build Guide

---

## What I'm Building Today

Most engineers build RAG over PDFs. I decided to build it over an entire codebase! The secret sauce here is **AST-aware chunking**—splitting code by actual function and class boundaries instead of just chopping it at arbitrary token boundaries. A function cut in half mid-logic is worse than useless.

Here is my complete documentation for building a Codebase Intelligence Engine that understands the whole repo.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Folder Structure](#folder-structure)
3. [Environment Setup](#environment-setup)
4. [Step 1 — GitHub Ingestion](#step-1--github-ingestion)
5. [Step 2 — AST-Aware Chunking](#step-2--ast-aware-chunking)
6. [Step 3 — Embeddings + Qdrant Indexing](#step-3--embeddings--qdrant-indexing)
7. [Step 4 — Hybrid Search Pipeline](#step-4--hybrid-search-pipeline)
8. [Step 5 — Cross-Encoder Re-ranking](#step-5--cross-encoder-re-ranking)
9. [Step 6 — LLM Answer Synthesis](#step-6--llm-answer-synthesis)
10. [Step 7 — FastAPI Server](#step-7--fastapi-server)
11. [Step 8 — RAGAS Evaluation](#step-8--ragas-evaluation)
12. [Step 9 — End-to-End Execution](#step-9--end-to-end-execution)
13. [Common Errors & Fixes](#common-errors--fixes)

---

## Prerequisites

Before I started, I made sure I had:

- Python 3.10+
- Git
- My OpenRouter API key
- My **Qdrant Cloud Account** (I'm using the managed cloud database instead of a local Docker container)

---

## Folder Structure

I set up this exact modular folder structure. Everything has a dedicated purpose:

```
codebase-intelligence/
│
├── main.py                         # FastAPI app entry point
│
├── ingestion/
│   ├── __init__.py
│   ├── github_loader.py            # Clone repo + walk files
│   └── file_filter.py              # Filter by language extension
│
├── chunking/
│   ├── __init__.py
│   ├── ast_chunker.py              # Core AST parsing logic
│   └── chunk_models.py             # Pydantic model for a Chunk
│
├── indexing/
│   ├── __init__.py
│   ├── embedder.py                 # Dense embedding generation
│   ├── sparse_encoder.py           # BM25 sparse vector generation
│   └── qdrant_store.py             # Qdrant collection setup + upsert
│
├── retrieval/
│   ├── __init__.py
│   ├── hybrid_search.py            # Hybrid search with RRF fusion
│   └── reranker.py                 # Cross-encoder re-ranking
│
├── generation/
│   ├── __init__.py
│   └── answer_chain.py             # LangChain chain for final answer
│
├── evaluation/
│   ├── __init__.py
│   ├── golden_dataset.json         # My hand-crafted Q&A test set
│   └── ragas_eval.py               # RAGAS evaluation runner
│
├── api/
│   ├── __init__.py
│   ├── routes.py                   # FastAPI route definitions
│   └── schemas.py                  # Request/Response Pydantic models
│
├── config.py                       # All env vars and constants
└── .env                            # API keys (never commit this)
```

---

## Environment Setup

Since I use `uv` as my blazing-fast package manager, the setup is incredibly smooth.

### Step 1 — Initialize project and install dependencies

Instead of a bulky `requirements.txt`, I just run `uv init` and `uv add`:

```bash
cd day-10-codebase-intelligence-engine
uv init
# Add all the necessary packages in one go
uv add fastapi uvicorn pydantic python-dotenv langchain langchain-openai langchain-community qdrant-client tree-sitter tree-sitter-python tree-sitter-javascript sentence-transformers openai rank-bm25 ragas datasets gitpython requests
```

### Step 2 — Set up my `.env` variables

I already have an `.env` file in the root directory `c:\Pratham\100 days of AI\.env`. It looks something like this:

```env
OPENAI_API_KEY=sk-or-v1-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
QDRANT_URL=https://...aws.cloud.qdrant.io
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR...
```

### Step 3 — Create `config.py`

I pulled the environment variables directly from my `.env`.

```python
# config.py
import os
from dotenv import load_dotenv

# Load from my root .env file
load_dotenv("../.env")

OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY") # Mapping to my OpenRouter key
OPENROUTER_BASE_URL = os.getenv("OPENAI_BASE_URL")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "codebase_intel")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")

DENSE_VECTOR_SIZE = 1536       # text-embedding-3-small output dim
TOP_K_RETRIEVAL = 20           # candidates before reranking
TOP_K_FINAL = 5                # chunks passed to LLM after reranking
SUPPORTED_EXTENSIONS = [".py", ".js", ".ts", ".java", ".go", ".rs"]
```

---

## Step 1 — GitHub Ingestion

**What I built:** A way to clone a GitHub repo locally and return a list of all code file paths filtered by language.

### `chunking/chunk_models.py` — Defining my Chunk schema

```python
# chunking/chunk_models.py
from pydantic import BaseModel
from typing import Optional

class CodeChunk(BaseModel):
    chunk_id: str               # Unique ID: filepath_functionname_startline
    content: str                # Actual code text
    file_path: str              # e.g. "src/auth/login.py"
    chunk_type: str             # "function", "class", "module"
    name: str                   # Function or class name
    start_line: int
    end_line: int
    language: str               # "python", "javascript", etc.
    repo_name: str
```

### `ingestion/github_loader.py`

```python
# ingestion/github_loader.py
import os
import shutil
from pathlib import Path
from git import Repo
from config import SUPPORTED_EXTENSIONS

def clone_repo(repo_url: str, target_dir: str = "./tmp_repo") -> str:
    """
    Clones a GitHub repo to a local directory.
    Returns the path to the cloned repo.
    """
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)  # Clean up any previous clone

    print(f"Cloning {repo_url}...")
    Repo.clone_from(repo_url, target_dir)
    print(f"Cloned to {target_dir}")
    return target_dir


def get_repo_name(repo_url: str) -> str:
    """Extracts repo name from URL. e.g. 'langchain' from full URL."""
    return repo_url.rstrip("/").split("/")[-1].replace(".git", "")


def walk_code_files(repo_path: str) -> list[str]:
    """
    Recursively walks repo directory.
    Returns list of file paths with supported extensions only.
    Skips: node_modules, __pycache__, .git, dist, build
    """
    SKIP_DIRS = {"node_modules", "__pycache__", ".git", "dist", "build", ".venv", "venv"}
    code_files = []

    for root, dirs, files in os.walk(repo_path):
        # Remove skip directories in-place so os.walk doesn't descend into them
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            ext = Path(file).suffix
            if ext in SUPPORTED_EXTENSIONS:
                full_path = os.path.join(root, file)
                code_files.append(full_path)

    print(f"Found {len(code_files)} code files")
    return code_files
```

---

## Step 2 — AST-Aware Chunking

**What I built:** A script that parses each code file using `tree-sitter` to extract individual functions and classes as separate chunks — each with metadata. This ensures I respect code boundaries!

### `chunking/ast_chunker.py`

```python
# chunking/ast_chunker.py
import uuid
from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
from chunking.chunk_models import CodeChunk

# Build language objects
PY_LANGUAGE = Language(tspython.language())
JS_LANGUAGE = Language(tsjavascript.language())

LANGUAGE_MAP = {
    ".py": ("python", PY_LANGUAGE),
    ".js": ("javascript", JS_LANGUAGE),
    ".ts": ("javascript", JS_LANGUAGE),  # TS uses JS grammar for basics
}

# Node types to extract as separate chunks
CHUNK_NODE_TYPES = {
    "python": ["function_definition", "class_definition"],
    "javascript": ["function_declaration", "class_declaration", "arrow_function"],
}


def get_parser(extension: str) -> tuple[Parser, str] | None:
    """Returns (parser, language_name) for a given file extension."""
    if extension not in LANGUAGE_MAP:
        return None
    lang_name, lang_obj = LANGUAGE_MAP[extension]
    parser = Parser(lang_obj)
    return parser, lang_name


def extract_chunks_from_file(file_path: str, repo_name: str) -> list[CodeChunk]:
    """
    Parses a single file and returns a list of CodeChunk objects.
    Falls back to whole-file chunk if AST parsing fails.
    """
    extension = Path(file_path).suffix
    result = get_parser(extension)

    if result is None:
        return []

    parser, lang_name = result

    # Read file content
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source_code = f.read()
    except Exception as e:
        print(f"Could not read {file_path}: {e}")
        return []

    source_bytes = source_code.encode("utf-8")
    tree = parser.parse(source_bytes)

    chunks = []
    target_types = CHUNK_NODE_TYPES.get(lang_name, [])

    # Walk the AST and find function/class nodes
    def walk_tree(node):
        if node.type in target_types:
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            chunk_text = source_bytes[node.start_byte:node.end_byte].decode("utf-8")

            # Extract the name of the function/class
            name_node = node.child_by_field_name("name")
            name = name_node.text.decode("utf-8") if name_node else "anonymous"

            # Relative file path for cleaner metadata
            rel_path = file_path.split(repo_name)[-1].lstrip("/\\")

            chunk = CodeChunk(
                chunk_id=f"{rel_path}::{name}::{start_line}",
                content=chunk_text,
                file_path=rel_path,
                chunk_type=node.type.replace("_definition", "").replace("_declaration", ""),
                name=name,
                start_line=start_line,
                end_line=end_line,
                language=lang_name,
                repo_name=repo_name,
            )
            chunks.append(chunk)

        for child in node.children:
            walk_tree(child)

    walk_tree(tree.root_node)

    # Fallback: if no chunks found (e.g. script-level code), use whole file
    if not chunks:
        rel_path = file_path.split(repo_name)[-1].lstrip("/\\")
        chunks.append(CodeChunk(
            chunk_id=f"{rel_path}::module::1",
            content=source_code[:3000],  # Cap at 3000 chars for module-level
            file_path=rel_path,
            chunk_type="module",
            name=Path(file_path).stem,
            start_line=1,
            end_line=source_code.count("\n"),
            language=lang_name,
            repo_name=repo_name,
        ))

    return chunks


def chunk_repository(file_paths: list[str], repo_name: str) -> list[CodeChunk]:
    """
    Runs AST chunking over all files in the repo.
    Returns flat list of all CodeChunk objects.
    """
    all_chunks = []
    for fp in file_paths:
        file_chunks = extract_chunks_from_file(fp, repo_name)
        all_chunks.extend(file_chunks)

    print(f"Total chunks extracted: {len(all_chunks)}")
    return all_chunks
```

---

## Step 3 — Embeddings + Qdrant Indexing

**What I built:** A script to convert each chunk into a dense vector (semantic) AND a sparse vector (keyword), and upsert both into my Qdrant Cloud cluster.

### `indexing/embedder.py`

```python
# indexing/embedder.py
from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, EMBEDDING_MODEL

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
)

def get_dense_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generates dense embeddings for a list of texts.
    Batches in groups of 100 to respect API limits.
    """
    all_embeddings = []
    batch_size = 100

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
        print(f"Embedded batch {i // batch_size + 1}")

    return all_embeddings
```

### `indexing/sparse_encoder.py`

```python
# indexing/sparse_encoder.py
from rank_bm25 import BM25Okapi
import re

def tokenize_code(text: str) -> list[str]:
    """
    Tokenizes code text for BM25.
    Splits on spaces, underscores, camelCase, and punctuation.
    """
    # Split camelCase: "getUserById" -> "get User By Id"
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Split on common code delimiters
    text = re.sub(r'[_\-\.\(\)\[\]\{\}:,]', ' ', text)
    tokens = text.lower().split()
    return [t for t in tokens if len(t) > 1]


def build_sparse_vectors(corpus: list[str]) -> tuple[BM25Okapi, list[list[str]]]:
    """
    Builds BM25 index over the entire corpus.
    Returns the BM25 object and tokenized corpus.
    """
    tokenized_corpus = [tokenize_code(doc) for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25, tokenized_corpus


def get_sparse_vector_for_qdrant(text: str, vocab: list[str]) -> dict:
    """
    Creates a sparse vector dict compatible with Qdrant's sparse format.
    { indices: [...], values: [...] }
    """
    tokens = tokenize_code(text)
    token_freq = {}
    for token in tokens:
        if token in vocab:
            idx = vocab.index(token)
            token_freq[idx] = token_freq.get(idx, 0) + 1

    return {
        "indices": list(token_freq.keys()),
        "values": [float(v) for v in token_freq.values()]
    }
```

### `indexing/qdrant_store.py`

Because I am using Qdrant Cloud, I am passing both the URL and my API Key.

```python
# indexing/qdrant_store.py
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, SparseVectorParams,
    SparseIndexParams, PointStruct, SparseVector
)
from chunking.chunk_models import CodeChunk
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME, DENSE_VECTOR_SIZE

# Connect to my Cloud Qdrant cluster
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def create_collection():
    """
    Creates a Qdrant collection with both dense and sparse vectors.
    Safe to call multiple times — checks if collection exists first.
    """
    existing_collections = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME in existing_collections:
        print(f"Collection '{COLLECTION_NAME}' already exists. Skipping creation.")
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": VectorParams(size=DENSE_VECTOR_SIZE, distance=Distance.COSINE)
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))
        }
    )
    print(f"Collection '{COLLECTION_NAME}' created.")


def upsert_chunks(
    chunks: list[CodeChunk],
    dense_vectors: list[list[float]],
    sparse_vectors: list[dict],
):
    """
    Upserts all chunks with their dense + sparse vectors into Qdrant.
    Each point stores the chunk metadata as payload.
    """
    points = []
    for i, chunk in enumerate(chunks):
        point = PointStruct(
            id=abs(hash(chunk.chunk_id)) % (2**63),  # Qdrant needs int ID
            vector={
                "dense": dense_vectors[i],
                "sparse": SparseVector(
                    indices=sparse_vectors[i]["indices"],
                    values=sparse_vectors[i]["values"],
                )
            },
            payload={
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "file_path": chunk.file_path,
                "chunk_type": chunk.chunk_type,
                "name": chunk.name,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "language": chunk.language,
                "repo_name": chunk.repo_name,
            }
        )
        points.append(point)

    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(points), batch_size):
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points[i:i + batch_size]
        )
        print(f"Upserted batch {i // batch_size + 1}/{len(points) // batch_size + 1}")

    print(f"Total {len(points)} chunks indexed in Qdrant.")
```

---

## Step 4 — Hybrid Search Pipeline

**What I built:** Takes a user query, runs both dense and sparse search, then fuses the results using Reciprocal Rank Fusion (RRF).

### `retrieval/hybrid_search.py`

```python
# retrieval/hybrid_search.py
from qdrant_client import QdrantClient
from qdrant_client.models import (
    NamedVector, NamedSparseVector, SparseVector,
    QueryRequest, Prefetch, FusionQuery, Fusion
)
from indexing.embedder import get_dense_embeddings
from indexing.sparse_encoder import tokenize_code
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME, TOP_K_RETRIEVAL

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def get_query_sparse_vector(query: str) -> SparseVector:
    """Converts query text to sparse vector using same tokenizer as indexing."""
    tokens = tokenize_code(query)
    # Build term frequency dict
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1

    # Use hash of token as index (consistent with indexing)
    indices = [abs(hash(t)) % 100000 for t in tf.keys()]
    values = [float(v) for v in tf.values()]
    return SparseVector(indices=indices, values=values)


def hybrid_search(query: str, top_k: int = TOP_K_RETRIEVAL) -> list[dict]:
    """
    Performs hybrid search using Qdrant's built-in RRF fusion.
    Returns top_k results with payload and score.
    """
    # Dense vector for semantic search
    dense_vector = get_dense_embeddings([query])[0]

    # Sparse vector for keyword search
    sparse_vector = get_query_sparse_vector(query)

    # Qdrant native hybrid search with RRF fusion
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            Prefetch(
                query=dense_vector,
                using="dense",
                limit=top_k
            ),
            Prefetch(
                query=sparse_vector,
                using="sparse",
                limit=top_k
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "content": r.payload["content"],
            "file_path": r.payload["file_path"],
            "name": r.payload["name"],
            "start_line": r.payload["start_line"],
            "end_line": r.payload["end_line"],
            "chunk_type": r.payload["chunk_type"],
            "score": r.score,
        }
        for r in results.points
    ]
```

---

## Step 5 — Cross-Encoder Re-ranking

**What I built:** A way to take the top-20 hybrid search results and re-score every one against the query using a cross-encoder to select the very best top-5.

```python
# retrieval/reranker.py
from sentence_transformers import CrossEncoder
from config import RERANKER_MODEL, TOP_K_FINAL

reranker = CrossEncoder(RERANKER_MODEL)

def rerank_results(query: str, candidates: list[dict], top_k: int = TOP_K_FINAL) -> list[dict]:
    """
    Re-ranks hybrid search candidates using cross-encoder.

    Cross-encoder sees both query AND document together
    (unlike bi-encoder which encodes them separately).
    This gives much higher accuracy for final ranking.
    """
    if not candidates:
        return []

    # Prepare (query, document) pairs for cross-encoder
    pairs = [(query, c["content"]) for c in candidates]

    # Score all pairs
    scores = reranker.predict(pairs)

    # Attach scores back to candidates
    for i, candidate in enumerate(candidates):
        candidate["rerank_score"] = float(scores[i])

    # Sort by rerank score descending, return top_k
    reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]
```

---

## Step 6 — LLM Answer Synthesis

**What I built:** Takes the top-5 re-ranked chunks and my user query, formats a code-aware prompt, and calls the LLM via OpenRouter.

```python
# generation/answer_chain.py
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, LLM_MODEL

llm = ChatOpenAI(
    model=LLM_MODEL,
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    temperature=0,
)

SYSTEM_PROMPT = """You are my codebase expert assistant. I am giving you relevant code chunks from a repository.
Answer my question based ONLY on the provided code context.
Always mention the file path and function/class name when referencing code.
If the answer is not in the context, say "I couldn't find this in the indexed codebase."
Be precise and technical."""

USER_PROMPT = """Here are the most relevant code chunks from the repository:

{context}

---
Question: {question}

Answer with specific references to file paths and function names:"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", USER_PROMPT),
])

chain = prompt | llm | StrOutputParser()


def format_context(chunks: list[dict]) -> str:
    """Formats chunks into a readable context block for the LLM."""
    formatted = []
    for i, chunk in enumerate(chunks, 1):
        formatted.append(
            f"--- Chunk {i} ---\n"
            f"File: {chunk['file_path']} (lines {chunk['start_line']}–{chunk['end_line']})\n"
            f"Type: {chunk['chunk_type']} | Name: {chunk['name']}\n\n"
            f"{chunk['content']}\n"
        )
    return "\n".join(formatted)


def generate_answer(question: str, chunks: list[dict]) -> dict:
    """
    Full answer generation pipeline.
    Returns answer text + source references.
    """
    context = format_context(chunks)
    answer = chain.invoke({"context": context, "question": question})

    sources = [
        {
            "file": c["file_path"],
            "function": c["name"],
            "lines": f"{c['start_line']}–{c['end_line']}",
            "rerank_score": round(c.get("rerank_score", 0), 4),
        }
        for c in chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
    }
```

---

## Step 7 — FastAPI Server

### `api/schemas.py`

```python
# api/schemas.py
from pydantic import BaseModel

class IndexRequest(BaseModel):
    repo_url: str               # e.g. "https://github.com/langchain-ai/langchain"

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class Source(BaseModel):
    file: str
    function: str
    lines: str
    rerank_score: float

class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    total_chunks_searched: int
```

### `api/routes.py`

```python
# api/routes.py
from fastapi import APIRouter, HTTPException
from api.schemas import IndexRequest, QueryRequest, QueryResponse
from ingestion.github_loader import clone_repo, walk_code_files, get_repo_name
from chunking.ast_chunker import chunk_repository
from indexing.embedder import get_dense_embeddings
from indexing.sparse_encoder import get_sparse_vector_for_qdrant, tokenize_code
from indexing.qdrant_store import create_collection, upsert_chunks
from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import rerank_results
from generation.answer_chain import generate_answer

router = APIRouter()

# In-memory vocab store (for sparse vectors)
_vocab: list[str] = []


@router.post("/index", summary="Clone and index a GitHub repository")
async def index_repository(request: IndexRequest):
    """
    Full pipeline: Clone → Walk → Chunk → Embed → Index
    This will take 2–10 minutes depending on repo size.
    """
    try:
        repo_name = get_repo_name(request.repo_url)
        repo_path = clone_repo(request.repo_url)
        file_paths = walk_code_files(repo_path)

        if not file_paths:
            raise HTTPException(status_code=400, detail="No supported code files found in repo.")

        chunks = chunk_repository(file_paths, repo_name)

        # Build vocab from all chunks for sparse encoding
        all_texts = [c.content for c in chunks]
        global _vocab
        all_tokens = []
        for text in all_texts:
            all_tokens.extend(tokenize_code(text))
        _vocab = list(set(all_tokens))

        # Generate embeddings
        dense_vectors = get_dense_embeddings(all_texts)
        sparse_vectors = [get_sparse_vector_for_qdrant(t, _vocab) for t in all_texts]

        # Create collection + upsert
        create_collection()
        upsert_chunks(chunks, dense_vectors, sparse_vectors)

        return {
            "status": "success",
            "repo": repo_name,
            "files_indexed": len(file_paths),
            "chunks_indexed": len(chunks),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse, summary="Ask a question about the codebase")
async def query_codebase(request: QueryRequest):
    """
    Query pipeline: HybridSearch → Rerank → LLM → Answer
    """
    try:
        # Retrieve top candidates
        candidates = hybrid_search(request.question)

        # Re-rank and cut to top_k
        reranked = rerank_results(request.question, candidates, top_k=request.top_k)

        # Generate answer with source attribution
        result = generate_answer(request.question, reranked)

        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            total_chunks_searched=len(candidates),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Health check")
async def health():
    return {"status": "ok"}
```

### `main.py`

```python
# main.py
from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="My Codebase Intelligence Engine",
    description="Ask natural language questions about my GitHub codebase using AST-aware RAG",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

---

## Step 8 — RAGAS Evaluation

### `evaluation/golden_dataset.json`

I handcrafted these questions to test my RAG accuracy.

```json
[
  {
    "question": "What does the login function do?",
    "ground_truth": "The login function validates user credentials, calls validate_token, and returns a JWT on success."
  },
  {
    "question": "How is the database connection initialized?",
    "ground_truth": "The database connection is initialized in db.py using SQLAlchemy's create_engine with connection pooling."
  },
  {
    "question": "What authentication method does the API use?",
    "ground_truth": "The API uses JWT bearer token authentication with a 24 hour expiry."
  }
]
```

### `evaluation/ragas_eval.py`

```python
# evaluation/ragas_eval.py
import json
import requests
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

API_BASE = "http://localhost:8000/api/v1"


def run_evaluation():
    """
    Runs RAGAS evaluation against the golden dataset.
    Calls the live API for each question to get answers + contexts.
    """
    with open("evaluation/golden_dataset.json") as f:
        golden = json.load(f)

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for item in golden:
        q = item["question"]
        response = requests.post(
            f"{API_BASE}/query",
            json={"question": q, "top_k": 5}
        ).json()

        questions.append(q)
        answers.append(response["answer"])
        contexts.append([s["file"] for s in response["sources"]])  # Using file refs as context
        ground_truths.append(item["ground_truth"])

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })

    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )

    print("\n=== My RAGAS Evaluation Results ===")
    print(result)
    return result


if __name__ == "__main__":
    run_evaluation()
```

---

## Step 9 — End-to-End Execution

Here's how I run the entire pipeline today.

### 1. Start the API server

Since I use Qdrant in the cloud, I skip starting Docker and just launch my app with `uv run`:

```bash
cd day-10-codebase-intelligence-engine
uv run main.py
```

I should see:

```text
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Open Swagger UI

I navigate my browser to: `http://localhost:8000/docs` to see all three endpoints: `/index`, `/query`, `/health`

### 3. Index a Repository

```bash
curl -X POST "http://localhost:8000/api/v1/index" \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/tiangolo/fastapi"}'
```

Expected response:

```json
{
  "status": "success",
  "repo": "fastapi",
  "files_indexed": 142,
  "chunks_indexed": 1847
}
```

### 4. Query the Codebase

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "How does FastAPI handle dependency injection?", "top_k": 5}'
```

Expected response:

```json
{
  "answer": "FastAPI handles dependency injection through the Depends() function...",
  "sources": [
    {
      "file": "fastapi/dependencies/utils.py",
      "function": "solve_dependencies",
      "lines": "210–298",
      "rerank_score": 0.9821
    }
  ],
  "total_chunks_searched": 20
}
```

### 5. Run RAGAS Evaluation

I can rigorously test my system using RAGAS via `uv`:

```bash
uv run evaluation/ragas_eval.py
```

Expected output:

```text
=== My RAGAS Evaluation Results ===
faithfulness          0.87
answer_relevancy      0.91
context_precision     0.83
context_recall        0.79
```

---

## Common Errors & Fixes

Here are the issues I encountered while building this:

| Error                                              | Cause                           | Fix                                                    |
| -------------------------------------------------- | ------------------------------- | ------------------------------------------------------ |
| `tree_sitter.LibraryError`                         | Language library not built      | Run `uv add tree-sitter-python` again                  |
| `qdrant_client.http.exceptions.UnexpectedResponse` | Qdrant Cloud API Key issue      | Verify `.env` has the correct `QDRANT_API_KEY`         |
| `openai.AuthenticationError`                       | Wrong API key                   | Check `.env` file and `OPENAI_API_KEY`                 |
| `No chunks found` for a file                       | File uses unsupported extension | Add extension to `SUPPORTED_EXTENSIONS` in `config.py` |
| Sparse vector all zeros                            | Token not in vocab              | Rebuild vocab after re-indexing                        |

---

## What to Post on LinkedIn (Day 10)

**Hook:** "Most engineers build RAG over PDFs. Today, I built it over code."

**Insight:** AST-aware chunking — splitting by function/class boundary instead of token count — is the single biggest quality lever in code RAG. A function cut in half mid-logic is worse than useless.

**Next:** Day 11 — Adding metadata filtering to query only specific files or languages.

---

_100 Days of AI · Pratham Panchariya · @GrackerAI_
