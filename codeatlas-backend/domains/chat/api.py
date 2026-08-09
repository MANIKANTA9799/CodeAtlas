from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from langchain_ollama import ChatOllama
from .graph import build_codeatlas_graph

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

# Initialize the LLM client pointing to local Ollama
# We use temperature=0 to ensure technical accuracy and minimize hallucinations
# Initialize the LLM client pointing to local Ollama
llm_client = ChatOllama(
    model="llama3.1", 
    temperature=0.0,
    base_url="http://localhost:11434"
)

# Compile the LangGraph application
codeatlas_agent = build_codeatlas_graph(llm_client)

@router.post("/", response_model=ChatResponse)
def query_agent(request: ChatRequest):
    """
    Passes the user query into the stateful LangGraph agent, 
    executes the routing, retrieval, and synthesis workflow.
    """
    try:
        # Initialize the graph state
        initial_state = {
            "query": request.query,
            "messages": [],
            "route": "",
            "retrieved_context": "",
            "sources": []
        }
        
        # Invoke the LangGraph workflow
        final_state = codeatlas_agent.invoke(initial_state)#type:ignore
        
        # The SynthesisNode appended the final AIMessage to the messages list
        final_answer = final_state["messages"][-1].content
        
        return ChatResponse(
            answer=final_answer,
            sources=final_state.get("sources", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")