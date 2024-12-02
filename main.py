from fastapi import FastAPI
from RAG.graph import app as rag_app
import os
from pprint import pprint
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from web_crawler_and_scraper.crawl_n_scrape import scrape_website
from web_crawler_and_scraper.format_files import process_files_in_directory
from web_crawler_and_scraper.description_generator import generate_descriptions
from vector_db.chroma import process_descriptions

load_dotenv()
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')  
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

app = FastAPI()
chat_histories: Dict[str, List[str]] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def test():
    config = {"configurable": {"thread_id": "1234"}}
    inputs = {
        "question": "How to fill the income tax return?",
    }
    for output in rag_app.stream(inputs, config=config):
        for key, value in output.items():
            # Node
            pprint(f"Node '{key}':")
            pprint(value, indent=2, width=80, depth=None)
        pprint("\n---\n")

    pprint(value["generation"])   
    return value["generation"]

@app.post("/chat")
async def chat(request: dict):
    if not (os.path.exists("./vector_db/vectorstore") and os.path.exists("./vector_db/descriptions")):
        return {"answer": "Scrape website first"}
    
    question = request.get("question")
    thread_id = request.get("thread_id")
    print(question)
    inputs = {
        "question": question
    }
    config = {"configurable": {"thread_id": thread_id}}
    for output in rag_app.stream(inputs, config=config):
        for key, value in output.items():
            pprint(f"Node '{key}':")
            pprint(value, indent=2, width=80, depth=None)
        pprint("\n---\n")

    pprint(value["generation"])
    return {"answer": value["generation"]}

@app.post("/web_scrape")
async def web_scrape(request: dict):
    url = request.get("url")
    page_limit = request.get("page_limit")
    scrape_website(url, page_limit)
    process_files_in_directory()
    generate_descriptions()
    process_descriptions()
    return {"status": "ok"}
