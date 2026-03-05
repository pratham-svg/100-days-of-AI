from fastapi import APIRouter, HTTPException
from api.schemas import IndexRequest, QueryRequest, QueryResponse
from ingestion.github_loader import clone_repo, walk_code_files, get_repo_name
from chunking.ast_chunker import chunk_repository
from indexing.embedder import get_dense_embeddings
from indexing.sparse_encoder import get_sparse_vector_for_qdrant, tokenize_code
from indexing.qdrant_store import create_collection, upsert_chunks
from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import rerank_results
from generation.answer_chain import generate_answer

router = APIRouter()

# In-memory vocab store (for sparse vectors)
_vocab: list[str] = []


@router.post("/index", summary="Clone and index a GitHub repository")
async def index_repository(request: IndexRequest):
    """
    Full pipeline: Clone → Walk → Chunk → Embed → Index
    This will take 2–10 minutes depending on repo size.
    """
    try:
        repo_name = get_repo_name(request.repo_url)
        repo_path = clone_repo(request.repo_url)
        file_paths = walk_code_files(repo_path)
        
        if not file_paths:
            raise HTTPException(status_code=400, detail="No supported code files found in repo.")
        
        chunks = chunk_repository(file_paths, repo_name)
        
        # Filter out empty or whitespace-only chunks to avoid API errors
        chunks = [c for c in chunks if c.content.strip()]
        
        if not chunks:
            return {
                "status": "success",
                "repo": repo_name,
                "files_indexed": len(file_paths),
                "chunks_indexed": 0,
                "warning": "No non-empty chunks extracted from code files."
            }

        # Build vocab from all chunks for sparse encoding
        all_texts = [c.content for c in chunks]
        global _vocab
        all_tokens = []
        for text in all_texts:
            all_tokens.extend(tokenize_code(text))
        _vocab = list(set(all_tokens))
        
        # Generate embeddings
        dense_vectors = get_dense_embeddings(all_texts)
        sparse_vectors = [get_sparse_vector_for_qdrant(t, _vocab) for t in all_texts]
        
        # Create collection + upsert
        create_collection()
        upsert_chunks(chunks, dense_vectors, sparse_vectors)
        
        return {
            "status": "success",
            "repo": repo_name,
            "files_indexed": len(file_paths),
            "chunks_indexed": len(chunks),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse, summary="Ask a question about the codebase")
async def query_codebase(request: QueryRequest):
    """
    Query pipeline: HybridSearch → Rerank → LLM → Answer
    """
    try:
        # Retrieve top candidates
        candidates = hybrid_search(request.question)
        
        # Re-rank and cut to top_k
        reranked = rerank_results(request.question, candidates, top_k=request.top_k)
        
        # Generate answer with source attribution
        result = generate_answer(request.question, reranked)
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            total_chunks_searched=len(candidates),
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Health check")
async def health():
    return {"status": "ok"}
