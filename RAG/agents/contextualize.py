from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel  , Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

class ContextualizeQuestion(BaseModel):
  """Contextualize the question."""

  contextualized_question: str = Field(
      ...,
      description="The contextualized question.",
  )

contextualize_q_system_prompt = (
    "Given a chat history and the latest user question, "
    "which might reference context in the chat history, "
    "formulate a standalone question that can be understood "
    "without the chat history. Specifically:"
    "\n1. Replace pronouns (e.g., 'he', 'she', 'it', 'they') with their specific referents."
    "\n2. Expand references like 'that', 'this', 'those' to what they specifically refer to."
    "\n3. Include any relevant context from previous messages that's necessary to understand the question."
    "\n4. Ensure the reformulated question is clear, specific, and self-contained."
    "\nDo NOT answer the question, just reformulate it to be self-explanatory."
    'If there is no chat history ot chat history seems not enough, just pass on the input question without change'
)

llm = ChatOpenAI(model="gpt-4o-mini")
structured_llm_router = llm.with_structured_output(ContextualizeQuestion)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

contextualizer = contextualize_q_prompt | structured_llm_router
