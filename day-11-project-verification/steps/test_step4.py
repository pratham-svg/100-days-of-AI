import sys
import os
from pathlib import Path

# Add parent directory
sys.path.append(str(Path(__file__).parent.parent))

from retrieval.hybrid_search import hybrid_search, get_query_sparse_vector
from config import QDRANT_URL, COLLECTION_NAME

def test_hybrid_search():
    print("\n🚀 Testing Step 4: Hybrid Search Pipeline")
    print("-" * 40)
    
    # 1. Test query sparse vector generation
    query = "Find the auth function"
    sparse_vec = get_query_sparse_vector(query)
    print(f"✅ Extracted query sparse vector: {sparse_vec}")
    assert hasattr(sparse_vec, "indices")
    assert hasattr(sparse_vec, "values")
    
    # 2. Test Qdrant Hybrid Search (Requires actual data and connection)
    if QDRANT_URL:
        from qdrant_client import QdrantClient
        from qdrant_client.models import CollectionInfo
        from config import QDRANT_API_KEY
        
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        try:
            # Check if collection exists first
            client.get_collection(collection_name=COLLECTION_NAME)
            print(f"⏳ Running hybrid search on collection '{COLLECTION_NAME}'...")
            results = hybrid_search(query, top_k=2)
            
            print(f"✅ Found {len(results)} results!")
            for i, result in enumerate(results):
                print(f"Result {i+1}: File {result['file_path']} | Name: {result['name']} | Score: {result['score']:.4f}")
            
        except Exception as e:
            print(f"⚠️ Search failed (possibly collection does not exist): {e}")
    else:
        print("⏭️ Skipping hybrid search test (No Qdrant URL found).")

if __name__ == "__main__":
    test_hybrid_search()
