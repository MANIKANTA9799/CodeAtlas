from typing import TypedDict, Annotated, List, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    The working memory of the CodeAtlas agent. 
    This dictionary is passed through every node in the graph.
    """
    
    # The conversation history. 'add_messages' ensures we append rather than overwrite.
    messages: Annotated[List[BaseMessage], add_messages]
    
    # The current isolated question being asked
    query: str
    
    # The decision made by the Router Node ("code", "git", "both", or "general")
    route: str
    
    # The raw string contexts retrieved from Qdrant
    retrieved_context: str
    
    # Optional: Track the specific file paths or hashes retrieved for UI rendering
    sources: List[Dict[str, Any]]