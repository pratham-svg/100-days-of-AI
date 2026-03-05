import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from indexing.sparse_encoder import tokenize_code, build_sparse_vectors, get_sparse_vector_for_qdrant
from indexing.embedder import get_dense_embeddings
from config import OPENROUTER_API_KEY, QDRANT_URL

def test_indexing_components():
    print("\n🚀 Testing Step 3: Embeddings + Qdrant Indexing")
    print("-" * 40)
    
    # 1. Test Sparse Encoding
    code_sample = "def calculate_sum(a, b):\n    return a + b"
    tokens = tokenize_code(code_sample)
    print(f"✅ Code sample tokenized: {tokens}")
    assert "calculate" in tokens
    assert "sum" in tokens
    
    # 2. Test Build Sparse Vectors
    corpus = [code_sample, "class Calculator:\n    pass"]
    bm25, tokenized_corpus = build_sparse_vectors(corpus)
    print("✅ BM25 index built successfully.")
    
    # 3. Test Sparse Vector for Qdrant
    vocab = ["calculate", "sum", "calculator"]
    sparse_vec = get_sparse_vector_for_qdrant(code_sample, vocab)
    print(f"✅ Sparse vector generated: {sparse_vec}")
    assert "indices" in sparse_vec
    assert "values" in sparse_vec
    
    # 4. Test Dense Embeddings (Requires API Key)
    if OPENROUTER_API_KEY:
        try:
            print("⏳ Testing Dense Embeddings (API call)...")
            dense_vecs = get_dense_embeddings(["Hello world"])
            print(f"✅ Dense embedding received. Length: {len(dense_vecs[0])}")
            assert len(dense_vecs[0]) > 0
        except Exception as e:
            print(f"⚠️ Dense embedding call failed: {e}")
    else:
        print("⏭️ Skipping Dense Embedding test (No API key found).")

    # 5. Test Qdrant Connection
    if QDRANT_URL:
        from qdrant_client import QdrantClient
        from qdrant_client.http import exceptions
        from config import QDRANT_API_KEY
        
        try:
            print("⏳ Testing Qdrant connection...")
            client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
            collections = client.get_collections()
            print(f"✅ Connected to Qdrant! Found {len(collections.collections)} collections.")
        except Exception as e:
            print(f"⚠️ Qdrant connection failed: {e}")
    else:
        print("⏭️ Skipping Qdrant connection test (No URL found).")

if __name__ == "__main__":
    test_indexing_components()
