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
