from bs4 import Comment, Doctype
import re
# Main function to clean the soup
def clean_soup(soup):
       remove_doctype(soup)
       remove_comments(soup)
       remove_specific_tags(soup, ['head', 'script', 'style', 'br', 'svg', 'audio', 'video', 'picture', 'source', 'object', 'embed', 'applet', 'comment', 'img', 'noscript'])
       clean_unwanted_links(soup)
       remove_elements_by_class_pattern(soup, [r"^header", r"^footer", r"^hidden", r"^nav"])
       remove_elements_by_id_pattern(soup, [r"^header", r"^footer", r"^hidden", r"^nav"])
       remove_empty_elements(soup)
       remove_unwanted_attributes(soup, ['href', "type", "name"])

       # print("After remove_unwanted_attributes:", soup)
    # remove_attributes(soup, ['style', 'height', 'padding', 'width', 'align', 'valign'])
    # remove_empty_elements(soup)  # Remove elements that are empty after cleaning

def remove_empty_elements(soup):
    # Iterate over all elements in the soup
    for element in soup.find_all():
        # Check if the element is empty (no text and no children)
        if not element.get_text(strip=True) and not element.find_all():
            element.decompose()  # Remove the empty element
    return soup

def remove_specific_tags(soup, tags):
    # Remove specific tags and their contents
    for element in soup(tags):
        element.decompose()  # Removes element from HTML
    # Find and remove all elements with type="hidden"
    for hidden_input in soup.find_all('input', type='hidden'):
        hidden_input.decompose()  # Remove the element from the tree

def remove_attributes(soup, attributes):
    # Remove specified attributes from all tags
    for tag in soup.find_all(True):  # True will match all tags
        for attr in attributes:
            if tag.has_attr(attr):
                del tag[attr]  # Remove the attribute

def remove_comments(soup):
    # Remove comments from HTML
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

def remove_doctype(soup):
    doctype = soup.find(string=lambda text: isinstance(text, Doctype))
    if doctype:
        doctype.extract()

    # Remove XML declarations
    xml_declaration = soup.find(string=lambda text: text.strip().startswith("<?xml"))
    if xml_declaration:
        xml_declaration.extract()


def remove_elements_by_class_pattern(soup, class_patterns):
    compiled_patterns = [re.compile(pattern) for pattern in class_patterns]
    elements_to_remove = []  # Store elements to remove after checking

    # Find all elements with a class attribute
    for element in soup.find_all(class_=True):
        if element.get("class"):
            # Check if any compiled pattern matches any of the element's classes
            if any(pattern.search(class_name) for pattern in compiled_patterns for class_name in element.get("class", [])):
                elements_to_remove.append(element)

    # Remove all matching elements
    for element in elements_to_remove:
        element.decompose()
    
    return soup

def remove_elements_by_id_pattern(soup, id_patterns):
    compiled_patterns = [re.compile(pattern) for pattern in id_patterns]
    elements_to_remove = []  # Store elements to remove after checking

    # Find all elements with an id attribute
    for element in soup.find_all(id=True):
        if element.get("id"):
            if any(pattern.search(element.get("id")) for pattern in compiled_patterns):
                elements_to_remove.append(element)

    # Remove all matching elements
    for element in elements_to_remove:
        element.decompose()
    
    return soup

def remove_unwanted_attributes(soup, allowed_attributes):
    for tag in soup.find_all(True):  # Find all tags
        for attr in list(tag.attrs):  # Iterate over a copy of current attributes
            if attr not in allowed_attributes:  # Remove if not in allowed list
                del tag.attrs[attr]
    return soup

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