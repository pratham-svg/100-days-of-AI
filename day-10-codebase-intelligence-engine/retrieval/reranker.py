from sentence_transformers import CrossEncoder
from config import RERANKER_MODEL, TOP_K_FINAL

reranker = CrossEncoder(RERANKER_MODEL)

def rerank_results(query: str, candidates: list[dict], top_k: int = TOP_K_FINAL) -> list[dict]:
    """
    Re-ranks hybrid search candidates using cross-encoder.
    
    Cross-encoder sees both query AND document together
    (unlike bi-encoder which encodes them separately).
    This gives much higher accuracy for final ranking.
    """
    if not candidates:
        return []
    
    # Prepare (query, document) pairs for cross-encoder
    pairs = [(query, c["content"]) for c in candidates]
    
    # Score all pairs
    scores = reranker.predict(pairs)
    
    # Attach scores back to candidates
    for i, candidate in enumerate(candidates):
        candidate["rerank_score"] = float(scores[i])
    
    # Sort by rerank score descending, return top_k
    reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]
