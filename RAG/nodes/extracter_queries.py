from RAG.agents.decider import question_extractor
from langchain_core.messages import HumanMessage

def extract_queries(state):
    from RAG.graph import app
    """
    Extract queries for vector search.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---EXTRACT QUERIES---")

    contextualized_question = state["contextualized_question"]
    source = question_extractor.invoke({"question": contextualized_question})
    
    return {
        "vectorstore_search_query": source.vectorstore_search_query,
        "question": contextualized_question,
        }
