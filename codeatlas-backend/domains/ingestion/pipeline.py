import uuid
from pathlib import Path
from typing import List, Dict, Any

from domains.ingestion.service import RepositoryScanner
from domains.parsing.registry import LanguageRegistry
from domains.parsing.ir import PythonAdapter, LanguageAdapter
from domains.parsing.chunker import ASTChunker
from qdrant_client.models import VectorParams, Distance
from core.embedding import EmbeddingService
from core.vector_db import VectorDatabaseService

class IngestionPipeline:
    def __init__(self, repo_path: str, project_name: str):
        self.repo_path = repo_path
        self.project_name = project_name # <-- NEW
        
        # Initialize our domain services
        self.scanner = RepositoryScanner(repo_path)
        self.registry = LanguageRegistry()
        self.chunker = ASTChunker(max_tokens=500, overlap_tokens=50)
        
        # Initialize our core infrastructure services
        self.embedder = EmbeddingService()
        
        # IMPORTANT: We pass the dynamic project name to the vector database!
        self.vector_db = VectorDatabaseService(collection_name=self.project_name)
        
        # Recreate the collection to clear out old duplicates if re-ingesting
        self.vector_db.client.recreate_collection(
            collection_name=self.project_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE) 
        )
        
        self.adapters: Dict[str, LanguageAdapter] = {
            ".py": PythonAdapter(),
        }
    def _process_batch(self, batch_chunks: List[Dict[str, Any]]):
        """Embeds and uploads a batch of code chunks to Qdrant."""
        if not batch_chunks:
            return

        # 1. Extract the text we want to embed (we include breadcrumbs for better semantic context)
        texts_to_embed = []
        for chunk in batch_chunks:
            # We prepend the file and parent context so the LLM understands the embedding
            context_header = f"File: {chunk.get('file_path')}\nParent: {chunk.get('parent')}\n"
            texts_to_embed.append(context_header + chunk["code"])

        # 2. Get embeddings from local Ollama
        embeddings = self.embedder.get_embeddings_batch(texts_to_embed)

        # 3. Format the data for Qdrant
        points_data = []
        for i, chunk in enumerate(batch_chunks):
            points_data.append({
                "id": str(uuid.uuid4()),  # Qdrant accepts string UUIDs natively
                "vector": embeddings[i],
                "payload": {
                    "document_type": "source_code",
                    "file_path": chunk.get("file_path"),
                    "node_type": chunk.get("type"),
                    "name": chunk.get("name"),
                    "parent_name": chunk.get("parent"),
                    "part": chunk.get("part", 1),
                    # We store the raw code in the payload so the LLM can read it during retrieval
                    "code_content": chunk["code"] 
                }
            })

        # 4. Upsert to Qdrant
        self.vector_db.upsert_chunks_batch(points_data)
        print(f" Upserted batch of {len(points_data)} chunks to Qdrant.")

    def run(self):
        """Executes the end-to-end ingestion process."""
        print(f" Starting ingestion for repository: {self.repo_path}")
        
        batch_chunks = []
        BATCH_SIZE = 150 # Optimize for your 16GB RAM and Ollama's processing queue
        total_files_processed = 0

        for file_path in self.scanner.scan():
            extension = file_path.suffix.lower()
            
            # Skip if we don't have an adapter or parser for this language yet
            if extension not in self.adapters:
                continue
                
            parser = self.registry.get_parser(str(file_path))
            if not parser:
                continue

            # Read the raw source code
            try:
                with open(file_path, "rb") as f:
                    source_code = f.read()
            except Exception as e:
                print(f"Could not read {file_path}: {e}")
                continue
                
            # Parse into AST
            tree = parser.parse(source_code)
            
            # Extract context-aware chunks
            adapter = self.adapters[extension]
            chunks = self.chunker.extract_symbols(tree.root_node, adapter, source_code)
            
            # Enrich chunks with file path metadata
            for chunk in chunks:
                # Store relative path to keep it clean
                chunk["file_path"] = str(file_path.relative_to(self.repo_path))
                batch_chunks.append(chunk)

            total_files_processed += 1

            # If we hit our batch limit, process and clear the buffer
            if len(batch_chunks) >= BATCH_SIZE:
                self._process_batch(batch_chunks)
                batch_chunks.clear()

        # Process any remaining chunks in the final partial batch
        if batch_chunks:
            self._process_batch(batch_chunks)

        print(f"🎉 Ingestion complete! Processed {total_files_processed} files.")