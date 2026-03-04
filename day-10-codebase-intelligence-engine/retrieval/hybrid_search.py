from qdrant_client import QdrantClient
from qdrant_client.models import (
    NamedVector, NamedSparseVector, SparseVector,
    QueryRequest, Prefetch, FusionQuery, Fusion
)
from indexing.embedder import get_dense_embeddings
from indexing.sparse_encoder import tokenize_code
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME, TOP_K_RETRIEVAL

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def get_query_sparse_vector(query: str) -> SparseVector:
    """Converts query text to sparse vector using same tokenizer as indexing."""
    tokens = tokenize_code(query)
    # Build term frequency dict
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    
    # Use hash of token as index (consistent with indexing)
    indices = [abs(hash(t)) % 100000 for t in tf.keys()]
    values = [float(v) for v in tf.values()]
    return SparseVector(indices=indices, values=values)


def hybrid_search(query: str, top_k: int = TOP_K_RETRIEVAL) -> list[dict]:
    """
    Performs hybrid search using Qdrant's built-in RRF fusion.
    Returns top_k results with payload and score.
    """
    # Dense vector for semantic search
    dense_vector = get_dense_embeddings([query])[0]
    
    # Sparse vector for keyword search
    sparse_vector = get_query_sparse_vector(query)
    
    # Qdrant native hybrid search with RRF fusion
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            Prefetch(
                query=dense_vector,
                using="dense",
                limit=top_k
            ),
            Prefetch(
                query=sparse_vector,
                using="sparse",
                limit=top_k
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=top_k,
        with_payload=True,
    )
    
    return [
        {
            "content": r.payload["content"],
            "file_path": r.payload["file_path"],
            "name": r.payload["name"],
            "start_line": r.payload["start_line"],
            "end_line": r.payload["end_line"],
            "chunk_type": r.payload["chunk_type"],
            "score": r.score,
        }
        for r in results.points
    ]
