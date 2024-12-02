from langgraph.graph import StateGraph, START, END
from RAG.graph_state import GraphState
from RAG.nodes.contextualize_query import contextualize_question
from RAG.nodes.extracter_queries import extract_queries
from RAG.nodes.retriever import retrieve
from RAG.nodes.generate import generate
from langgraph.checkpoint.memory import MemorySaver

# Define a new graph
workflow = StateGraph(GraphState)

workflow.add_node("contextualize_question", contextualize_question)
workflow.add_node("extract_queries", extract_queries)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.add_edge(START, "contextualize_question")
workflow.add_edge("contextualize_question", "extract_queries")
workflow.add_edge("extract_queries", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)