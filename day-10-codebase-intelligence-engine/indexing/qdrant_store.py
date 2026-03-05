from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, SparseVectorParams,
    SparseIndexParams, PointStruct, SparseVector
)
from chunking.chunk_models import CodeChunk
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME, DENSE_VECTOR_SIZE

# Connect to cloud Qdrant cluster
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def create_collection():
    """
    Creates a Qdrant collection with both dense and sparse vectors.
    Deletes existing collection if it exists to ensure correct vector configuration.
    """
    existing_collections = [c.name for c in client.get_collections().collections]
    
    if COLLECTION_NAME in existing_collections:
        print(f"Collection '{COLLECTION_NAME}' already exists. Deleting to recreate with correct schema...")
        client.delete_collection(collection_name=COLLECTION_NAME)
    
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": VectorParams(size=DENSE_VECTOR_SIZE, distance=Distance.COSINE)
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))
        }
    )
    print(f"Collection '{COLLECTION_NAME}' created with dense and sparse vector support.")


def upsert_chunks(
    chunks: list[CodeChunk],
    dense_vectors: list[list[float]],
    sparse_vectors: list[dict],
):
    """
    Upserts all chunks with their dense + sparse vectors into Qdrant.
    Each point stores the chunk metadata as payload.
    """
    points = []
    for i, chunk in enumerate(chunks):
        point = PointStruct(
            id=abs(hash(chunk.chunk_id)) % (2**63),  # Qdrant needs int ID
            vector={
                "dense": dense_vectors[i],
                "sparse": SparseVector(
                    indices=sparse_vectors[i]["indices"],
                    values=sparse_vectors[i]["values"],
                )
            },
            payload={
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "file_path": chunk.file_path,
                "chunk_type": chunk.chunk_type,
                "name": chunk.name,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "language": chunk.language,
                "repo_name": chunk.repo_name,
            }
        )
        points.append(point)
    
    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(points), batch_size):
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points[i:i + batch_size]
        )
        print(f"Upserted batch {i // batch_size + 1}/{len(points) // batch_size + 1}")
    
    print(f"Total {len(points)} chunks indexed in Qdrant.")
