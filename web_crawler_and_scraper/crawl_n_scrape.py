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
# from web_crawler_and_scraper.clean_html import clean_soup, strip_structure
from clean_html import clean_soup
from logger import open_log_files, log_rejection, log_crawled_link
from init import initialize_directories
from bs4 import BeautifulSoup
from init import clear_scraped_files
from additional_cleaning import clean_html
from utils import get_base_filename, format_and_save_file

# Set a custom process name
os.system("title web_crawler_scraper")  # For Windows
# Global log file handles
rejected_log = None
crawled_log = None

visited = set()
queue = Queue()

# Global variables
PAGE_LIMIT = 5  # Set this to an integer to limit the number of pages, or None for no limit
BASE_DIRECTORY = None
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
        # print(f"Fetching: {url}")
        driver.get(url)
        time.sleep(2)  # Wait for JavaScript content to load
        page_source = driver.page_source

        # Detect language and skip non-English pages
        if detect(page_source) != "en":
            log_rejection(url, "Rejected due to non-English content")
            return None, None

        soup = BeautifulSoup(page_source, 'html.parser')
        # print(f"Parsed: {url}")
        # print(soup)
        return soup, url
    except Exception as e:
        log_rejection(url, f"Error: {e}")
    return None, None

# Parse links from the page content
def parse_links(soup, base_url):
    # print(f"Parsing links from: {base_url}")
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
                # print(f"link added: {url}")
                links.add(url)

    # Log rejected links if any
    if rejected_links:
        log_rejection(rejected_links, "Rejected due to query parameters.")

    return links

# Save the cleaned HTML to a file
def save_to_file(url, soup):
    # global BASE_DIRECTORY
    base_filename = urlparse(url).path.replace("/", "_") or "index"
    filename = f"./scraped_files/{BASE_DIRECTORY}/{base_filename}.txt"

    # Check if file exists, and create unique filename if necessary
    if os.path.exists(filename):
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        filename = f"{base}_{counter}{ext}"

    clean_soup(soup)
    plain_text = str(soup)
    text = clean_html(plain_text)

    with open(filename, "w", encoding="utf-8") as file:
        file.write("URL: " + url + "\n\n")
        file.write(text)
    format_and_save_file(text, url, base_filename, BASE_DIRECTORY)

# Crawl the URL, extract content, and parse links
def crawl(driver, url):
    global crawled_count
    # Check limit safely with a lock
    with crawled_count_lock:
        if PAGE_LIMIT is not None and crawled_count >= PAGE_LIMIT:
            print(f"Crawling stopped at {crawled_count} pages.")
            return
    # print(f"Crawling: {url}")
    if url not in visited:
        # print(url)
        log_crawled_link(url)
        visited.add(url)
        soup, actual_url = fetch_and_parse_page(driver, url)
        if soup:
            # print("Soup after saving to file", soup)
            links = parse_links(soup, actual_url)
            # print("Links", links)
            for link in links:
                if link not in visited:
                    queue.put(link)
            save_to_file(actual_url, soup)  # Save the cleaned HTML content to file
                    
        # Increment the crawled count within the lock
        with crawled_count_lock:
            crawled_count += 1

# Worker thread for crawling
def worker(driver):
    while True:
        # Check for PAGE_LIMIT
        with crawled_count_lock:
            if PAGE_LIMIT is not None and crawled_count >= PAGE_LIMIT:
                print(f"Crawling stopped at {crawled_count} pages.")
                break 
        
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
    # Initialize logs and directories
    global PAGE_LIMIT
    if page_limit:
        PAGE_LIMIT = page_limit
    print(f"PAGE_LIMIT is: {PAGE_LIMIT}")
    initialize_directories(start_url)
    clear_scraped_files(start_url)
    global rejected_log
    global crawled_log
    rejected_log, crawled_log = open_log_files(start_url)
    global BASE_DIRECTORY
    BASE_DIRECTORY = get_base_filename(start_url)
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

    global crawled_count
    crawled_count = 0
    driver.quit()
    rejected_log.close()
    crawled_log.close()
    queue.queue.clear()
    visited.clear()

