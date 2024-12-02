import os
import re
from bs4 import BeautifulSoup

# Function to replace repeating opening tags with a single tag
def replace_repeating_opening_tags(html):
    return re.sub(r'(<(\w+)>)(\s*<\2>)+', r'\1', html)

# Function to replace repeating closing tags with a single tag
def replace_repeating_closing_tags(html):
    return re.sub(r'(</(\w+)>)(\s*</\2>)+', r'\1', html)

# Function to remove elements containing only whitespace
def remove_empty_elements(html):
    soup = BeautifulSoup(html, 'html.parser')
    for element in soup.find_all():
        if not element.get_text(strip=True) and not element.find_all():
            element.decompose()
    return str(soup)

# Function to remove all spaces and newlines between element tags
def remove_whitespace_between_tags(html):
    return re.sub(r'>\s+<', '><', html)

# Function to remove href attributes from all <a> tags
def remove_href_from_a_tags(html):
    soup = BeautifulSoup(html, 'html.parser')
    for a_tag in soup.find_all('a', href=True):
        del a_tag['href']
    return str(soup)

# Function to process all files in the /scraped_files directory and save them to /formatted_files
input_directory = './web_crawler_and_scraper/scraped_files'
output_directory = './web_crawler_and_scraper/formatted_files'

def process_files_in_directory():
    print("Formatting files started")
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(input_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        input_file_path = os.path.join(input_directory, filename)
        
        if os.path.isfile(input_file_path):
            with open(input_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Apply the tag replacement and whitespace removal functions
            content = replace_repeating_opening_tags(content)
            content = replace_repeating_closing_tags(content)
            content = remove_empty_elements(content)
            content = remove_whitespace_between_tags(content)
            content = remove_href_from_a_tags(content)
            
            output_file_path = os.path.join(output_directory, filename)
            
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
