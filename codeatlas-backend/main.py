from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from domains.chat.api import router as chat_router
from domains.ingestion.router import router as ingestion_router
app = FastAPI(title="CodeAtlas API")
# Configure CORS to allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # The Next.js development server
    allow_credentials=True,
    allow_methods=["*"], # Explicitly allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)
app.include_router(ingestion_router)
app.include_router(chat_router)
@app.get("/health")
def health_check():
    return {"status": "CodeAtlas is online."}