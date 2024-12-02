from RAG.agents.contextualize import contextualizer

def contextualize_question(state):
    print("---CONTEXTUALIZE QUESTION---")

    question = state["question"]
    chat_history = state["chat_history"]
    result = contextualizer.invoke({"input": question, "chat_history": chat_history})

    return {
        "contextualized_question": result.contextualized_question,
    }
    
