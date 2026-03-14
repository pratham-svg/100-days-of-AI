from fastapi import FastAPI
from api.routes import screen, search
from vectorstore.qdrant import vector_store

app = FastAPI(title="Resume Screener Agent API")

# Include routes
app.include_router(screen.router, tags=["Screening"])
app.include_router(search.router, tags=["Search"])

@app.on_event("startup")
async def startup_event():
    # Ensure Qdrant collection exists
    vector_store.create_collection()

@app.get("/health")
async def health_check():
    try:
        # Check Qdrant connection
        vector_store.client.get_collections()
        qdrant_status = "connected"
    except Exception:
        qdrant_status = "disconnected"
        
    return {
        "status": "ok",
        "qdrant": qdrant_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
