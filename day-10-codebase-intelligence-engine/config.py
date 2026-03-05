# config.py
import os
from dotenv import load_dotenv

# Load from the root .env file if it exists, otherwise check parent
load_dotenv() 
load_dotenv("../.env")

OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY") 
OPENROUTER_BASE_URL = os.getenv("OPENAI_BASE_URL")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "codebase_intel")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "google/gemini-3.1-flash-lite-preview")

DENSE_VECTOR_SIZE = 1536       # text-embedding-3-small output dim
TOP_K_RETRIEVAL = 20           # candidates before reranking
TOP_K_FINAL = 5                # chunks passed to LLM after reranking
SUPPORTED_EXTENSIONS = [".py", ".js", ".ts", ".java", ".go", ".rs" , ".html" , ".md" , ".css"]
