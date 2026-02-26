# Day 4: RAG Foundations 🧠

Welcome to Phase 2 of the 100 Days of AI! Today we move from basic chains to **Retrieval-Augmented Generation (RAG)**. This is where AI starts working with _your_ private data.

## 📖 The Story: Why RAG?

Imagine you have a super-intelligent assistant (The LLM). It knows everything published on the internet up until last year.

However, you have a private diary or a company policy document that was written yesterday. When you ask the assistant about it, it says: _"I don't know."_

You can't retrain the whole brain (LLM) every time you write a new page. It's too slow and expensive.

**The Solution:** Instead of making the assistant memorize the book, we give it a **Search Engine**. When you ask a question, we quickly find the relevant page, show it to the assistant, and say: _"Read this and answer based on it."_

This system is **RAG**.

---

## 🧱 The 4 Building Blocks

### 1️⃣ Document Loaders (The Doorway)

Before we can use your data, we need to extract it from various formats (PDFs, CSVs, Websites, Notion).

- **Job:** Open the file, extract the text, and turn it into a standard "Document" object.
- **Why?** LLMs can't "see" files directly; they need raw text.

### 2️⃣ Text Splitters (The Shredder)

You can't feed a 500-page book into an LLM all at once (limited context window).

- **Job:** Break large documents into small, manageable "chunks".
- **Concept:** We use **Overlap** (e.g., 200 characters) so that if a sentence is cut in half, the meaning is preserved in the next chunk.

### 3️⃣ Embeddings (The Translator)

Computers don't understand words; they understand numbers.

- **Job:** Convert a chunk of text into a long list of numbers (a **Vector**).
- **Magic:** Similar meanings get similar numbers. "Refund policy" and "Reimbursement rules" will have vectors that are numerically "close" to each other even if the words are different.

### 4️⃣ Vector Stores (The Vault)

A normal database (SQL) is good for finding exact names. A Vector Store is built for finding **meanings**.

- **Job:** Store all those lists of numbers (embeddings) and allow us to search for the "nearest" ones to our question.
- **Examples:** FAISS, ChromaDB, Pinecone.

---

### 🚀 The Full Loop

1. **Load** the PDF → 2. **Split** into Chunks → 3. **Embed** (Math) → 4. **Store** in Vault.
   _(At Query Time: Question → Embed → Search Vault → Give Context to LLM → Answer)_
