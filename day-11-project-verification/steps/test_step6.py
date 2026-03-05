import sys
import os
from pathlib import Path

# Add parent directory
sys.path.append(str(Path(__file__).parent.parent))

from generation.answer_chain import generate_answer, format_context
from config import OPENROUTER_API_KEY

def test_llm_chain():
    print("\n🚀 Testing Step 6: LLM Answer Synthesis")
    print("-" * 40)
    
    query = "How is authentication handled?"
    
    # Dummy reranked chunks
    chunks = [
        {"content": "def authenticate(user, password):\n    return user == 'admin'", "file_path": "auth.py", "name": "authenticate", "start_line": 1, "end_line": 5, "chunk_type": "function", "rerank_score": 0.95},
        {"content": "class AuthSession:\n    def create(self): pass", "file_path": "auth.py", "name": "AuthSession", "start_line": 6, "end_line": 10, "chunk_type": "class", "rerank_score": 0.85}
    ]
    
    print("⏳ Formatting context...")
    context_str = format_context(chunks)
    print(f"✅ Formatted context length: {len(context_str)}")
    
    if OPENROUTER_API_KEY:
        try:
            print("⏳ Generating answer (API call)...")
            response = generate_answer(query, chunks)
            
            print(f"✅ Answer synthesized: {response['answer'][:100]}...")
            print(f"✅ Sources identified: {len(response['sources'])}")
            
            assert "answer" in response
            assert "sources" in response
            
        except Exception as e:
            print(f"❌ Answer generation failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⏭️ Skipping answer generation test (No API key found).")

if __name__ == "__main__":
    test_llm_chain()
