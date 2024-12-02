import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv
from vector_db.chroma import openai_ef, collection
load_dotenv()


results = collection.query(
    query_texts=["How to fill tax documents"],
    n_results=3,
)

print(results)

