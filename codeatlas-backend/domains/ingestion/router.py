from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import time
from domains.git.pipeline import GitIngestionPipeline
from .pipeline import IngestionPipeline

router = APIRouter(prefix="/api/v1/ingest", tags=["Ingestion"])

class IngestRequest(BaseModel):
    repo_path: str
    project_name: str  # <-- NEW: Dynamic namespace

class IngestResponse(BaseModel):
    status: str
    message: str
    elapsed_time_seconds: float

@router.post("/", response_model=IngestResponse)
def ingest_repository(request: IngestRequest):
    """
    Triggers the ingestion pipeline for a local repository.
    Creates an isolated Qdrant collection for the project.
    """
    repo_path = Path(request.repo_path).resolve()
    
    if not repo_path.exists() or not repo_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Invalid repository path: {repo_path}")
        
    try:
        start_time = time.time()
        
        # Pass the project name down to isolate the vectors
        pipeline = IngestionPipeline(repo_path=str(repo_path), project_name=request.project_name)
        pipeline.run()
        
        elapsed = round(time.time() - start_time, 2)
        
        return IngestResponse(
            status="success",
            message=f"Successfully ingested repository into collection '{request.project_name}'",
            elapsed_time_seconds=elapsed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.post("/git", response_model=IngestResponse)
def ingest_git_history(request: IngestRequest):
    """
    Triggers the Git history ingestion pipeline into the project's isolated collection.
    """
    repo_path = Path(request.repo_path).resolve()
    
    if not repo_path.exists() or not repo_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid repository path")
        
    try:
        start_time = time.time()
        
        # Pass the project name down to the Git pipeline
        pipeline = GitIngestionPipeline(repo_path=str(repo_path), project_name=request.project_name)
        pipeline.run(max_commits=100)
        
        elapsed = round(time.time() - start_time, 2)
        
        return IngestResponse(
            status="success",
            message=f"Successfully ingested Git history into '{request.project_name}'",
            elapsed_time_seconds=elapsed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git ingestion failed: {str(e)}")