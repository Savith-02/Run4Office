from RAG.tools.vecterstore_retriever import retrieve_vectorstore_documents


def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    print(state)
    vectorstore_search_query = state["vectorstore_search_query"]

    # Retrieval
    if vectorstore_search_query:
        vectorstore_documents = retrieve_vectorstore_documents(vectorstore_search_query)
    else:
        vectorstore_documents = []

    return {"vectorstore_documents": vectorstore_documents} 
