from typing import Set, Dict, Any
from urllib.parse import urlparse
import os
os.chdir("e:\\WORK\\langchains\\run4Office\\web_crawler_and_scraper")

def filter_urls(urls: Set[str], config: Dict[str, Any]) -> Set[str]:
    """
    Filters URLs based on a configuration object using urllib.parse for parsing.

    Parameters:
        urls (Set[str]): The set of URLs to filter.
        config (Dict[str, Any]): Configuration object containing filter criteria:
            - "exclude_domains" (Set[str]): Domains to exclude from URLs.
            - "include_domains" (Set[str], optional): Domains to include in URLs.
            - "exclude_paths" (Set[str], optional): Substrings in paths to exclude.
            - "include_paths" (Set[str], optional): Substrings in paths to include.
            - "schemes" (Set[str], optional): Allowed schemes (e.g., "https", "http").
            - "max_length" (int, optional): Maximum length of the URL.

    Returns:
        Set[str]: The filtered set of URLs.
    """
    exclude_domains = config.get("exclude_domains", set())
    include_domains = config.get("include_domains", set())
    exclude_paths = config.get("exclude_paths", set())
    include_paths = config.get("include_paths", set())
    schemes = config.get("schemes", {"http", "https"})
    max_length = config.get("max_length", None)

    filtered_urls = set()

    for url in urls:
        parsed_url = urlparse(url)

        # Check scheme
        if schemes and parsed_url.scheme not in schemes:
            with open("./urls/rejected_urls.txt", "a") as rejected_file:
                rejected_file.write(f"{url}\n")
            append_to_file(url, f"Skipping URL due to scheme {parsed_url.scheme} not in schemes")
            continue

        # Check domain (netloc)
        domain = parsed_url.netloc
        if domain in exclude_domains:
            append_to_file(url, f"Skipping URL due to domain {domain} in exclude_domains")
            continue
        if include_domains and domain not in include_domains:
            append_to_file(url, f"Skipping URL due to domain {domain} not in include_domains")
            continue

        # Check path
        path = parsed_url.path
        if any(exclude in path for exclude in exclude_paths):
            append_to_file(url, f"Skipping URL due to path {path} in exclude_paths")
            continue
        if include_paths and not any(include in path for include in include_paths):
            append_to_file(url, f"Skipping URL due to path {path} not in include_paths")
            continue

        # Check URL length
        if max_length and len(url) > max_length:
            append_to_file(url, f"Skipping URL due to length {len(url)} > max_length {max_length}")
            continue

        filtered_urls.add(url)

    return filtered_urls

def append_to_file(url: str, message: str):
    with open("./urls/rejected_urls.txt", "a", encoding="utf-8") as f:
        f.write(f"{url} - {message}\n")
