import json
from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage

class RouteDecision(BaseModel):
    """
    Schema for the router node classification output.
    """
    route: Literal["code", "git", "both", "general"] = Field(
        description="The target retrieval source based on user intent."
    )
    reasoning: str = Field(
        description="Brief explanation of why this route was selected."
    )

class RouterNode:
    """
    Classifies user queries into discrete operational routes using structured outputs.
    """

    SYSTEM_PROMPT = """You are an expert query router for a codebase intelligence platform.
Your sole job is to analyze the user's input and classify its intent into exactly one of four routes:

1. 'code': The query asks about logic, architecture, how a feature works, class definitions, function parameters, or current system design. If the user asks "How does X work?" or "Explain Y logic", assume they mean within THIS codebase and choose 'code'.
2. 'git': The query asks about historical changes, commit messages, author contributions, past refactors, or why a change was made in the past.
3. 'both': The query asks for a comparison between past changes and current code, or requires both historical context and current implementation.
4. 'general': STRICTLY for greetings ("hello", "hi"), small talk, or extremely broad programming questions completely unrelated to any specific codebase (e.g., "What is Python?"). DO NOT use this for questions about logic, routing, or architecture.

CRITICAL RULE: When in doubt about a technical question, ALWAYS default to 'code'.

You MUST respond strictly with valid JSON conforming to this schema:
{
    "route": "code" | "git" | "both" | "general",
    "reasoning": "short explanation"
}
"""

    def __init__(self, llm_client=None):
        self.llm = llm_client

    def route_query(self, query: str) -> RouteDecision:
        """
        Executes query classification with deterministic fallback protection.
        """
        if not self.llm:
            return RouteDecision(route="code", reasoning="Default route; no LLM client attached.")

        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Query: {query}")
        ]

        try:
            response = self.llm.invoke(messages)
            content = response.content.strip()

            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            data = json.loads(content)
            return RouteDecision(**data)

        except Exception as e:
            print(f"Router classification error: {str(e)}. Defaulting to 'code'.")
            return RouteDecision(route="code", reasoning=f"Fallback due to parsing error: {str(e)}")