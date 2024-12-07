import os
from tavily import TavilyClient
from openai import OpenAI
import dotenv
dotenv.load_dotenv()

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def filter_relevant_urls(urls: list[str]):
    """
    Filter a list of URLs by determining their relevance to U.S. elections and related information.
    
    Args:
        urls (list[str]): List of URLs to filter.
        
    Returns:
        list[str]: Filtered list of relevant URLs.
    """
    filtered_urls = []
    for url in urls:
        try:
            description = get_url_description(url)
            if description and is_relevant(url, description):
                filtered_urls.append(url)
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
    return filtered_urls


def get_url_description(url: str):
    """
    Retrieve a description of the content for a given URL using Tavily's search API.
    Args:
        url (str): The URL to describe.

    Returns:
        str: Description of the URL content, or None if not available.
    """
    query = f"Give me a brief description of {url}"
    print("\ngetting description for ", url)
    response = tavily_client.search(query=query, include_answer=True, include_images=False, max_results=1)
    
    # Ensure response has the expected structure
    if response and "results" in response and response["results"]:
        print("description: ", response.get("answer", ""))
        return response.get("answer", "")
    return None


def is_relevant(url: str, description: str):
    """
    Use OpenAI to determine if a URL and its description contain relevant information.
    
    Args:
        url (str): The URL being checked.
        description (str): The description of the URL's content.
        
    Returns:
        bool: True if the URL is relevant, False otherwise.
    """
    prompt = (
        f"Determine if the following URL and its description are relevant to the topics of U.S. elections, "
        f"candidate profiles, ballot measures, election dates, or public office requirements:\n\n"
        f"URL: {url}\n"
        f"Description: {description}\n\n"
        f"Answer 'Yes' or 'No'."
    )
    
    try:
        print("checking relevance for ", url)
        response = openai_client.chat.completions.create(
            model=os.getenv("GPT_MODEL_MINI"),
            messages=[{"role": "system", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        answer = response.choices[0].message.content.strip().lower()
        print("answer: ", answer)
        return answer == "yes"
    except Exception as e:
        print(f"Error checking relevance for URL {url}: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    test_urls = [
        "https://sosmt.gov/elections/filing/",
        "https://www.elections.alaska.gov/candidates/",
        "https://example.com/unrelated-content",
    ]
    
    relevant_urls = filter_relevant_urls(test_urls)
    print("\nRelevant URLs:")
    for url in relevant_urls:
        print(url)
