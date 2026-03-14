from fastapi import APIRouter, Query
from vectorstore.qdrant import vector_store

router = APIRouter()

@router.get("/similar")
async def get_similar_candidates(jd: str = Query(...)):
    results = vector_store.search_similar(jd)
    return {"results": results}
