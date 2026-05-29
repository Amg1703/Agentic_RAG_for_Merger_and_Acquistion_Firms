from ingestion_and_embedding_pipeline import (
    pdf_loading_and_chunking_pipeline,
    embedding_pipeline
)

pdf_path = r"C:\Users\Arjun VJ\Downloads\uber-pitch-deck.pdf"

print("Loading PDF...")

chunks = pdf_loading_and_chunking_pipeline(pdf_path)

print(f"Total chunks: {len(chunks)}")

embedded_data = embedding_pipeline(chunks)

print(f"Vectors generated: {len(embedded_data['vectors'])}")

print("Success!")