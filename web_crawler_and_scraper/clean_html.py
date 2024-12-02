from bs4 import Comment, Doctype
import re
from web_crawler_and_scraper.additional_cleaning import clean_unwanted_links, remove_empty_elements
# Main function to clean the soup
def clean_soup(soup):
    remove_unwanted_elements(soup)
    remove_doctype(soup)
    # remove_empty_elements(soup)  # Remove elements that are empty after cleaning

# Remove unwanted HTML elements and attributes
def remove_unwanted_elements(soup):
    remove_specific_tags(soup, ['head', 'script', 'style', 'br', 'svg', 'audio', 'video', 'picture', 'source', 'object', 'embed', 'applet', 'comment', 'img', 'noscript'])
    remove_attributes(soup, ['style', 'height', 'padding', 'width', 'align', 'valign'])
    remove_comments(soup)
    clean_unwanted_links(soup)
    remove_empty_elements(soup)
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

def remove_empty_elements(soup):
# Remove elements that are empty (contain no text or child tags)
    for element in soup.find_all(True):
        if not element.get_text(strip=True) and not element.find(True):
            element.decompose()

def strip_structure(soup):
    # def keep_text_and_links(tag):
    #     for child in list(tag.children)[::-1]:
    #         if isinstance(child, str):
    #             continue
    #         keep_text_and_links(child)
    #     if not isinstance(tag, str):
    #         if tag in soup.find_all(True):
    #             tag.unwrap()
    # keep_text_and_links(soup)
    # cleaned_html = str(soup)
    # cleaned_html = '\n'.join([line.strip() for line in cleaned_html.split('\n') if line.strip()])
    # return cleaned_html
    plain_text = str(soup)
    # plain_text = soup.get_text(separator='\n')  # Each block of text separated by a newline
    cleaned_text = '\n'.join([line.strip() for line in plain_text.splitlines() if line.strip()])
    
    return cleaned_text

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