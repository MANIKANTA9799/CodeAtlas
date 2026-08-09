from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from core.embedding import EmbeddingService
from core.db_client import get_qdrant_client
class RetrievalNode:
    """
    Retrieves vector chunks from Qdrant based on the routing decision 
    and formats them for the synthesis prompt.
    """

    def __init__(
        self, 
        storage_path: str = "./qdrant_storage", 
        collection_name: str = "codeatlas_index",
        limit: int = 5
    ):
        self.client = get_qdrant_client()
        self.collection_name = collection_name
        self.limit = limit
        self.embedder = EmbeddingService()

    def _query_by_document_type(self, query_vector: List[float], doc_type: str) -> List[Any]:
        """Executes a filtered vector search in Qdrant using the modern API."""
        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="document_type",
                    match=models.MatchValue(value=doc_type)
                )
            ]
        )
        
        # Qdrant client query execution using the modern query_points API
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=filter_condition,
            limit=self.limit
        )
        
        # query_points returns a response object; we extract the points list
        return results.points

    def retrieve(self, query: str, route: str) -> Dict[str, Any]:
        """
        Executes vector search depending on the route and returns formatted context and sources.
        """
        if route == "general":
            return {"context": "", "sources": []}

        query_vector = self.embedder.get_embedding(query)
        points = []

        if route in ["code", "git"]:
            doc_type = "source_code" if route == "code" else "commit"
            points = self._query_by_document_type(query_vector, doc_type)
        elif route == "both":
            code_points = self._query_by_document_type(query_vector, "source_code")
            git_points = self._query_by_document_type(query_vector, "commit")
            points = code_points + git_points

        formatted_context_blocks = []
        sources = []

        for p in points:
            payload = p.payload
            doc_type = payload.get("document_type")

            if doc_type == "source_code":
                block = f"--- SOURCE CODE: {payload.get('file_path')} ---\n"
                block += f"Symbol: {payload.get('name')} (Type: {payload.get('node_type')}, Parent: {payload.get('parent_name')})\n"
                block += f"Content:\n{payload.get('code_content')}\n"
                formatted_context_blocks.append(block)
                
                sources.append({
                    "type": "code",
                    "file_path": payload.get("file_path"),
                    "symbol": payload.get("name")
                })

            elif doc_type == "commit":
                block = f"--- GIT COMMIT: {payload.get('commit_hash')[:8]} ---\n"
                block += f"Author: {payload.get('author')} | Date: {payload.get('date_iso')}\n"
                block += f"File: {payload.get('file_path')}\n"
                block += f"Message: {payload.get('message')}\n"
                formatted_context_blocks.append(block)

                sources.append({
                    "type": "commit",
                    "hash": payload.get("commit_hash"),
                    "author": payload.get("author"),
                    "file_path": payload.get("file_path")
                })

        context_string = "\n".join(formatted_context_blocks)
        return {
            "context": context_string,
            "sources": sources
        }