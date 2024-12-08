import os
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from langdetect import detect
from logger import open_log_files, log_rejection, log_crawled_link
from init import initialize_directories, clear_scraped_files
from utils import get_base_filename, update_checkpoint_file, format_and_save_file
from additional_cleaning import clean_html

visited = set()
queue = asyncio.Queue()
PAGE_LIMIT = 5
crawled_count = 0

# Save cleaned HTML to a file
async def save_to_file(url, soup):
    base_filename = urlparse(url).path.replace("/", "_") or "index"
    filename = f"./scraped_files/{BASE_DIRECTORY}/{base_filename}.txt"
    print(f"[DEBUG] Saving file: {filename}")

    if os.path.exists(filename):
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        filename = f"{base}_{counter}{ext}"

    plain_text = str(soup)
    text = clean_html(plain_text)

    with open(filename, "w", encoding="utf-8") as file:
        file.write("URL: " + url + "\n\n")
        file.write(text)
    format_and_save_file(text, url, base_filename, "")
    print(f"[DEBUG] File saved: {filename}")

# Parse links from a page
async def parse_links(soup, base_url):
    print(f"[DEBUG] Parsing links from: {base_url}")
    links = set()
    rejected_links = []
    required_params = {"lang": "en"}
    rejected_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.7z', '.jpg', '.png', '.gif']

    for a_tag in soup.find_all("a", href=True):
        url = urljoin(base_url, a_tag["href"])
        if urlparse(url).netloc == urlparse(base_url).netloc:
            if any(url.lower().endswith(ext.lower()) for ext in rejected_extensions):
                rejected_links.append(url)
                continue
            query_params = parse_qs(urlparse(url).query)
            reject = False
            for key, value in required_params.items():
                if key in query_params and query_params[key][0] != value:
                    reject = True
                    break
            if reject:
                rejected_links.append(url)
            else:
                links.add(url)
    if rejected_links:
        log_rejection(rejected_links, "Rejected due to query parameters.")
    print(f"[DEBUG] Found {len(links)} valid links, {len(rejected_links)} rejected links.")
    return links

# Crawl a single URL
async def crawl(playwright, url):
    global crawled_count
    if PAGE_LIMIT is not None and crawled_count >= PAGE_LIMIT:
        print(f"[DEBUG] Page limit reached: {crawled_count}/{PAGE_LIMIT}")
        return
    if url in visited:
        print(f"[DEBUG] URL already visited: {url}")
        return

    visited.add(url)
    log_crawled_link(url)
    print(f"[DEBUG] Visiting URL: {url}")

    browser = await playwright.chromium.launch(headless=True)  # Use non-headless for debugging
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    page = await context.new_page()
    try:
        # Navigate to the URL with a timeout
        try:
            response = await page.goto(url, timeout=8000)
            await page.wait_for_load_state("networkidle", timeout=3000)
            print(f"[DEBUG] Successfully loaded URL: {url} with status {response.status}")
        except Exception as e:
            print(f"[WARNING] Timeout exceeded for URL: {url}, proceeding with partially loaded content. Error: {e}")

        # Get the page content, regardless of timeout
        content = await page.content()
        if not content.strip():
            print(f"[DEBUG] Empty content for URL: {url}, skipping.")
            return

        # Check for language
        if detect(content) != "en":
            log_rejection(url, "Rejected due to non-English content")
            return

        # Parse and process the content
        soup = BeautifulSoup(content, 'html.parser')
        links = await parse_links(soup, url)
        for link in links:
            if link not in visited:
                await queue.put(link)
        await save_to_file(url, soup)

    except Exception as e:
        print(f"[ERROR] Failed to crawl URL: {url}, Error: {e}")
        log_rejection(url, f"Error: {e}")
    finally:
        await context.close()
        await browser.close()
        print(f"[DEBUG] Browser closed for URL: {url}")
        crawled_count += 1
        print(f"[DEBUG] Crawled count: {crawled_count}")


# Worker task for concurrency
async def worker(playwright):
    while True:
        if PAGE_LIMIT is not None and crawled_count >= PAGE_LIMIT:
            print("[DEBUG] Page limit reached, worker exiting.")
            break
        if queue.empty():
            print("[DEBUG] Queue is empty, worker exiting.")
            break
        try:
            url = await queue.get()
            print(f"[DEBUG] Worker processing URL: {url}")
            await crawl(playwright, url)
            queue.task_done()
        except Exception as e:
            print(f"[ERROR] Worker error: {e}")

# Main function
async def scrape_website(start_url, page_limit=None):
    global PAGE_LIMIT
    if page_limit:
        PAGE_LIMIT = page_limit
    print(f"[DEBUG] Starting scrape with PAGE_LIMIT: {PAGE_LIMIT}")

    initialize_directories(start_url)
    clear_scraped_files(start_url)
    global rejected_log, crawled_log
    rejected_log, crawled_log = open_log_files(start_url)
    global BASE_DIRECTORY
    BASE_DIRECTORY = get_base_filename(start_url)
    print(f"[DEBUG] Base directory set to: {BASE_DIRECTORY}")
    await queue.put(start_url)
    print(f"[DEBUG] Start URL added to queue: {start_url}")

    async with async_playwright() as playwright:
        workers = [asyncio.create_task(worker(playwright)) for _ in range(4)]
        print(f"[DEBUG] {len(workers)} workers started.")
        await asyncio.gather(*workers)

    print("[DEBUG] Scraping completed.")

    global crawled_count
    crawled_count = 0
    rejected_log.close()
    crawled_log.close()
    visited.clear()
