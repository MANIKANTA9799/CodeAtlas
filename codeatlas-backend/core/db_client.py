from qdrant_client import QdrantClient

# Global variable to hold the single connection
_qdrant_client = None

def get_qdrant_client() -> QdrantClient:
    """Returns a singleton instance of the Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(path="./qdrant_storage")
    return _qdrant_client