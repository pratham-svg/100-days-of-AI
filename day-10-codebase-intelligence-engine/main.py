from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="My Codebase Intelligence Engine",
    description="Ask natural language questions about my GitHub codebase using AST-aware RAG",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
