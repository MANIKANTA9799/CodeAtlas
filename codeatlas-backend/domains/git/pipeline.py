import uuid
from typing import List, Dict, Any

from .service import GitHistoryScanner
from .formatter import GitSemanticFormatter
from core.embedding import EmbeddingService
from core.vector_db import VectorDatabaseService

class GitIngestionPipeline:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.scanner = GitHistoryScanner(repo_path=repo_path)
        self.embedder = EmbeddingService()
        self.vector_db = VectorDatabaseService()
        
        # Ensure collection exists before inserting
        self.vector_db.initialize_collection()

    def _process_batch(self, batch_commits: List[Dict[str, Any]]):
        """Embeds and uploads a batch of file-level commit changes to Qdrant."""
        if not batch_commits:
            return

        # 1. Format the commits into semantic text for the embedding model
        texts_to_embed = []
        for commit in batch_commits:
            semantic_doc = GitSemanticFormatter.format_commit_for_embedding(commit)
            texts_to_embed.append(semantic_doc)

        # 2. Generate vector embeddings
        embeddings = self.embedder.get_embeddings_batch(texts_to_embed)

        # 3. Prepare payload for Qdrant (combining vectors with metadata)
        points_data = []
        for i, commit in enumerate(batch_commits):
            points_data.append({
                "id": str(uuid.uuid4()),
                "vector": embeddings[i],
                "payload": {
                    "document_type": "commit",
                    "commit_hash": commit.get("commit_hash"),
                    "author": commit.get("author"),
                    "timestamp": commit.get("timestamp"),
                    "date_iso": commit.get("date_iso"),
                    "file_path": commit.get("file_path"),
                    "message": commit.get("message")
                    # We do not store the massive raw diff in the payload 
                    # to save disk space, as the LLM primarily needs the message and file path
                }
            })

        # 4. Batch upsert to vector database
        self.vector_db.upsert_chunks_batch(points_data)
        print(f"Upserted batch of {len(points_data)} commit file-changes to Qdrant.")

    def run(self, max_commits: int = 100):
        """
        Executes the end-to-end Git ingestion process.
        Limited to max_commits to keep MVP testing fast.
        """
        print(f"Starting Git history ingestion for repository: {self.repo_path}")
        
        batch_commits = []
        BATCH_SIZE = 50 # Smaller batch size because diffs contain more tokens than code chunks

        for commit_data in self.scanner.scan_commits(max_commits=max_commits):
            batch_commits.append(commit_data)

            if len(batch_commits) >= BATCH_SIZE:
                self._process_batch(batch_commits)
                batch_commits.clear()

        # Process any remaining items
        if batch_commits:
            self._process_batch(batch_commits)

        print("Git history ingestion complete.")