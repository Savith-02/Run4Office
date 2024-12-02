from typing import List

from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages.base import BaseMessage


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        chat_history: chat history
        contextualized_question: contextualized question
    """

    question: str
    generation: str
    chat_history: Annotated[List[BaseMessage], add_messages]
    contextualized_question: str
    vectorstore_search_query: str
    vectorstore_documents: list
