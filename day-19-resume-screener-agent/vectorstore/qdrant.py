from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_openai import OpenAIEmbeddings
from config.settings import settings
import uuid

class ResumeVectorStore:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENROUTER_API_KEY, # Using OpenRouter for embeddings too
            openai_api_base=settings.OPENROUTER_BASE_URL
        )
        self.collection_name = settings.QDRANT_COLLECTION

    def create_collection(self):
        """Create the collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536, # Size for text-embedding-ada-002
                    distance=models.Distance.COSINE
                )
            )
            print(f"Collection '{self.collection_name}' created.")

    def store_resume(self, resume_text: str, metadata: dict):
        """Embed and store a resume."""
        vector = self.embeddings.embed_query(resume_text)
        point_id = str(uuid.uuid4())
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "text": resume_text,
                        **metadata
                    }
                )
            ]
        )
        print(f"Resume stored in Qdrant with ID {point_id}")

    def search_similar(self, query_text: str, limit: int = 3):
        """Search for similar resumes."""
        vector = self.embeddings.embed_query(query_text)
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=limit
        ).points
        
        return [
            {
                "score": hit.score,
                "text": hit.payload.get("text"),
                "metadata": {k: v for k, v in hit.payload.items() if k != "text"}
            }
            for hit in results
        ]

vector_store = ResumeVectorStore()
