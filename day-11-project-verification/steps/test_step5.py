import sys
import os
from pathlib import Path

# Add parent directory
sys.path.append(str(Path(__file__).parent.parent))

from retrieval.reranker import rerank_results

def test_reranking():
    print("\n🚀 Testing Step 5: Cross-Encoder Re-ranking")
    print("-" * 40)
    
    query = "How do I handle authentication?"
    
    # Dummy hybrid search results
    candidates = [
        {"content": "def login():\n    return 'login successful'", "file_path": "auth.py", "name": "login", "score": 0.8},
        {"content": "def calculate_sum(a, b):\n    return a + b", "file_path": "utils.py", "name": "calculate_sum", "score": 0.5},
        {"content": "class AuthManager:\n    def handle_auth(self): pass", "file_path": "auth.py", "name": "AuthManager", "score": 0.9}
    ]
    
    print(f"⏳ Running re-ranking (query: '{query}')...")
    
    try:
        reranked = rerank_results(query, candidates, top_k=2)
        
        print(f"✅ Re-ranked {len(reranked)} candidates.")
        for i, result in enumerate(reranked):
            print(f"Rank {i+1}: Name: {result['name']} | Rerank Score: {result['rerank_score']:.4f}")
        
        # We expect auth-related chunks to be at the top
        top_result_name = reranked[0]["name"]
        print(f"🥇 Top result: {top_result_name}")
        
    except Exception as e:
        print(f"❌ Error during re-ranking: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reranking()
