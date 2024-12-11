import os
import requests
from tavily import TavilyClient
import random
from openai import OpenAI
import dotenv
dotenv.load_dotenv()
# API keys and initialization
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("SEARCH_ENGINE_API_KEY")
google_cx = os.getenv("CX")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

target_url_count = 50  # Total unique URLs required
url_count_needed_from_google = 25
url_count_needed_from_tavily = target_url_count - url_count_needed_from_google
google_urls_per_query = 10

class llmClient():
    def __init__(self, api_key):
        self.api_key = api_key

    def get_prompts_from_llm(self, query_base, keywords):
        pass

class promptGenerator():
    def __init__(self, query_base, keywords):
        self.query_base = query_base
        self.keywords = keywords
        self.prompt_current_index = 0
        self.prompts = set()
        self.keywords = ["elections", "public office", "candidacy filing", "ballot measures",
            "election boards", "government positions", "USA local government",
            "mayoral elections", "filing windows", "district elections",
        ]
        self.fetched_urls_count = 0
        self.query_base = "Local government vacancies of 2024 onwards and upcoming election information in the USA"
        self.MAX_PROMPT_COUNT = 100

    def get_prompts_from_llm(self):
        current_prompt_count = len(self.prompts)
        sample_size = 10 if current_prompt_count > 10 else current_prompt_count
        past_prompts = random.sample(self.prompts, sample_size)
        new_urls = callLLM(past_prompts, self.query_base)
        self.prompts.add(new_urls)
        self.fetched_urls_count += len(new_urls)
        return new_urls
    
    def get_Keywords(self):
        random_keywords = random.sample(self.keywords, 5)
        return random_keywords
    
    def get_prompt(self):
        if self.fetched_urls_count >= self.MAX_PROMPT_COUNT:
            return None
        if self.prompt_current_index >= len(self.prompts):
            self.prompts += self.get_prompts_from_llm()
            self.prompt_current_index = 0
        prompt = self.prompts[self.prompt_current_index]
        self.prompt_current_index += 1
        return prompt

def callLLM(past_prompts, prompt):
    content = f"""
    You are a helpful assistant that generates prompts for a search engine.
    You will be given a list of past prompts and base prompt.
    You will need to generate 10 prompts that are related to the past prompts but different.
    Delimit each prompt with a new line.

    The past prompts are:
    {past_prompts}
    """
    response = openai_client.chat.completions.create(
        model=os.getenv("GPT_MODEL_MINI"),
        messages=[{"role": "user", "content": content}],
        temperature=0.5,
    )
    return response.choices[0].message.content

# Configurable parameters
query_base = "Local government vacancies of 2024 onwards and upcoming election information in the USA"
keywords = [
    "elections, public office, candidacy filing, ballot measures",
    "election boards, government positions, USA local government",
    "mayoral elections, filing windows, district elections",
]
date_restrict = "y3"
num_results_per_query = 10

# Deduplication storage
collected_urls = set()


def get_urls_from_google(query: str, extra_keywords: str, start: int = 1):
    """Fetches URLs from Google Custom Search API."""
    params = {
        "key": GOOGLE_API_KEY,
        "cx": google_cx,
        "q": query,
        "hl": "en",
        "cr": "countryUS",
        "lr": "lang_en",
        "num": num_results_per_query,
        "dateRestrict": date_restrict,
        "orTerms": extra_keywords,
        "fileType": "html",
        "start": start,
    }
    response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)

    if response.status_code == 200:
        data = response.json()
        urls = {
            item["link"] for item in data.get("items", [])
        }  # Using a set to ensure uniqueness
        return urls
    else:
        print(f"Error from Google API: {response.status_code} - {response.text}")
        return set()

def get_all_urls_per_query_google(query: str, extra_keywords: str):
    urls = set()
    for i in range(1, 10):
        urls = get_urls_from_google(query, extra_keywords, i)
        urls = filter_urls(urls)
        return urls


def filter_urls(urls):
    return {url for url in urls if "ballotpedia.org" not in url}

def fetch_all_urls():
    """Main function to iteratively fetch unique URLs, excluding Ballotpedia."""
    global collected_urls
    prompt_generator = promptGenerator(query_base, keywords)
    search_methods = [get_urls_from_google, get_urls_from_tavily]
    prompt_index = 0
    method_index = 0
    url_count_from_tavily = 0

    url_count_from_google = 0
    google_iteration_count = 0
    while (url_count_needed_from_google < url_count_from_google):
        prompt = prompt_generator.get_prompt()
        if prompt is None:
            print("No more prompts to generate. Stopping early.")
            break
        keywords = prompt_generator.get_Keywords()
        urls = get_all_urls_per_query_google(prompt, extra_keywords=keywords)
        google_iteration_count += 1
        url_count_from_google += len(urls)


    while url_count_needed_from_tavily < url_count_from_tavily:
        prompt = prompt_generator.get_prompt()
        keywords = prompt_generator.get_Keywords()
        urls = get_urls_from_tavily(prompt)
        url_count_from_tavily += len(urls)
        urls = filter_urls(urls)

        # # Cycle through prompts and methods
        # prompt_index = (prompt_index + 1) % len(prompt_variations)
        # if prompt_index == 0:  # Switch method only after all prompts are used
        #     method_index = (method_index + 1) % len(search_methods)

        # Safety break (optional, to avoid infinite loops in rare cases)
        # if method_index == 0 and prompt_index == 0 and not new_urls:
        #     print("No new results in a full iteration. Stopping early to avoid endless loop.")
        #     break

    print(f"Final URL collection complete: {len(collected_urls)} URLs.")
    return collected_urls

def get_urls_from_tavily(query: str):
    """Fetches URLs from Tavily API."""
    response = tavily_client.search(
        query=query,
        include_answer=False,  # Exclude direct answers, focus on results
        include_images=False,  # Exclude images
        max_results=num_results_per_query,
    )
    if response and "results" in response:
        urls = {result["url"] for result in response["results"] if "url" in result}
        return urls
    else:
        print("No relevant results found from Tavily.")
        return set()
    
if __name__ == "__main__":
    all_urls = fetch_all_urls()
    print("\nFinal Collected URLs (Excluding Ballotpedia):")
    for url in all_urls:
        print(url)
