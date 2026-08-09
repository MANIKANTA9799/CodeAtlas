from qdrant_client import QdrantClient
from qdrant_client.http import models

def inspect_git_history():
    print("Connecting to local Qdrant database...")
    client = QdrantClient(path="./qdrant_storage")
    collection_name = "codeatlas_index"

    # Verify collection exists
    collections = client.get_collections().collections
    if not any(c.name == collection_name for c in collections):
        print("Collection does not exist. Please run ingestion first.")
        return

    # Filter to count only Git commit chunks
    count_result = client.count(
        collection_name=collection_name,
        count_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="document_type",
                    match=models.MatchValue(value="commit")
                )
            ]
        )
    )
    print(f"Total Git commit chunks in database: {count_result.count}")

    if count_result.count == 0:
        print("No Git commits found. Did the ingestion run successfully?")
        return

    # Retrieve one Git commit chunk to inspect its payload
    print("\nRetrieving a sample Git commit chunk...")
    sample, _ = client.scroll(
        collection_name=collection_name,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="document_type",
                    match=models.MatchValue(value="commit")
                )
            ]
        ),
        limit=1,
        with_payload=True,
        with_vectors=False
    )

    if sample:
        point = sample[0]
        print(f"\nID: {point.id}")
        print("Payload metadata:")
        for key, value in point.payload.items():#type:ignore 
            print(f"  {key}: {value}")

if __name__ == "__main__":
    inspect_git_history()