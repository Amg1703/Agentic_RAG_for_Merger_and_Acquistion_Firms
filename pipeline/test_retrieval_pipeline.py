from vector_db_storage_and_retrieval_pipeline import QdrantStorage

db = QdrantStorage()

queries = [
    "What problem does uber solve?",
    "What is uber's business model?",
    "How does uber make money?",
    "What market validation is shown?",
    "What revenue is mentioned?"
]

for query in queries:

    print(f"\n{'='*50}")
    print("QUERY:", query)
    print(f"{'='*50}")

    result = db.search_based_on_user_query(query)
    print(result)