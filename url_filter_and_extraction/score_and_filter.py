import os
import shutil
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import argparse
from evaluate_relevance import evaluate_relevance
from utils import extract_content

# Directory paths
input_dir = "./formatted_files"
output_dir = "./filtered"
CUTOFF_SCORE = 6

# Ensure the filtered directory exists
os.makedirs(output_dir, exist_ok=True)

# Test a single file
def test_single_file(file_name):
    file_path = f"{input_dir}/{file_name}"
    print("\n", file_path)
    # Ensure it's a text file
    if os.path.isfile(file_path) and file_name.endswith('.txt'):
        url, content = extract_content(file_path)
        score = evaluate_relevance(content)

        # Append the score to the second line
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"{url}\n")
            file.write(f"Score: {score}\n")
            file.write(content)

        # Copy files with score > CUTOFF_SCORE to the filtered directory
        if score > CUTOFF_SCORE: 
            shutil.copy(file_path, output_dir)
        
        print(f"Processed file: {file_name} with score: {score}")
    else:
        print("File does not exist or is not a text file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process all files in the input directory.")
    parser.add_argument("--count", type=int, default=None, help="Number of files to process. If not specified, all files will be processed.")
    args = parser.parse_args()
    for file in os.listdir(input_dir)[:args.count] if args.count else os.listdir(input_dir):
        test_single_file(file)
