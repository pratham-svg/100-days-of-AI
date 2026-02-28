# Day 6: Multi-Document Research Assistant

Today, I built a Multi-Document Research Assistant. The goal was to move beyond simple chatbots and create a tool that can synthesize information across multiple research papers while providing accurate source attribution.

**Tech Stack:** LangChain + Qdrant + FastAPI + OpenRouter

---

### Step 1: Gathering the Documents

I started by selecting a focused topic: **LLM Engineering and RAG**. I downloaded 4-5 PDFs from ArXiv and other technical sources. Keeping them strictly on one topic ensured that testing cross-document queries would be meaningful and challenging.

---

### Step 2: Document Loading & Metadata Preservation

Instead of blindly dumping text, I made sure to preserve metadata during the loading phase. I manually tagged each document with its source filename and topic ("RAG"). Without this metadata, the assistant wouldn't be able to tell the user _which_ document answered their question—a critical feature for a real research tool.

---

### Step 3: Implementing a Chunking Strategy

Rather than using default chunk sizes, I experimented with different approaches. I tested how different overlap sizes affected the retrieval of concepts that spanned multiple paragraphs. This overlap analysis turned out to be one of the most important insights of the build.

---

### Step 4: Embeddings and Vector Store (Qdrant)

I converted the document chunks into vector embeddings and stored them in **Qdrant** instead of FAISS. I also made sure to persist the Qdrant collection to disk, avoiding the need to re-embed the documents every time I ran the application.

---

### Step 5: Building a Metadata-Aware Retriever

To elevate this from a basic QA bot to a research assistant, I configured the Qdrant retriever to perform similarity searches while filtering by metadata. This allows for dynamic queries later on, such as "only search this specific paper" or "search all papers related to this topic."

---

### Step 6: Engineering Source Attribution

This was the most challenging but essential part. I set up the retrieval chain to return the specific document and page number that answered the question. Every response now includes the synthesized answer along with exact citations, making it a trustworthy research companion.

---

### Step 7: Cross-Document Synthesis Prompt

I designed a custom prompt instructing the LLM to act as a research assistant. I explicitly told it to:

- Synthesize information if it comes from multiple documents.
- Mention each source clearly.
- State when it _cannot_ find an answer, strictly preventing hallucinations.

---

### Step 8: FastAPI Endpoint Integration

Finally, I wrapped the entire pipeline in a FastAPI endpoint. The API accepts a search query and an optional topic filter, runs the retrieval chain, and returns a clean JSON response containing the answer, the source documents, and the page numbers.

---

### Verification and Testing

I ran several tests to ensure the system worked as intended:

- **Cross-document synthesis:** "What do different papers say about chunking strategies?"
- **Source attribution:** "Which paper specifically discusses hybrid search?"
- **Retrieval breadth:** "Summarize the key arguments from all documents."
- **Hallucination resistance:** Asked a completely unrelated question to verify the bot would admit it didn't know the answer.

---

### Key Takeaway for the Day

The biggest lesson today was that successfully asking the same question to 10 research papers simultaneously requires precise metadata engineering and source attribution. It's not just about vector similarity; it's about tracing the answer back to its exact origin.
