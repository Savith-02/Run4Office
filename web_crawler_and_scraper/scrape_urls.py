import os
import argparse
from typing import List
from crawl_n_scrape_playwright import scrape_website
from get_url import fetch_all_urls
from initial_url_filter import filter_relevant_urls
import asyncio
os.chdir("e:\\WORK\\langchains\\run4Office\\web_crawler_and_scraper")
os.makedirs("urls", exist_ok=True)

page_count_to_scrape = 20 # number of pages to scrape for each url


def get_urls_and_filter():
    all_urls = fetch_all_urls()
    system_urls = get_system_urls()
    filtered_urls = filter_relevant_urls(all_urls + system_urls)

    with open("./urls/initial_filtered_urls.txt", "w") as f:
        for url in filtered_urls:
            f.write(url + "\n")

    print("\nFiltered URLs:")
    for url in filtered_urls:
        print(f"- {url}")

def scrape_urls():
    with open("./urls/initial_filtered_urls.txt", "r") as f:
        urls = f.readlines()
        for url in urls:
            print(f"\nScraping URL: {url.strip()}")
            # scrape_website(url.strip(), page_count_to_scrape)
            asyncio.run(scrape_website(url.strip(), page_count_to_scrape))

def get_system_urls() -> List[str]:
    with open("./urls/system_urls.txt", "r") as f:
        return [line.strip() for line in f.readlines()]
    
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

