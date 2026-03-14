from vectorstore.qdrant import vector_store
from qdrant_client.http import models

def test_search():
    # Ensure collection exists
    vector_store.create_collection()
    
    # Store a dummy resume if needed (optional since we're testing the method signature)
    # vector_store.store_resume("Python developer with 5 years experience in FastAPI.", {"name": "Test User"})
    
    try:
        results = vector_store.search_similar("Python developer", limit=1)
        print("Search successful!")
        print(f"Results: {results}")
    except Exception as e:
        print(f"Search failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
