from fastapi import APIRouter, UploadFile, File, Form
from utils.pdf_parser import parse_pdf
from graph.pipeline import pipeline
from vectorstore.qdrant import vector_store
import json

router = APIRouter()

@router.post("/screen")
async def screen_resume(
    jd: str = Form(...),
    resume: UploadFile = File(...)
):
    # 1. Parse PDF
    resume_bytes = await resume.read()
    resume_text = parse_pdf(resume_bytes)
    
    if not resume_text:
        return {"error": "Could not extract text from PDF"}
    
    # 2. Run Pipeline
    initial_state = {
        "jd": jd,
        "resume_text": resume_text,
        "is_relevant": False,
        "scores": {},
        "feedback": "",
        "similar_candidates": [],
        "final_report": {}
    }
    
    result = pipeline.invoke(initial_state)
    
    # 3. If relevant, store in Qdrant and find similar
    if result.get("is_relevant"):
        # Store
        vector_store.store_resume(
            resume_text, 
            {
                "filename": resume.filename,
                "scores": result.get("scores")
            }
        )
        
        # Search similar (optional: based on JD)
        similar = vector_store.search_similar(jd)
        result["similar_candidates"] = similar

    return result["final_report"] if "final_report" in result else result
