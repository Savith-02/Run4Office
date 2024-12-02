import re

def clean_unwanted_links(soup):
    """
    Remove <a> tags containing unwanted links such as 'Turn off more accessible mode', 'Turn on Animations', etc.
    """
    # Define unwanted link texts or patterns
    unwanted_texts = [
        "Turn off more accessible mode",
        "Turn on Animations",
        "Turn off Animations",
        "Skip Ribbon Commands",
        "Skip to main content",
        "Turn on more accessible mode",
        "Skip to main content"
    ]
    
    unwanted_hrefs = [
        "javascript",  # Match hrefs starting with 'javascript:'
        "#"
    ]

    # Remove <a> tags that match unwanted text or hrefs
    for a_tag in soup.find_all("a"):
        if any(text in a_tag.get_text() for text in unwanted_texts):
            a_tag.decompose()  # Remove the tag
        elif any(a_tag.get("href", "").startswith(href) for href in unwanted_hrefs):
            a_tag.decompose()  # Remove the tag

    return soup

def remove_empty_elements(soup):
    # Iterate over all elements in the soup
    for element in soup.find_all():
        # Check if the element is empty (no text and no children)
        if not element.get_text(strip=True) and not element.find_all():
            element.decompose()  # Remove the empty element
    return soup

# Function to replace repeating opening tags with a single tag
def replace_repeating_opening_tags(html):
    # This will match consecutive opening tags of the same type and replace with a single tag
    return re.sub(r'(<(\w+)>)(\s*<\2>)+', r'\1', html)

# Function to replace repeating closing tags with a single tag
def replace_repeating_closing_tags(html):
    # This will match consecutive closing tags of the same type and replace with a single closing tag
    return re.sub(r'(</(\w+)>)(\s*</\2>)+', r'\1', html)