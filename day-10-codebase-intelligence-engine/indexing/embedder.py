from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, EMBEDDING_MODEL

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
)

def get_dense_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generates dense embeddings for a list of texts.
    Batches in groups of 100 to respect API limits.
    """
    all_embeddings = []
    batch_size = 100
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
        print(f"Embedded batch {i // batch_size + 1}")
    
    return all_embeddings
