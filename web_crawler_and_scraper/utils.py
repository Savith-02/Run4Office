import os
from additional_cleaning import remove_whitespace_between_tags, remove_whitespace_between_tags_and_text

def get_base_filename(url):
    sanitized_url = url.replace("https://", "").replace("http://", "").replace("/", "_")
    return sanitized_url.rstrip("_")

def update_checkpoint_file(current_url, checkpoint_file='checkpoint.txt'):
    # Check if the checkpoint file exists
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r', encoding='utf-8') as file:
            first_line = file.readline().strip()
    else:
        first_line = None

    # Compare the first line with the current URL
    if first_line != current_url:
        # Empty the file and write the current URL
        with open(checkpoint_file, 'w', encoding='utf-8') as file:
            file.write(current_url + '\n')
        print(f"Checkpoint file updated. New URL: {current_url}")
    else:
        print("Checkpoint file is up-to-date. No changes made.")

def format_and_save_file(content, url, filename, output_directory):
    content = remove_whitespace_between_tags(content)
    content = remove_whitespace_between_tags_and_text(content)
    # os.makedirs(f"./../{output_directory}", exist_ok=True)
    filepath = f"./../url_filter/formatted_files/{output_directory}_{filename}.txt"
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write("URL: " + url + "\n\n")
        file.write(content)
