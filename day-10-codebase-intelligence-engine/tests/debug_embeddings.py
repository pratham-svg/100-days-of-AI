import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from indexing.embedder import get_dense_embeddings

def test_embeddings():
    print("Testing dense embeddings through OpenRouter...")
    try:
        texts = ["Hello, this is a test of the embedding API."]
        embeddings = get_dense_embeddings(texts)
        print(f"Success! Received {len(embeddings)} embeddings.")
        if embeddings:
            print(f"First embedding length: {len(embeddings[0])}")
    except Exception as e:
        print(f"Caught error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_embeddings()
