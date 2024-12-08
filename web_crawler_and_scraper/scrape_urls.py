import os
import argparse
# from crawl_n_scrape import scrape_website
from crawl_n_scrape_playwright import scrape_website
from get_urls import get_urls_from_google, get_urls_from_tavily
from initial_url_filter import filter_relevant_urls
import asyncio

page_count_to_scrape = 20 # number of pages to scrape for each url
os.chdir("e:\\WORK\\langchains\\run4Office\\web_crawler_and_scraper")

primary_urls = [
    "https://ballotpedia.org/List_of_current_mayors_of_the_top_100_cities_in_the_United_States",
    "https://justfacts.votesmart.org/elections"
]


os.makedirs("urls", exist_ok=True)
def get_urls_and_filter():
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

    print("\nFiltered URLs:")
    for url in filtered_urls:
        print(f"- {url}")
        # scrape_website(url, pages_to_scrape)

def scrape_urls():
    with open("./urls/initial_filtered_urls.txt", "r") as f:
        urls = f.readlines()
        for url in urls:
            print(f"\nScraping URL: {url.strip()}")
            # scrape_website(url.strip(), page_count_to_scrape)
            asyncio.run(scrape_website(url.strip(), page_count_to_scrape))

def main():
    parser = argparse.ArgumentParser(description="Web scraping and data processing script.")
    parser.add_argument(
        "action",
        choices=["get_urls", "scrape"],
        help="Specify the action to perform: 'get_urls' or 'scrape'."
    )
    
    args = parser.parse_args()

    if args.action == "get_urls":
        get_urls_and_filter()
    elif args.action == "scrape":
        scrape_urls()

if __name__ == "__main__":
    main()

