import os
os.chdir("e:\\WORK\\langchains\\run4Office\\web_crawler_and_scraper")
from crawl_n_scrape import scrape_website

pages_to_scrape = 15 # number of pages to scrape for each url
urls = [
    "https://ballotpedia.org/List_of_current_mayors_of_the_top_100_cities_in_the_United_States",
    "https://justfacts.votesmart.org/elections"
]
for url in urls:
    scrape_website(url, pages_to_scrape)


