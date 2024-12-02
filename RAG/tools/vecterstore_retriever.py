import chromadb.utils.embedding_functions as embedding_functions
import chromadb
import os

client = chromadb.PersistentClient(path="./vector_db/vectorstore")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
            )
collection = client.get_or_create_collection(name="my_collection", embedding_function=openai_ef)

def retrieve_vectorstore_documents(query):
    results = collection.query(
        query_texts=query,
        n_results=2,
    )

    # Extracting and formatting the results
    formatted_results = {}
    
    # Loop through the result metadata and documents
    for i in range(len(results["documents"][0])):
        # Extract the document, title, and link from the results
        document = results["documents"][0][i]
        title = results["metadatas"][0][i]["title"]
        link = results["metadatas"][0][i]["link"]
        
        # Add to the dictionary
        formatted_results[title] = [{"content": document, "link": link}]

    return formatted_results