import os
import requests
from tavily import TavilyClient

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("SEARCH_ENGINE_API_KEY")
google_cx = os.getenv("CX")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

query = "Local government vacancies of 2024 onwards and upcoming election information in the USA"
or_terms = "elections, public office, candidacy filing, ballot measures, election boards, government positions, usa"
date_restrict = "y3"
num = 10 

# Construct the URL
url = "https://www.googleapis.com/customsearch/v1"
params = {
    "key": GOOGLE_API_KEY,
    "cx": google_cx,
    "q": query,
    "hl": "en",
    "cr": "countryUS",
    "lr": "lang_en",
    "num": num,
    "dateRestrict": date_restrict,
    "orTerms": or_terms,
    "fileType": "html"
}

def get_urls_from_google(url: str=url, params: dict=params):
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        urls = [item['link'] for item in data.get('items', [])]
        print("\nURLs from Google:")
        for url in urls:
            print(url)
        return urls
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def get_urls_from_tavily(query: str=query):
    response = tavily_client.search(
        query=query,
        include_answer=True,  # Exclude direct answers, focus on results
        include_images=False,  # Exclude images
        max_results=10         # Limit results for relevance
    )

    # Process and extract relevant URLs
    if response and "results" in response:
        urls = [result["url"] for result in response["results"] if "url" in result]
        print("\nURLs from Tavily:")
        for url in urls:
            print(url)
        return urls
    else:
        print("No relevant results found.")

if __name__ == "__main__":
    urls_from_google = get_urls_from_google()
    urls_from_tavily = get_urls_from_tavily()
    urls = urls_from_google + urls_from_tavily
    
    with open("urls.txt", "w") as f:
        for url in urls:
            f.write(url + "\n")
