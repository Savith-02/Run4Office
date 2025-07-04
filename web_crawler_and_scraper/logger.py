from utils import get_base_filename
# logger.py
# Global log file handles
rejected_log = None
crawled_log = None
timeout_log = None
# Open log files at the start


def open_log_files(start_url):
    base_directory = get_base_filename(start_url)
    global rejected_log, crawled_log, timeout_log
    rejected_log = open(f"./logs/{base_directory}/rejected_links.log",
                        "w", encoding="utf-8")  # Open in append mode
    crawled_log = open(f"./logs/{base_directory}/crawled_links.log",
                       "w", encoding="utf-8")    # Open in append mode
    timeout_log = open(f"./logs/{base_directory}/time_out_urls.log",
                       "w", encoding="utf-8")    # Open in append mode
    return rejected_log, crawled_log, timeout_log

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


def log_timeout(url):
    # Log the timeout URL to the file
    timeout_log.write(f"{url}\n")
    timeout_log.flush()  # Ensure the data is written immediately
