from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from retriever import query_research_assistant

app = FastAPI(
    title="Multi-Document Research Assistant",
    description="Ask questions across multiple research papers with source attribution.",
    version="1.0.0"
)

class ResearchQuery(BaseModel):
    query: str
    topic_filter: Optional[str] = None

class ResearchResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

@app.post("/research", response_model=ResearchResponse)
async def research_endpoint(request: ResearchQuery):
    try:
        # Run the LangChain retrieval pipeline
        result = query_research_assistant(query=request.query, topic_filter=request.topic_filter)
        
        # Extract the answer
        answer = result.get("answer", "No answer generated.")
        
        # Extract source attribution cleanly for the API response
        sources = []
        if "context" in result:
            for doc in result["context"]:
                sources.append({
                    "source_file": doc.metadata.get("source_file", "Unknown"),
                    "page": doc.metadata.get("page", "Unknown"),
                    # Optional: returning a snippet of what was retrieved
                    "snippet": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                })
                
        return {"answer": answer, "sources": sources}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Multi-Document Research Assistant API. Use POST /research to query."}

if __name__ == "__main__":
    print("Starting FastAPI server on http://127.0.0.1:8000")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
