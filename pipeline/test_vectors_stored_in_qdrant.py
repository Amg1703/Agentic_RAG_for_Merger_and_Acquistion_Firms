# verify_qdrant.py

from qdrant_client import QdrantClient

client = QdrantClient("http://localhost:6333")

collection = client.get_collection("docs")

print(collection)