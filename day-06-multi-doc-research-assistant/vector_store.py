import warnings
warnings.filterwarnings('ignore')  # suppress some langchain warnings for clean output

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from chunking import chunk_documents
from document_loader import load_documents_with_metadata
import config

def initialize_qdrant_client():
    """Initializes and returns the Qdrant client."""
    url = config.get_qdrant_url()
    api_key = config.get_qdrant_api_key()
    
    print(f"Connecting to Qdrant at: {url}")
    client = QdrantClient(url=url, api_key=api_key)
    return client

def setup_vector_store(collection_name="research_assistant_docs"):
    """
    Loads documents, chunks them, generates embeddings, 
    and stores them in Qdrant.
    """
    # 1. Load and Chunk
    docs = load_documents_with_metadata()
    if not docs:
        print("No documents to process. Exiting.")
        return None
        
    chunks = chunk_documents(docs)
    
    # 2. Get OpenAI Embeddings
    # This requires OPENAI_API_KEY in your .env
    print("\nInitializing OpenAI Embeddings...")
    embeddings = OpenAIEmbeddings()
    
    # 3. Initialize Qdrant Client
    client = initialize_qdrant_client()
    
    # 4. Check if collection exists; if not, create it
    if not client.collection_exists(collection_name):
        print(f"Creating new Qdrant collection: '{collection_name}'...")
        # OpenAI Embeddings text-embedding-ada-002 outputs 1536 dimensions
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
    else:
        print(f"Collection '{collection_name}' already exists. We will append to it.")

    # 5. Load chunks into Qdrant Vector Store
    print(f"Loading {len(chunks)} chunks into Qdrant...")
    
    qdrant = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    
    # Add documents to Qdrant
    qdrant.add_documents(chunks)
    
    print("\nSuccessfully added documents to Qdrant!")
    return qdrant

def get_vector_store(collection_name="research_assistant_docs"):
    """
    Returns a configured QdrantVectorStore object for querying, 
    assuming the collection already exists and has data.
    """
    client = initialize_qdrant_client()
    embeddings = OpenAIEmbeddings()
    
    qdrant = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    return qdrant

if __name__ == "__main__":
    print("--- Step 4: Embeddings + Vector Store (Qdrant) ---")
    try:
        store = setup_vector_store()
    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        print("Please check your .env file!")
