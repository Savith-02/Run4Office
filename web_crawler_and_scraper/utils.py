import os
from additional_cleaning import remove_whitespace_between_tags, remove_whitespace_between_tags_and_text

def get_base_filename(url):
    sanitized_url = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "_").replace("?", "_").replace("=", "_").replace("&", "_")
    return sanitized_url.rstrip("_")

def format_and_save_file(content, url, filename, output_directory):
    content = remove_whitespace_between_tags(content)
    content = remove_whitespace_between_tags_and_text(content)
    # os.makedirs(f"./../{output_directory}", exist_ok=True)
    filepath = f"./../url_filter_and_extraction/formatted_files/{output_directory}_{filename}.txt"
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write("URL: " + url + "\n\n")
        file.write(content)
