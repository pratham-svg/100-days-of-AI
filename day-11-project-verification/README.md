# 🧪 Day 11 — Project Verification & Testing

Welcome to **Day 11**! Today is all about verifying the **Codebase Intelligence Engine** built on [Day 10](../day-10-codebase-intelligence-engine/README.md). We have moved from implementation to a structured testing phase to ensure every component works perfectly.

---

## 🏗️ Project Overview

Reflecting on Day 10, we built a modular RAG system for codebases. Today, we verify the following 7 critical steps:

1.  **GitHub Ingestion**: Cloning and walking files.
2.  **AST-Aware Chunking**: Parsing code with `tree-sitter`.
3.  **Embeddings & Indexing**: Generating vectors and storing in Qdrant Cloud.
4.  **Hybrid Search**: Combining Dense (Semantic) and Sparse (Keyword) search.
5.  **LLM Reranking (Optimized)**: Using OpenRouter to rank results (removed local model weight burden!).
6.  **Answer Synthesis**: Synthesizing expert answers with source attribution.
7.  **FastAPI Integration**: Testing the end-to-end API.

---

## 📂 Verification Folder Structure

I have organized the tests into a dedicated `steps/` folder for clarity:

```text
day-11-project-verification/
├── README.md                # This documentation
└── steps/                   # Individual test scripts for each phase
    ├── test_step1.py        # GitHub Loader Test
    ├── test_step2.py        # AST Chunker Test
    ├── test_step3.py        # Indexing & Embeddings Test
    ├── test_step4.py        # Hybrid Search Test
    ├── test_step5.py        # LLM Reranking Test
    ├── test_step6.py        # Answer Generation Test
    └── test_step7.py        # FastAPI Server Test
```

---

## 🚦 How to Run the Verifications

To verify each step, navigate to the `day-10-codebase-intelligence-engine` directory and run the scripts from there (to ensure imports work correctly):

### 1️⃣ Step 1: GitHub Ingestion

```powershell
uv run python tests/test_step1.py
```

_Checks if cloning and file walking works on Windows._

### 2️⃣ Step 2: AST Chunking

```powershell
uv run python tests/test_step2.py
```

_Verifies that functions and classes are extracted correctly using tree-sitter._

### 3️⃣ Step 3: Indexing

```powershell
uv run python tests/test_step3.py
```

_Tests the connection to Qdrant Cloud and OpenRouter Embeddings._

### 4️⃣ Step 4: Hybrid Search

```powershell
uv run python tests/test_step4.py
```

_Confirms that we can retrieve code chunks from the vector store._

### 5️⃣ Step 5: LLM Reranking

```powershell
uv run python tests/test_step5.py
```

_Verifies the new cloud-based reranker (replacing the heavy local model)._

### 6️⃣ Step 6: Synthesis

```powershell
uv run python tests/test_step6.py
```

_Tests the final LLM response generation with source links._

---

## 🛠️ Key Fixes Implemented Today

During verification, we identified and fixed several issues:

- **Windows Permission Errors**: Added `on_rm_error` handlers for deleting `.git` folders.
- **Empty Chunk Handling**: Filtered out empty strings to prevent API errors.
- **Robust Config**: Improved `.env` loading to work across different working directories.
- **Cloud Reranking**: Replaced the local `sentence-transformers` model with an **LLM-based reranker via OpenRouter** to achieve near-instant server startup times.

---

## 🔗 Links

- [Day 10 Implementation](../day-10-codebase-intelligence-engine/README.md)
- [Back to root](../../README.md)
