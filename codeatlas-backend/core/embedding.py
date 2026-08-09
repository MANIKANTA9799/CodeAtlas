import requests
import time
from typing import List

class EmbeddingService:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "nomic-embed-text"):
        self.ollama_url = ollama_url.rstrip('/')
        self.model = model

    def get_embedding(self, text: str, max_retries: int = 3) -> List[float]:#type:ignore
        """Fetches a single embedding vector with robust retry logic."""
        url = f"{self.ollama_url}/api/embeddings"
        payload = {
            "model": self.model,
            "prompt": text
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                return response.json()["embedding"]
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to embed chunk after {max_retries} attempts. Skipping. Error: {e}")
                    # Return a dummy zero-vector so the pipeline survives, 
                    # assuming a 768-dimensional model like nomic-embed-text
                    return [0.0] * 768
                
                # Wait 1s, then 2s before trying again
                time.sleep(2 ** attempt)

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.get_embedding(text) for text in texts]