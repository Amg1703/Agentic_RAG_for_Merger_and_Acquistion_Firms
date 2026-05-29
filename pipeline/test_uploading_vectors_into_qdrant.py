# upload_to_qdrant.py

import uuid

from ingestion_and_embedding_pipeline import (
    pdf_loading_and_chunking_pipeline,
    embedding_pipeline
)

from vector_db_storage_and_retrieval_pipeline import (
    QdrantStorage
)

pdf_path = r"C:\Users\Arjun VJ\Downloads\Airbnb_pitch_deck.pdf"

chunks = pdf_loading_and_chunking_pipeline(pdf_path)

embedded_data = embedding_pipeline(chunks)

vectors = embedded_data["vectors"]
payloads = embedded_data["payloads"]

ids = [str(uuid.uuid4()) for _ in vectors]

db = QdrantStorage()

db.update_and_insert_new_vectors(
    incoming_ids=ids,
    incoming_vectors=vectors,
    incoming_payloads=payloads
)

print(f"Inserted {len(vectors)} vectors into Qdrant")