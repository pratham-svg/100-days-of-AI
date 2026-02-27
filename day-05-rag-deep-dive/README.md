# Day 05: RAG Deep Dive & Embeddings

Welcome to Day 5! Today we dive deeper into the mechanics of **Retrieval-Augmented Generation (RAG)**. We are focusing on two massive foundational pillars: how we break down data (**Chunking**) and how machines understand language (**Embeddings**).

To make studying easier and more visual, the Day 5 contents have been broken out into 4 modular chapters.

---

## 📖 Table of Contents

### 1. [Chunking Strategies](./01_CHUNKING_STRATEGIES.md)

Discover _Fixed-Size_, _Recursive_, _Semantic_, and _Document-Aware_ chunking. Learn why adding an **Overlap** is crucial for preventing context loss between splits.

### 2. [Text to Numbers Pipeline](./02_TEXT_TO_NUMBERS.md)

Trace the 5-step journey of text: from Tokenization to IDs, dense vectors, Self-Attention, and final vector Pooling.

### 3. [Attention & Training Mechanics](./03_ATTENTION_AND_TRAINING.md)

Understand what **Self-Attention** does (context-awareness) and how embedding models use **Contrastive Learning** (push/pull forces) to create semantic maps.

### 4. [Similarity & Core RAG Model](./04_SIMILARITY_AND_MODEL.md)

Explore why **Cosine Similarity** (direction) beats Euclidean (distance). Conclude with a visual master chart of the entire RAG "Language as Geometry" mental model!

---

> **Tip for Revision:** Use a markdown previewer (like VS Code's `Ctrl+Shift+V`) to see all the interactive Mermaid flowcharts in each chapter!
