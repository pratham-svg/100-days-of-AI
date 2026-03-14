# 🤖 Resume Screener Agent — Day 19

A **multi-agent resume screening system** built with LangGraph, FastAPI, and Qdrant.  
Automatically screens resumes against a job description, scores them across 5 dimensions, generates recruiter-grade feedback, and stores every evaluated resume in a vector database for future similarity search.

---

## ⚙️ Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) installed (`pip install uv`)
- An [OpenRouter](https://openrouter.ai/) account + API key
- A [Qdrant Cloud](https://cloud.qdrant.io/) cluster + API key

---

## 🚀 Setup

### 1. Clone / Navigate to the project

```bash
cd day-19-resume-screener-agent
```

### 2. Install dependencies

```bash
uv sync
```

This installs all packages from `pyproject.toml` into a local `.venv` automatically.

### 3. Configure environment variables

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

Open `.env` and set:

```env
# OpenRouter
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=openai/gpt-4o-mini          # or any model on OpenRouter

# Qdrant Cloud
QDRANT_URL=https://your-cluster.eu-west-1.aws.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION=resumes

# Embeddings (via OpenRouter)
EMBEDDING_MODEL=text-embedding-ada-002
```

### 4. Initialize Qdrant collection

Before the first run, create the vector collection in Qdrant:

```bash
uv run python -c "from vectorstore.qdrant import vector_store; vector_store.create_collection()"
```

You should see:
```
Collection 'resumes' created.
```

### 5. Start the API server

```bash
uv run uvicorn api.main:app --reload
```

The server starts at **http://127.0.0.1:8000**

---

## 🧪 Usage

### Screen a Resume

Send a POST request with a job description (text) and a resume (PDF file):

**Using `curl`:**
```bash
curl -X POST http://localhost:8000/screen \
  -F "jd=We are looking for a Senior Python developer with FastAPI and RAG experience." \
  -F "resume=@/path/to/resume.pdf"
```

**Using the interactive docs:**  
Open http://localhost:8000/docs in your browser → click `POST /screen` → try it out.

**Response:**
```json
{
  "is_relevant": true,
  "scores": {
    "skills_match": 90,
    "experience_level": 80,
    "education": 75,
    "project_relevance": 95,
    "overall_fit": 88
  },
  "feedback": "Strong candidate with excellent RAG pipeline experience...",
  "similar_candidates": []
}
```

---

### Find Similar Resumes

After screening a few resumes, find past candidates similar to a new JD:

```bash
curl "http://localhost:8000/similar?jd=Python+developer+with+LangGraph+experience"
```

---

### Health Check

```bash
curl http://localhost:8000/health
```

---

## 📁 Project Structure

```
day-19-resume-screener-agent/
│
├── config/
│   └── settings.py          # Pydantic settings — loads .env
│
├── agents/
│   ├── state.py             # Shared AgentState (TypedDict)
│   ├── llm.py               # LLM factory (OpenRouter via ChatOpenAI)
│   ├── screener.py          # Agent 1: Is resume relevant? (yes/no)
│   ├── scorer.py            # Agent 2: 5-dimensional scoring
│   └── feedback.py          # Agent 3: Recruiter-grade feedback
│
├── graph/
│   └── pipeline.py          # LangGraph pipeline — nodes + conditional edges
│
├── vectorstore/
│   └── qdrant.py            # Qdrant: store + semantic search for resumes
│
├── utils/
│   └── pdf_parser.py        # PDF → raw text using pypdf
│
├── api/
│   ├── main.py              # FastAPI app
│   └── routes/
│       ├── screen.py        # POST /screen
│       └── search.py        # GET /similar
│
├── .env                     # Your secrets (never commit)
├── .env.example             # Safe template
├── pyproject.toml           # Dependencies
└── DAY_19_RESUME_SCREENER.md  # Full project documentation & journal
```

---

## 🗺️ How the Pipeline Works

```
POST /screen (JD + PDF)
        │
   [Parse PDF]
        │
   [Screener Agent] ── NOT relevant ──► [Feedback Agent] ──► Return
        │ relevant
   [Scorer Agent]
        │
   [Feedback Agent]
        │
   [Store in Qdrant] → [Search Similar]
        │
     Return JSON report
```

---

## 🛑 Troubleshooting

| Error | Fix |
|---|---|
| `401 User not found` | Your OpenRouter API key is invalid or expired. Regenerate at openrouter.ai |
| `AttributeError: 'QdrantClient' has no attribute 'search'` | Use `query_points()` — `search()` was removed in qdrant-client v1.16+ |
| `Collection not found` | Run the collection init step (Step 4 above) |
| `Could not extract text from PDF` | Make sure the PDF has selectable text, not a scanned image |
| `ModuleNotFoundError` | Run `uv sync` to install all dependencies |

---

*Day 19-20 of 100 Days of AI*