import os

def get_base_filename(url):
    return url.replace("https://", "").replace("http://", "").replace("/", "_")

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