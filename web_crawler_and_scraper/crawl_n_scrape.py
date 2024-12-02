import os
import time
import threading
import requests
from urllib.parse import urljoin, urlparse, parse_qs
from queue import Queue
from langdetect import detect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from web_crawler_and_scraper.clean_html import clean_soup, strip_structure, remove_elements_by_class_pattern, remove_elements_by_id_pattern, remove_unwanted_attributes
from web_crawler_and_scraper.logger import open_log_files, log_rejection, log_crawled_link
from web_crawler_and_scraper.init import initialize_directories
from bs4 import BeautifulSoup

# Set a custom process name
os.system("title web_crawler_scraper")  # For Windows
# Global log file handles
rejected_log = None
crawled_log = None

visited = set()
queue = Queue()

# Global variables
PAGE_LIMIT = 5  # Set this to an integer to limit the number of pages, or None for no limit
crawled_count = 0  # Counter for the number of pages crawled
crawled_count_lock = threading.Lock()  # Lock for safe access to crawled_count

# Initialize WebDriver for Selenium
def initialize_driver():
    options = Options()
    options.headless = True  # Run headless to avoid opening a browser window
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Fetch and parse the page using Selenium, clean unnecessary elements
def fetch_and_parse_page(driver, url):
    try:
        # Check the HTTP status code using requests
        response = requests.get(url)
        if response.status_code != 200:
            log_rejection(url, f"Rejected due to HTTP status code: {response.status_code}")
            return None, None
        
        driver.get(url)
        time.sleep(2)  # Wait for JavaScript content to load
        page_source = driver.page_source

        # Detect language and skip non-English pages
        if detect(page_source) != "en":
            log_rejection(url, "Rejected due to non-English content")
            return None, None

        # Parse HTML and clean unnecessary elements
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup, url
    except Exception as e:
        log_rejection(url, f"Error: {e}")
    return None, None

# Parse links from the page content
def parse_links(soup, base_url):
    links = set()
    rejected_links = []
    required_params = {"lang": "en"}  # Only consider links with 'lang=en'
    rejected_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.XLSX', '.zip', '.rar', '.7z','.xlsm', '.jpg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp']

    for a_tag in soup.find_all("a", href=True):
        url = urljoin(base_url, a_tag["href"])

        # Check if the link is within the same domain
        if urlparse(url).netloc == urlparse(base_url).netloc:
            # Reject links ending with specified extensions
            if any(url.lower().endswith(ext.lower()) for ext in rejected_extensions):
                rejected_links.append(url)
                continue

            query_params = parse_qs(urlparse(url).query)

            # Check if the required parameters match
            reject = False
            for key, value in required_params.items():
                if key in query_params and query_params[key][0] != value:
                    reject = True
                    break
            
            if reject:
                rejected_links.append(url)
            else:
                links.add(url)

    # Log rejected links if any
    if rejected_links:
        log_rejection(rejected_links, "Rejected due to query parameters.")

    return links

# Save the cleaned HTML to a file
def save_to_file(url, soup):
    base_filename = urlparse(url).path.replace("/", "_") or "index"
    filename = f"./web_crawler_and_scraper/scraped_files/{base_filename}.txt"

    # Check if file exists, and create unique filename if necessary
    if os.path.exists(filename):
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        filename = f"{base}_{counter}{ext}"

    # Convert soup to string and remove empty lines
    soup = remove_elements_by_class_pattern(soup, [r"^header", r"^footer", r"^hidden", r"^nav"])
    soup = remove_elements_by_id_pattern(soup, [r"^hidden", r"^nav", r"^header", r"^footer", r"^div"])
    soup = remove_unwanted_attributes(soup, ['href', "type", "name"])
    clean_soup(soup)
    cleaned_content = strip_structure(soup)
    # Save the cleaned HTML content to the file
    with open(filename, "w", encoding="utf-8") as file:
        file.write("URL: " + url + "\n\n")
        file.write(cleaned_content)

# Crawl the URL, extract content, and parse links
def crawl(driver, url):
    global crawled_count
    # Check limit safely with a lock
    with crawled_count_lock:
        if PAGE_LIMIT is not None and crawled_count >= PAGE_LIMIT:
            return  # Stop if the limit is reached

    if url not in visited:
        print(url)
        log_crawled_link(url)
        visited.add(url)
        soup, actual_url = fetch_and_parse_page(driver, url)
        if soup:
            save_to_file(actual_url, soup)  # Save the cleaned HTML content to file
            links = parse_links(soup, actual_url)
            for link in links:
                if link not in visited:
                    queue.put(link)
                    
        # Increment the crawled count within the lock
        with crawled_count_lock:
            crawled_count += 1

# Worker thread for crawling
def worker(driver):
    while True:
        # Check for PAGE_LIMIT
        with crawled_count_lock:
            if PAGE_LIMIT is not None and crawled_count >= PAGE_LIMIT:
                break  # Exit if PAGE_LIMIT is reached
        
        # If queue is empty, also exit the worker loop
        if queue.empty():
            break
        
        url = queue.get()
        crawl(driver, url)
        queue.task_done()
        time.sleep(1)  # Be polite

# Main entry point
def scrape_website(start_url, page_limit=None):
    print("Scraping website started")
    update_checkpoint_file(start_url)
    # Initialize logs and directories
    global PAGE_LIMIT
    if page_limit:
        PAGE_LIMIT = page_limit
    initialize_directories()
    rejected_log, crawled_log = open_log_files()

    queue.put(start_url)

    # Initialize Selenium WebDriver
    driver = initialize_driver()

    # Start multiple threads for parallel crawling
    threads = []
    for _ in range(4):
        thread = threading.Thread(target=worker, args=(driver,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Close the driver and log files after finishing crawling
    driver.quit()
    rejected_log.close()
    crawled_log.close()

def update_checkpoint_file(current_url, checkpoint_file='checkpoint.txt'):
    # Check if the checkpoint file exists
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r', encoding='utf-8') as file:
            first_line = file.readline().strip()
    else:
        first_line = None

    # Compare the first line with the current URL
    if first_line != current_url:
        # Empty the file and write the current URL
        with open(checkpoint_file, 'w', encoding='utf-8') as file:
            file.write(current_url + '\n')
        print(f"Checkpoint file updated. New URL: {current_url}")
    else:
        print("Checkpoint file is up-to-date. No changes made.")