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
    if not texts:
        return []

    all_embeddings = []
    batch_size = 100
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        # All strings must be non-empty or standard OpenAI API might return fewer embeddings
        if any(not t.strip() for t in batch):
            # This should have been caught in routes.py, but let's be safe
            batch = [t if t.strip() else " (empty chunk) " for t in batch]
            
        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=batch
            )
            
            if not response.data:
                raise Exception(f"No embedding data received for model {EMBEDDING_MODEL}. Response: {response}")
                
            # Sort by index to ensure order if necessary (OpenRouter usually preserves order)
            # data objects have an 'index' field.
            sorted_data = sorted(response.data, key=lambda x: x.index)
            batch_embeddings = [item.embedding for item in sorted_data]
            
            if len(batch_embeddings) != len(batch):
                raise Exception(f"Mismatch in embeddings: Expected {len(batch)}, got {len(batch_embeddings)}")

            all_embeddings.extend(batch_embeddings)
            print(f"Embedded batch {i // batch_size + 1}")
        except Exception as e:
            print(f"Error calling embedding API: {e}")
            raise e
    
    return all_embeddings
