from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from typing import List, Dict, Any

class VectorDatabaseService:
    """
    Manages local Qdrant operations: collection creation, 
    payload indexing, and batch upserts.
    """
    def __init__(self, collection_name: str = "codeatlas_index", storage_path: str = "./qdrant_storage"):
        # Runs Qdrant locally on disk - no Docker required for development
        self.client = QdrantClient(path=storage_path)
        self.collection_name = collection_name

    def initialize_collection(self, vector_size: int = 768):
        """
        Creates the collection if it doesn't exist.
        Default vector size 768 matches `nomic-embed-text`.
        """
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )

    def upsert_chunks_batch(self, points_data: List[Dict[str, Any]], batch_size: int = 200):
        """
        Inserts points into Qdrant in batches to optimize WAL and network calls.
        `points_data` should contain: {'id': int/str, 'vector': [...], 'payload': {...}}
        """
        points = [
            PointStruct(
                id=item["id"],
                vector=item["vector"],
                payload=item["payload"]
            )
            for item in points_data
        ]

        # Chunk points list into batches of 200
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )