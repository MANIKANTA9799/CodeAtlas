from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class SynthesisNode:
    """
    Synthesizes the final response using the user's query and the retrieved context.
    """

    SYSTEM_PROMPT = """You are CodeAtlas, a Senior Staff Software Engineer assistant.
Your job is to answer the user's question accurately using ONLY the provided codebase and Git context.

Rules:
1. Always cite specific file paths, class/method names, or commit hashes when explaining concepts.
2. If the retrieved context does not contain enough information to answer the question, state clearly that the information is not in the indexed repository.
3. Be concise, technical, and direct in your explanation.

Context Provided:
{context}
"""

    def __init__(self, llm_client):
        self.llm = llm_client

    def synthesize(self, query: str, context: str, messages_history: list = None) -> str:#type:ignore
        """
        Generates the final natural language answer.
        """
        if not context and query.lower() in ["hi", "hello", "hey"]:
            return "Hello! I am CodeAtlas. Ask me anything about this repository's code architecture or Git history."

        system_msg = SystemMessage(content=self.SYSTEM_PROMPT.format(context=context or "No context retrieved."))
        
        prompt_messages = [system_msg]
        if messages_history:
            # Include recent chat history for conversational awareness
            prompt_messages.extend(messages_history[-4:])
        
        prompt_messages.append(HumanMessage(content=query))#type:ignore

        response = self.llm.invoke(prompt_messages)
        return response.content