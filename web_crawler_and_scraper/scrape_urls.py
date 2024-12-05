import os
import requests
os.chdir("e:\\WORK\\langchains\\run4Office\\web_crawler_and_scraper")
from crawl_n_scrape import scrape_website

pages_to_scrape = 15 # number of pages to scrape for each url
primary_urls = [
    "https://ballotpedia.org/List_of_current_mayors_of_the_top_100_cities_in_the_United_States",
    "https://justfacts.votesmart.org/elections"
]
# for url in primary_urls:
#     scrape_website(url, pages_to_scrape)



# Define your API key and other parameters
api_key = os.getenv("SEARCH_ENGINE_API_KEY")
cx = os.getenv("CX")
query = "detailed, nonpartisan information about U.S. elections, including candidate profiles, ballot measures, election dates, and public office requirements at federal, state, and local levels."
hl = "en"
cr = "countryUS"
gl = "us"
lr = "lang_en"
num = 10
# sort = "date-sdate:r:20220101:"
date_restrict = "y3"
or_terms = "elections, public office, candidacy filing, ballot measures, election boards, government positions, usa"

# Construct the URL
url = "https://www.googleapis.com/customsearch/v1"
params = {
    "key": api_key,
    "cx": cx,
    "q": query,
    "hl": hl,
    "cr": cr,
    "gl": gl,
    "lr": lr,
    "num": num,
    "dateRestrict": date_restrict,
    "orTerms": or_terms
}

# Send the HTTP request
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    # print(data.keys())
    # Extract URLs from the response
    urls = [item['link'] for item in data.get('items', [])]
    print(len(urls))
    print(urls)
    all_urls = primary_urls + urls
    for url in all_urls:
        scrape_website(url, pages_to_scrape)
else:
    print(f"Error: {response.status_code} - {response.text}")