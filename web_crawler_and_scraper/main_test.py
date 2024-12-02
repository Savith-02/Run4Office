import os
os.chdir("e:\\WORK\\langchains\\run4Office\\web_crawler_and_scraper")
from crawl_n_scrape import scrape_website

scrape_website("https://ballotpedia.org/List_of_current_mayors_of_the_top_100_cities_in_the_United_States", 3)
# scrape_website("https://www.ird.gov.lk/", 3)