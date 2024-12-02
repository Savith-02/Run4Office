### Router

# from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel  , Field
from langchain_openai import ChatOpenAI


# Data model
class ExtractQuery(BaseModel):
    """Route a user query to the relevant datasources with subquestions."""

    vectorstore_search_query: str = Field(
        "",
        description="The query to search the vector store.",
    )

llm = ChatOpenAI(model="gpt-4o-mini")
structured_llm_router = llm.with_structured_output(ExtractQuery)

# Prompt
system = """You are an expert in determining whether a user's question should be routed to a vector store for additional information. You have access to the chat history to assist in your decision-making process.

Instructions:
1. Review the chat history to determine if the user's question has already been answered.
2. If the question is new or if additional data from the vector store could enhance the response, prepare a query for the vector store.
3. If the vector store search is unnecessary, leave the query empty.

Output:
- 'vectorstore_search_query': Provide the query for the vector store if needed, otherwise leave it empty.
"""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_extractor = route_prompt | structured_llm_router