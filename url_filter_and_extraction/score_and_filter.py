import os
import shutil
from evaluate_relevance import evaluate_relevance
# Directory paths
input_dir = "./formatted_files"
output_dir = "./filtered"

# Ensure the filtered directory exists
os.makedirs(output_dir, exist_ok=True)

# Function to extract content excluding the URL
def extract_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        url = lines[0].strip()
        content = "".join(lines[1:]).strip()
    return url, content

def score_and_filter():
# Process all files in the input directory
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)

        # Ensure it's a text file
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            url, content = extract_content(file_path)
            score = evaluate_relevance(content)

            # Append the score to the second line
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(f"{url}\n")
                file.write(f"Score: {score}\n")
                file.write(content)

            # Copy files with score > 6 to the filtered directory
            if score > 6:
                shutil.copy(file_path, output_dir)

            print(f"Processed file: {filename} with score: {score}")
