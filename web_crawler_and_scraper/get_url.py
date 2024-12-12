import os
import requests
import math
import random
from typing import List, Set, Optional
from tavily import TavilyClient
from openai import OpenAI
import dotenv
from initial_url_filter import filter_urls
os.chdir("e:\\WORK\\langchains\\run4Office\\web_crawler_and_scraper")

# Load environment variables and initialize clients
dotenv.load_dotenv(override=True)
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration
TARGET_URL_COUNT = 80 # Total number of URLs to collect
GOOGLE_URL_COUNT = 40 # Number of URLs to collect from Google
GOOGLE_URLS_PER_QUERY = 8 # Number of URLs to collect from each Google query
DATE_RESTRICT = "y3" # Date restriction for Google search

if TARGET_URL_COUNT < GOOGLE_URL_COUNT:
    raise ValueError("Target URL count must be greater than Google URL count")
TAVILY_URL_COUNT = TARGET_URL_COUNT - GOOGLE_URL_COUNT
TAVILY_URLS_PER_QUERY = 8 # Number of URLs to collect from each Tavily query

# Filter config
config = {
    "exclude_domains": {"ballotpedia.org"},
    "include_domains": {},
    "exclude_paths": {},
    "include_paths": {},
    "schemes": {"https"},
    "max_length": 140
}

# Initialize file
os.makedirs("urls", exist_ok=True)
open("./urls/initial_urls.txt", "w").close()

class PromptGenerator:
    """Handles prompt generation and management"""
    def __init__(self):
        self.prompt_current_index = 0
        self.query_base = "Local government vacancies of 2024 onwards and upcoming election information in the USA"
        self.prompts = [self.query_base]
        self.keywords = [
            "elections", "public office", "candidacy filing", "ballot measures",
            "election boards", "government positions", "USA local government",
            "mayoral elections", "filing windows", "district elections",
        ]
        self.fetched_urls_count = 0
        self.MAX_PROMPT_COUNT = 100

    def get_prompts_from_llm(self) -> Optional[List[str]]:
        sample_size = min(10, len(self.prompts))
        past_prompts = random.sample(list(self.prompts), sample_size)
        new_prompts = generate_prompts_with_llm(past_prompts, self.query_base)
        
        if new_prompts:
            self.prompts.extend(new_prompts)
            self.fetched_urls_count += len(new_prompts)
        return new_prompts

    def get_keywords(self) -> List[str]:
        return random.sample(self.keywords, 5)

    def get_prompt(self) -> Optional[str]:
        if self.fetched_urls_count >= self.MAX_PROMPT_COUNT:
            print("Max prompts fetched. Stopping.")
            return None
            
        if self.prompt_current_index + 1 > len(self.prompts):
            print("\nNeed more prompts. Fetching more.")
            if not self.get_prompts_from_llm():
                return None
                
        prompt = self.prompts[self.prompt_current_index]
        self.prompt_current_index += 1
        return prompt

    def reset_prompt_index(self):
        self.prompt_current_index = 0

def generate_prompts_with_llm(past_prompts: List[str], base_prompt: str) -> Optional[List[str]]:
    """Generate new prompts using OpenAI"""
    content = f"""
    You are a helpful assistant that generates prompts for a search engine.
    You will be given a list of past prompts and base prompt.
    You will need to generate 10 prompts that are related to the past prompts but different.
    Delimit each prompt with a new line. Do not give a number or anything else.
    The base prompt is:
    {base_prompt}
    The past prompts are:
    {past_prompts}
    """
    
    try:
        response = openai_client.chat.completions.create(
            model=os.getenv("GPT_MODEL_MINI"),
            messages=[{"role": "user", "content": content}],
            temperature=0.5,
        )
        answers = [line.strip() for line in response.choices[0].message.content.split("\n") if line.strip()]
        print(f"Generated {len(answers)} prompts")
        return answers if len(answers) == 10 else None
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def get_urls_from_google(query: str, extra_keywords: str, start: int = 1) -> Set[str]:
    """Fetch URLs from Google Custom Search API"""
    params = {
        "key": os.getenv("SEARCH_ENGINE_API_KEY"),
        "cx": os.getenv("CX"),
        "q": query,
        "hl": "en",
        "cr": "countryUS",
        "lr": "lang_en",
        "num": 10,
        "dateRestrict": DATE_RESTRICT,
        "orTerms": extra_keywords,
        "fileType": "html",
        "start": start,
    }
    
    try:
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        response.raise_for_status()
        return {item["link"] for item in response.json().get("items", [])}
    except Exception as e:
        print(f"Google API error: {e}")
        return set()

def get_urls_from_tavily(query: str) -> Set[str]:
    """Fetch URLs from Tavily API"""
    try:
        response = tavily_client.search(
            query=query,
            include_answer=False,
            include_images=False,
            max_results=TAVILY_URLS_PER_QUERY,
        )
        return {result["url"] for result in response.get("results", []) if "url" in result}
    except Exception as e:
        print(f"Tavily API error: {e}")
        return set()

def get_all_urls_per_query_google(query: str, extra_keywords: str, needed_url_count: int) -> List[str]:
    """Fetch multiple pages of URLs from Google for a single query"""
    print(f"\nGetting URLs for query: {query}")
    should_fetch_count = min(GOOGLE_URLS_PER_QUERY, needed_url_count)
    loop_count = int(math.ceil(should_fetch_count / 10))
    urls = set()
    
    for i in range(loop_count):
        print(f"Getting URLs for query - page {i + 1}")
        # Calculate start parameter: 1, 11, 21, 31, ...
        start = 1 if i == 0 else (i * 10 + 1)
        urls.update(get_urls_from_google(query, extra_keywords, start))
    
    urls = filter_urls(urls, config)
    return list(urls)[:should_fetch_count]

def collect_urls_from_source(source: str, prompt_generator: PromptGenerator) -> List[str]:
    """Collect URLs from specified source"""
    url_store = set()
    url_count = 0
    iteration_count = 0
    total_duplicates = 0
    
    needed_urls = GOOGLE_URL_COUNT if source == "google" else TAVILY_URL_COUNT
    urls_per_query = GOOGLE_URLS_PER_QUERY if source == "google" else TAVILY_URLS_PER_QUERY
    max_iterations = int(math.ceil((needed_urls / urls_per_query) * 1.4))
    print(f"\nCollecting {needed_urls} URLs from {source}")
    
    while url_count < needed_urls and iteration_count < max_iterations:
        prompt = prompt_generator.get_prompt()
        if not prompt:
            break
            
        # Get URLs based on source
        if source == "google":
            needed_count = needed_urls - url_count
            urls = get_all_urls_per_query_google(prompt, prompt_generator.get_keywords(), needed_count)
        else:
            urls = get_urls_from_tavily(prompt)
            urls = filter_urls(urls, config)
        
        # Update URL store and count duplicates
        previous_size = len(url_store)
        url_store.update(urls)
        current_size = len(url_store)
        
        duplicates = len(urls) - (current_size - previous_size)
        total_duplicates += duplicates
        url_count += len(urls)
        
        print(f"\nTotal URLs processed: {url_count}")
        print(f"Duplicates in this iteration: {duplicates}")
        print(f"Total duplicates so far: {total_duplicates}")
        print(f"Store has {current_size} unique URLs")
        
        iteration_count += 1
    
    if url_count < needed_urls:
        print("\nWarning: Only collected {url_count} URLs, needed {needed_urls}")
    
    return list(url_store)[:needed_urls]

def save_urls(urls: List[str]):
    """Save URLs to file"""
    with open("./urls/initial_urls.txt", "a", encoding="utf-8") as f:
        f.write("\n".join(urls) + "\n")
    print(f"Saved {len(urls)} URLs to file")

def fetch_all_urls() -> List[str]:
    """Main function to fetch URLs from all sources"""
    prompt_generator = PromptGenerator()
    
    # # Collect Google URLs
    google_urls = collect_urls_from_source("google", prompt_generator)
    save_urls(google_urls)
    
    # Reset and collect Tavily URLs
    prompt_generator.reset_prompt_index()
    tavily_urls = collect_urls_from_source("tavily", prompt_generator)
    save_urls(tavily_urls)
    
    all_urls = google_urls + tavily_urls
    # all_urls = tavily_urls
    print(f"\nFinal URL collection complete: {len(all_urls)} URLs.")
    return all_urls

# if __name__ == "__main__":
#     all_urls = fetch_all_urls()
#     print("\nFinal Collected URLs (Excluding Ballotpedia):")
#     for url in all_urls:
#         print(url)