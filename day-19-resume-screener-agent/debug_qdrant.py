from qdrant_client import QdrantClient
client = QdrantClient(":memory:")
print(f"Methods: {[m for m in dir(client) if not m.startswith('_')]}")
