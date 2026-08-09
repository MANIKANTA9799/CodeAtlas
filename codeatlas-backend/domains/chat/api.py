from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import json

from langchain_ollama import ChatOllama
from .graph import build_codeatlas_graph

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

# Initialize the LLM client pointing to local Ollama
# Added streaming=True to allow token-by-token generation
llm_client = ChatOllama(
    model="llama3.1", 
    temperature=0.0,
    base_url="http://localhost:11434",
)

# Compile the LangGraph application
codeatlas_agent = build_codeatlas_graph(llm_client)

@router.post("/", response_model=ChatResponse)
def query_agent(request: ChatRequest):
    """
    Standard synchronous endpoint.
    Passes the user query into the stateful LangGraph agent, 
    executes the routing, retrieval, and synthesis workflow.
    """
    try:
        initial_state = {
            "query": request.query,
            "messages": [],
            "route": "",
            "retrieved_context": "",
            "sources": []
        }
        
        final_state = codeatlas_agent.invoke(initial_state) #type:ignore
        final_answer = final_state["messages"][-1].content
        
        return ChatResponse(
            answer=final_answer,
            sources=final_state.get("sources", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@router.post("/stream")
async def stream_agent(request: ChatRequest):
    """
    Streaming endpoint.
    Yields Server-Sent Events (SSE) so the UI can render 
    sources and text tokens in real-time.
    """
    async def generate():
        initial_state = {
            "query": request.query,
            "messages": [],
            "route": "",
            "retrieved_context": "",
            "sources": []
        }
        
        sources_sent = False
        
        try:
            # astream_events listens to everything happening inside the graph pipeline
            async for event in codeatlas_agent.astream_events(initial_state, version="v2"):# type: ignore
                
                # 1. Intercept state updates to grab and send the retrieved sources first
                if event["event"] == "on_chain_end":
                    output = event.get("data", {}).get("output")
                    if isinstance(output, dict) and "sources" in output and not sources_sent:
                        if output["sources"]:
                            # Send the sources array to the right lane of the UI
                            yield f"data: {json.dumps({'type': 'sources', 'sources': output['sources']})}\n\n"
                            sources_sent = True

                # 2. Intercept the LLM token generation and stream it to the chat lane
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
                        
            # Signal the frontend that the stream is completely finished
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            # If an error happens mid-stream, send it as text so it renders in the chat
            error_msg = f"\n\n**Error during streaming:** {str(e)}"
            yield f"data: {json.dumps({'type': 'token', 'content': error_msg})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")