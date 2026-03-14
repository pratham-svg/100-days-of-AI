# 📄 Day 19 — Resume Screener Agent
### 100 Days of AI | Pratham

---

## 💡 What I Built

On Day 19, I built a **multi-agent Resume Screener** powered by LangGraph, FastAPI, and Qdrant.

The idea was simple — instead of writing a single big LLM prompt to evaluate a resume, I split the job across 3 specialized AI agents working in a pipeline:

1. **Screener Agent** — Decides if the resume is even relevant to the JD
2. **Scorer Agent** — Gives a 5-dimensional score (skills, experience, education, projects, overall fit)
3. **Feedback Agent** — Writes human-readable, specific feedback for the hiring team

All orchestrated using **LangGraph**, exposed via **FastAPI**, and with every evaluated resume stored in **Qdrant** vector database for future similarity searches.

---

## 🧠 Why Multi-Agent?

Instead of one mega-prompt, each agent has a single clear job:

| Agent | Responsibility | Output |
|---|---|---|
| Screener | Is the resume relevant? | `is_relevant: bool` |
| Scorer | Score across 5 dimensions | `scores: Dict[str, int]` |
| Feedback | Write recruiter-facing feedback | `feedback: str` |

This makes each agent's output **focused, predictable, and easier to debug**. If scoring breaks, I don't need to touch the screener or feedback logic.

---

## 🗂️ Project Structure

```
day-19-resume-screener-agent/
│
├── config/
│   └── settings.py          # Pydantic settings — loads all env vars
│
├── agents/
│   ├── state.py             # AgentState TypedDict — shared graph state
│   ├── screener.py          # Agent 1: Relevancy check (yes/no)
│   ├── scorer.py            # Agent 2: 5D scoring (0–100 per dimension)
│   └── feedback.py          # Agent 3: Human-readable feedback
│
├── graph/
│   └── pipeline.py          # LangGraph wiring — nodes, edges, conditional routing
│
├── vectorstore/
│   └── qdrant.py            # Qdrant cloud: store + search resumes
│
├── utils/
│   └── pdf_parser.py        # PDF → raw text using pypdf
│
├── api/
│   ├── routes/
│   │   ├── screen.py        # POST /screen — main screening endpoint
│   │   └── search.py        # GET /similar — semantic resume search
│   └── main.py              # FastAPI app entry point
│
├── .env                     # Secrets (never commit this)
├── .env.example             # Safe template to share
├── pyproject.toml           # uv project dependencies
└── README.md                # Setup guide
```

---

## 🔁 The LangGraph Pipeline

```
           ┌─────────────┐
           │   /screen   │  ← POST request (JD + Resume PDF)
           └──────┬──────┘
                  │
           ┌──────▼──────┐
           │   Screener  │  ← Is resume relevant to JD?
           └──────┬──────┘
                  │
        ┌─────────┴──────────┐
      YES                    NO
        │                    │
  ┌─────▼──────┐      ┌──────▼──────┐
  │   Scorer   │      │  Feedback   │ ← "Not a match" response
  └─────┬──────┘      └─────────────┘
        │
  ┌─────▼──────┐
  │  Feedback  │  ← Detailed recruiter feedback
  └─────┬──────┘
        │
  Store in Qdrant + Search Similar → Return Report
```

---

## 📊 AgentState — The Shared State

```python
class AgentState(TypedDict):
    jd: str                             # Job description text
    resume_text: str                    # Parsed PDF text
    is_relevant: bool                   # Set by Screener
    scores: Dict[str, int]              # Set by Scorer
    feedback: str                       # Set by Feedback agent
    similar_candidates: List[Dict]      # From Qdrant vector search
    final_report: Dict[str, Any]        # Final API response
```

Every agent reads from and writes back to this shared `AgentState`. LangGraph handles state passing between nodes automatically.

---

## 🌐 API Endpoints

### `POST /screen`
The main endpoint. Upload a Job Description (text) + Resume (PDF).

**Request:**
```
Content-Type: multipart/form-data
  jd     → string  (job description)
  resume → file    (PDF file)
```

**Response:**
```json
{
  "is_relevant": true,
  "scores": {
    "skills_match": 95,
    "experience_level": 85,
    "education": 70,
    "project_relevance": 95,
    "overall_fit": 90
  },
  "feedback": "Strong candidate with excellent RAG pipeline experience...",
  "similar_candidates": [ ... ]
}
```

---

### `GET /similar`
Find previously screened resumes similar to a JD using vector search.

**Request:**
```
GET /similar?jd=Senior Python Developer with FastAPI experience
```

**Response:**
```json
{
  "results": [
    {
      "score": 0.91,
      "text": "...",
      "metadata": { "filename": "resume.pdf", "scores": { ... } }
    }
  ]
}
```

---

### `GET /health`
Check if the API and Qdrant connection are alive.

**Response:**
```json
{ "status": "ok", "qdrant": "connected" }
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | LangGraph |
| Language Model | OpenRouter (GPT-4o / Gemini) |
| Embeddings | OpenAI `text-embedding-ada-002` via OpenRouter |
| Vector Database | Qdrant Cloud |
| API Framework | FastAPI + Uvicorn |
| PDF Parsing | pypdf |
| Config Management | pydantic-settings |
| Package Manager | uv |

---

## 💭 What I Learned

- **LangGraph's `conditional_edges`** are the cleanest way to implement branching agent logic — no if/else spaghetti
- **Splitting one big prompt into 3 agents** makes each agent's output more precise and easier to debug
- **Qdrant's `query_points`** (the new API, replacing the deprecated `search`) lets you do semantic similarity search on stored resumes in milliseconds
- **FastAPI + `multipart/form-data`** is the right approach for handling file + text uploads in a single request
- **pydantic-settings** + `.env` is the cleanest pattern for managing secrets across environments

---

## 📝 Sample Output

```
Screener: Relevant=True, Reason=Strong match on Python, FastAPI, and RAG systems
Scorer: {'skills_match': 95, 'experience_level': 85, 'education': 70, 'project_relevance': 95, 'overall_fit': 90}
Feedback: Pratham is an exceptionally strong candidate whose extensive project portfolio in RAG 
pipelines, AI agent orchestration, and FastAPI development aligns perfectly with the core 
technical requirements...
Resume stored in Qdrant with ID 6419b600-3982-427b-a4f4-e1b156b23a1b
```

---

*Day 19 of 100 Days of AI — Pratham*
