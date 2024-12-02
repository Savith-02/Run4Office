from RAG.agents.generate import rag_chain

def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["contextualized_question"]
    vectorstore_documents = state["vectorstore_documents"]
    # RAG generation
    generation = rag_chain.invoke(
        {
            "vectorstore_context": vectorstore_documents,
            "question": question,
            "chat_history": state["chat_history"]
        }
    )

    return {
        "question": question, 
        "generation": generation,
        "chat_history": [
            {"role": "user", "content": question},
            {"role": "assistant", "content": generation}
        ]
    }