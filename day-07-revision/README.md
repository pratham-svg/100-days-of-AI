# Day 07: Revision and Summary (Days 1-6)

Welcome to Day 7! Today is dedicated to revising and consolidating everything learned so far in the **100 Days of AI** challenge. This summary serves as a quick reference guide for the foundational concepts of LangChain, Memory Systems, and Retrieval-Augmented Generation (RAG).

---

## 🚀 Day 1: Project Setup

- **Objective:** Establish the foundation for the AI development environment.
- **Key Actions:**
  - Using **`uv`** for fast and reliable Python package management.
  - Setting up the initial repository structure.
  - Basic environment variable management (`.env` files) for API keys like OpenAI.

## 🔗 Day 2: LCEL Execution Model

- **Objective:** Learn LangChain Expression Language (LCEL) to build AI pipelines declaratively.
- **Key Concepts:**
  - **The Pipe Operator (`|`)**: Used to chain prompts, models, and parsers together cleanly (`Prompt | Model | Parser`).
  - **Outputs & Parsing**: Used `JsonOutputParser` and Pydantic schemas to force LLMs to return structured JSON data.
  - **Parallel Execution**: Leveraged `RunnableParallel` (or RunnableMap) to execute multiple tasks (like summary, keywords, sentiment) simultaneously, optimizing for speed.

## 🧠 Day 3: Memory Systems

- **Objective:** Transition from stateless "one-off" interactions to stateful, context-aware AI agents.
- **Key Concepts:**
  - **Stateless vs. Stateful**: Standard LLMs have no memory. We must feed previous chat history into every new prompt.
  - **`ConversationBufferMemory`**: Stores the raw text of the entire conversation. Good for short chats but rapidly consumes token limits.
  - **`ConversationSummaryMemory`**: Uses an LLM to dynamically summarize previous turns, saving tokens for long conversations.
  - **`ConversationTokenBufferMemory`**: Keeps only the most recent messages, flushing the oldest ones based on a strict token limit to prevent exceeding context windows.

## 🏗️ Day 4: RAG Foundations

- **Objective:** Introduce Retrieval-Augmented Generation (RAG) to allow LLMs to search and answer from private data.
- **The 4 Building Blocks:**
  1. **Document Loaders**: Extract raw text from various sources (PDFs, Web, CSVs).
  2. **Text Splitters**: Break massive documents into smaller "chunks" (with overlaps to preserve context).
  3. **Embeddings**: Convert text chunks into numerical vectors. Similar meanings yield mathematically close vectors.
  4. **Vector Stores**: Specialized databases (like FAISS, ChromaDB, or Pinecone) designed to store and quickly search for vectors based on semantic similarity.

## 🔬 Day 5: RAG Deep Dive & Embeddings

- **Objective:** Dig deeper into the mechanics of data preparation and similarity metrics.
- **Key Concepts:**
  - **Chunking Strategies**: Explored Fixed-Size, Recursive, Semantic, and Document-Aware chunking methods. Overlaps prevent splitting ideas in half.
  - **Text-to-Numbers**: The journey from Tokenization → IDs → Dense Vectors → Attention Models → Vector Pooling.
  - **How Embedding Models Learn**: They use Self-Attention for context and Contrastive Learning (pushing different concepts apart, pulling similar ones together).
  - **Cosine Similarity**: Emphasizes the _direction_ (angle) between vectors, making it superior to standard Euclidean distance for text similarity.

## 🤖 Day 6: Multi-Document Research Assistant

- **Objective:** Build a complete end-to-end RAG application.
- **Key Achievements:**
  - **Document Synthesis**: Managed multiple PDFs focused on LLM Engineering.
  - **Metadata Preservation**: Tagged chunks with their source file and topic to enable filtering.
  - **Qdrant Integration**: Swapped to Qdrant for vector storage, persisting data to disk for fast iteration.
  - **Source Attribution**: Engineered the retriever and prompt to enforce citations (document and page numbers) and strictly prevent hallucinations.
  - **FastAPI**: Wrapped the LangChain pipeline into a usable REST endpoint.

---

### 📝 Next Steps

With the core concepts of Prompts, Memory, and RAG fully established, we are now ready to tackle more complex agentic workflows, dynamic routing, and multi-agent interaction in Phase 3!
