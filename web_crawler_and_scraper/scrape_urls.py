import os
import requests
os.chdir("e:\\WORK\\langchains\\run4Office\\web_crawler_and_scraper")
from crawl_n_scrape import scrape_website
from get_urls import get_urls_from_google, get_urls_from_tavily
from initial_url_filter import filter_relevant_urls
pages_to_scrape = 15 # number of pages to scrape for each url
primary_urls = [
    "https://ballotpedia.org/List_of_current_mayors_of_the_top_100_cities_in_the_United_States",
    "https://justfacts.votesmart.org/elections"
]


os.makedirs("urls", exist_ok=True)
def scrape_urls():
    urls_from_google = get_urls_from_google()
    urls_from_tavily = get_urls_from_tavily()
    all_urls = primary_urls + urls_from_google + urls_from_tavily
    filtered_urls = filter_relevant_urls(all_urls)

    with open("./urls/initial_urls.txt", "w") as f:
        for url in all_urls:
            f.write(url + "\n")

    with open("./urls/initial_filtered_urls.txt", "w") as f:
        for url in filtered_urls:
            f.write(url + "\n")

    for url in filtered_urls:
        print(f"Scraping URL: {url}")
        # scrape_website(url, pages_to_scrape)

if __name__ == "__main__":
    scrape_urls()

