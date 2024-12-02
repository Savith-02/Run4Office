# logger.py
# Global log file handles
rejected_log = None
crawled_log = None

# Open log files at the start
def open_log_files():
    global rejected_log, crawled_log
    rejected_log = open("./logs/rejected_links.log", "w", encoding="utf-8")  # Open in append mode
    crawled_log = open("./logs/crawled_links.log", "w", encoding="utf-8")    # Open in append mode
    return rejected_log, crawled_log

# Log rejected URLs with reasons
def log_rejection(url, reason):
    # Log the rejection to the file
    rejected_log.write(f"{url} - {reason}\n")
    rejected_log.flush()  # Ensure the data is written immediately

# Log crawled URLs
def log_crawled_link(url):
    # Log the crawled link to the file
    crawled_log.write(f"{url}\n")
    crawled_log.flush()  # Ensure the data is written immediately