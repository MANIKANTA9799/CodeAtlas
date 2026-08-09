from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import time
from domains.git.pipeline import GitIngestionPipeline
from .pipeline import IngestionPipeline

router = APIRouter(prefix="/api/v1/ingest", tags=["Ingestion"])

class IngestRequest(BaseModel):
    repo_path: str

class IngestResponse(BaseModel):
    status: str
    message: str
    elapsed_time_seconds: float

@router.post("/", response_model=IngestResponse)
def ingest_repository(request: IngestRequest):
    """
    Triggers the ingestion pipeline for a local repository.
    Note: For V1, this is a synchronous blocking call as decided in Phase 0.
    """
    repo_path = Path(request.repo_path).resolve()
    
    if not repo_path.exists() or not repo_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Invalid repository path: {repo_path}")
        
    try:
        start_time = time.time()
        
        # Initialize and run our orchestrated pipeline
        pipeline = IngestionPipeline(repo_path=str(repo_path))
        pipeline.run()
        
        elapsed = round(time.time() - start_time, 2)
        
        return IngestResponse(
            status="success",
            message=f"Successfully ingested repository at {repo_path}",
            elapsed_time_seconds=elapsed
        )
    except Exception as e:
        # In a real prod environment, we would log the full stack trace here
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.post("/git", response_model=IngestResponse)
def ingest_git_history(request: IngestRequest):
    """
    Triggers the Git history ingestion pipeline.
    """
    repo_path = Path(request.repo_path).resolve()
    
    if not repo_path.exists() or not repo_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid repository path")
        
    try:
        start_time = time.time()
        
        pipeline = GitIngestionPipeline(repo_path=str(repo_path))
        # Defaulting to 100 commits for MVP speed
        pipeline.run(max_commits=100)
        
        elapsed = round(time.time() - start_time, 2)
        
        return IngestResponse(
            status="success",
            message=f"Successfully ingested Git history for {repo_path}",
            elapsed_time_seconds=elapsed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git ingestion failed: {str(e)}")    