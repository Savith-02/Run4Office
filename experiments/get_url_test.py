import os
import requests
import math
from tavily import TavilyClient
import random
from openai import OpenAI
import dotenv
dotenv.load_dotenv()

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("SEARCH_ENGINE_API_KEY")
google_cx = os.getenv("CX")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
open("urls.txt", "w").write("")

target_url_count = 50  # Total unique URLs required
url_count_needed_from_google = 18
google_urls_per_query = 8
tavily_urls_per_query = 10
if target_url_count < url_count_needed_from_google:
    raise Exception("Target url count is less than the number of urls needed from google")
else:
    url_count_needed_from_tavily = target_url_count - url_count_needed_from_google

print(f"Target url count: {target_url_count}")
print(f"Url count needed from google: {url_count_needed_from_google}")
print(f"Google urls per query: {google_urls_per_query}")
print(f"Url count needed from tavily: {url_count_needed_from_tavily}")
print(f"Tavily urls per query: {tavily_urls_per_query}")
class promptGenerator():
    def __init__(self):
        self.prompt_current_index = 0
        self.query_base = "Local government vacancies of 2024 onwards and upcoming election information in the USA"
        self.prompts = [self.query_base]
        self.keywords = ["elections", "public office", "candidacy filing", "ballot measures",
            "election boards", "government positions", "USA local government",
            "mayoral elections", "filing windows", "district elections",
        ]
        self.fetched_urls_count = 0
        self.MAX_PROMPT_COUNT = 100

    def get_prompts_from_llm(self):
        print(f"Getting prompts from LLM")
        current_prompt_count = len(self.prompts)
        sample_size = 10 if current_prompt_count > 10 else current_prompt_count
        past_prompts = random.sample(list(self.prompts), sample_size)
        new_urls = callLLM(past_prompts, self.query_base)
        self.prompts.extend(new_urls)
        self.fetched_urls_count += len(new_urls)
        return new_urls
    
    def get_Keywords(self):
        print(f"Getting keywords from promptGenerator")
        random_keywords = random.sample(self.keywords, 5)
        return random_keywords
    
    def get_prompt(self):
        print(f"Getting prompt from promptGenerator")
        if self.fetched_urls_count >= self.MAX_PROMPT_COUNT:
            print(f"Max prompts fetched. Stopping.")
            return None
        if self.prompt_current_index + 1 > len(self.prompts):
            print(f"Need more prompts. Fetching more.")
            try:
                self.get_prompts_from_llm()
            except Exception as e:
                print(f"Error fetching prompts: {e}")
                return None
        prompt = self.prompts[self.prompt_current_index]
        self.prompt_current_index += 1
        return prompt

    def reset_prompt_index(self):
        self.prompt_current_index = 0

def callLLM(past_prompts, base_prompt):
    print(f"Calling LLM")
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
    response = openai_client.chat.completions.create(
        model=os.getenv("GPT_MODEL_MINI"),
        messages=[{"role": "user", "content": content}],
        temperature=0.5,
    )
    answers = [line.strip() for line in response.choices[0].message.content.split("\n") if line.strip()]
    print(answers)
    if len(answers) != 10:
        print(f"Error: {len(answers)} answers received. Expected 10.")
        return None
    return answers

# Configurable parameters
date_restrict = "y3"

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
        "num": 10,
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

def get_all_urls_per_query_google(query: str, extra_keywords: str, needed_url_count: int):
    print(f"\nGetting URLs for query: {query}")
    should_fetch_count = min(google_urls_per_query, needed_url_count)
    loop_count = int(math.ceil(should_fetch_count / 10))
    urls = set()
    for i in range(0, loop_count):
        print(f"Getting URLs for query: - page {i + 1}")
        start = 1 if i == 0 else (i * 10 + 1)
        urls.update(get_urls_from_google(query, extra_keywords, start))
    urls = filter_urls(urls)
    return list(urls)[:should_fetch_count]


def filter_urls(urls):
    return {url for url in urls if "ballotpedia.org" not in url}


def fetch_all_urls():
    """Main function to iteratively fetch unique URLs, excluding Ballotpedia."""
    global collected_urls
    prompt_generator = promptGenerator()
    url_store = set()
    url_count_from_google = 0
    google_iteration_count = 0
    max_google_iteration_limit = int(math.ceil((url_count_needed_from_google / google_urls_per_query) * 1.4))
    print(f"Max google iteration limit: {max_google_iteration_limit}")

    google_url_store = set()
    duplicates_this_iteration = 0
    try:
        while (len(google_url_store) < url_count_needed_from_google):
            print(f"\nGetting URLs from Google - iteration {google_iteration_count + 1}")
            prompt = prompt_generator.get_prompt()
            if prompt is None:
                print("No more prompts to generate. Stopping early.")
                break
            keywords = prompt_generator.get_Keywords()
            
            needed_url_count = url_count_needed_from_google - url_count_from_google
            urls = get_all_urls_per_query_google(prompt, keywords, needed_url_count)
            url_count_from_google += len(urls)
            google_url_store.update(urls)
            total_duplicates_from_google = url_count_from_google - len(google_url_store)
            duplicates_this_iteration = total_duplicates_from_google - duplicates_this_iteration
            print(f"Duplicate count from google in this iteration: {duplicates_this_iteration}")
            print(f"Total duplicates from google: {total_duplicates_from_google}")
            print(f"Store has {len(google_url_store)} URLs")
            google_iteration_count += 1
            if google_iteration_count >= max_google_iteration_limit:
                print(f"Max iteration limit for google reached. Stopping early.")
                break
    except Exception as e:
        print(f"Error: {e}")
        open("urls.txt", "a").write("\n".join(list(google_url_store)[:url_count_needed_from_google]))

    google_url_store = list(google_url_store)[:url_count_needed_from_google]
    open("urls.txt", "a", encoding="utf-8").write("\n".join(list(google_url_store)))

    prompt_generator.reset_prompt_index()

    tavily_url_store = set()
    url_count_from_tavily = 0
    tavily_iteration_count = 0
    max_tavily_iteration_limit = int(math.ceil((url_count_needed_from_tavily / tavily_urls_per_query) * 1.4))
    total_duplicates = 0
    print(f"Max tavily iteration limit: {max_tavily_iteration_limit}")
    try:
        while url_count_from_tavily < url_count_needed_from_tavily:
            print(f"\nGetting URLs from Tavily - iteration {tavily_iteration_count + 1}")
            prompt = prompt_generator.get_prompt()
            if prompt is None:
                print("No more prompts to generate. Stopping early.")
                break

            # Get and filter URLs
            urls = get_urls_from_tavily(prompt)
            print(f"Got {len(urls)} urls from tavily")
            urls = filter_urls(urls)
            print(f"Filtered: {len(urls)} urls now")

            # Calculate duplicates for this iteration
            previous_store_size = len(tavily_url_store)
            tavily_url_store.update(urls)
            current_store_size = len(tavily_url_store)
            
            # Calculate duplicates
            duplicates_this_iteration = len(urls) - (current_store_size - previous_store_size)
            total_duplicates += duplicates_this_iteration

            # Update counts
            url_count_from_tavily += len(urls)
            
            # Print status
            print(f"Store has {current_store_size} unique URLs")
            print(f"Total URLs processed: {url_count_from_tavily}")
            print(f"Duplicates in this iteration: {duplicates_this_iteration}")
            print(f"Total duplicates so far: {total_duplicates}")

            tavily_iteration_count += 1
            if tavily_iteration_count >= max_tavily_iteration_limit:
                print(f"Max iteration limit for tavily reached. Stopping early.")
                break
    except Exception as e:
        print(f"Error: {e}")
        open("urls.txt", "a", encoding="utf-8").write("\n".join(list(tavily_url_store)[:url_count_needed_from_tavily]))

    tavily_url_store = list(tavily_url_store)[:url_count_needed_from_tavily]
    open("urls.txt", "a", encoding="utf-8").write("\n".join(list(tavily_url_store)))

    print(f"Final URL collection complete: {len(tavily_url_store + google_url_store)} URLs.")
    return tavily_url_store + google_url_store

def get_urls_from_tavily(query: str):
    """Fetches URLs from Tavily API."""
    response = tavily_client.search(
        query=query,
        include_answer=False,  # Exclude direct answers, focus on results
        include_images=False,  # Exclude images
        max_results=tavily_urls_per_query,
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
