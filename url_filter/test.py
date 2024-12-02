import os
import shutil
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from evaluate_relevance import evaluate_relevance
from score_and_filter import extract_content

# Directory paths
input_dir = "./formatted_files"
output_dir = "./filtered"

# Ensure the filtered directory exists
os.makedirs(output_dir, exist_ok=True)

# Test a single file
def test_single_file(file_name):
    file_path = f"{input_dir}/{file_name}"
    print(file_path)
    # Ensure it's a text file
    if os.path.isfile(file_path) and file_name.endswith('.txt'):
        url, content = extract_content(file_path)
        score = evaluate_relevance(content)

        # Append the score to the second line
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"URL: {url}\n")
            file.write(f"Score: {score}\n")
            file.write(content)

        # Copy files with score > 6 to the filtered directory
        if score > 6:
            shutil.copy(file_path, output_dir)
        
        print(f"Processed file: {file_name} with score: {score}")
    else:
        print("File does not exist or is not a text file.")

for file in os.listdir(input_dir):
    test_single_file(file)
    # break
