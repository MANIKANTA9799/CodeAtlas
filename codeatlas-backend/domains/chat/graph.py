from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage

from .state import AgentState
from .router import RouterNode
from .retrieval import RetrievalNode
from .synthesis import SynthesisNode

def build_codeatlas_graph(llm_client):
    """
    Assembles the stateful LangGraph workflow for CodeAtlas.
    """
    # Instantiate nodes
    router_node = RouterNode(llm_client=llm_client)
    retrieval_node = RetrievalNode()
    synthesis_node = SynthesisNode(llm_client=llm_client)

    # 1. Define Node Functions
    def run_router(state: AgentState) -> dict:
        query = state["query"]
        decision = router_node.route_query(query)
        return {"route": decision.route}

    def run_retrieval(state: AgentState) -> dict:
        query = state["query"]
        route = state["route"]
        project_name = state.get("project_name", "default_project") # <-- NEW
        
        # Pass project_name to the retrieval node
        result = retrieval_node.retrieve(query=query, route=route, project_name=project_name) 
        return {
            "retrieved_context": result["context"],
            "sources": result["sources"]
        }

    def run_synthesis(state: AgentState) -> dict:
        query = state["query"]
        context = state["retrieved_context"]
        messages = state.get("messages", [])
        
        answer = synthesis_node.synthesize(query=query, context=context, messages_history=messages)
        
        return {
            "messages": [AIMessage(content=answer)]
        }

    # 2. Build Graph Architecture
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("router", run_router)
    workflow.add_node("retriever", run_retrieval)
    workflow.add_node("synthesizer", run_synthesis)

    # Define Edges (Execution Path)
    workflow.set_entry_point("router")
    workflow.add_edge("router", "retriever")
    workflow.add_edge("retriever", "synthesizer")
    workflow.add_edge("synthesizer", END)

    # Compile Executable Graph
    return workflow.compile()