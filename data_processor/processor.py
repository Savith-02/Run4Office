import os
from llmPrompts import use_llm_for_extraction, use_llm_for_position_data
from util import save_position_data_json, extract_content,save_position_data_csv
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from dataTemplate import PositionDataTemplate
import argparse

SHARED_DATA_DIR = "./../shared_data"
UNSTRUCTURED_DIR = f"{SHARED_DATA_DIR}/unstructured_data"
POSITION_LIMIT_PER_FILE = 20
os.makedirs(UNSTRUCTURED_DIR, exist_ok=True)

def process_text_with_llms(text, url):
    """
    Main function to process the input text:
    - Uses LLM to extract positions
    - Uses LLM to fetch and save data for each position
    """
    # Extract positions using LLM
    positions = use_llm_for_extraction(text)
    if not positions:
        print("No roles extracted. Ensure the text contains relevant role information.")
        return
    print(f"Extracted positions: {', '.join(positions)}")
    for position in positions[:POSITION_LIMIT_PER_FILE]:
        # print(f"Processing data for: {position}")
        # Fetch position-specific data using LLM
        try:
            print(f"\nProcessing data for: {position}")
            position_data = use_llm_for_position_data(position, text)
            if position_data is None:
                print(f"Error: No data extracted for position {position}.")
                continue      

            position_data = PositionDataTemplate(**position_data)
            save_position_data_json(position, position_data, url)
            save_position_data_csv(position, position_data, url)
        except Exception as e:
            print(f"\nError processing data for {position}: {e}\n")
            continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process all files in the unstructured data directory.")
    parser.add_argument("--count", type=int, default=None, help="Number of files to process. If not specified, all files will be processed.")
    args = parser.parse_args()
    print(f"Processing {args.count if args.count else 'all'} files.")

    for file_name in os.listdir(UNSTRUCTURED_DIR)[:args.count] if args.count else os.listdir(UNSTRUCTURED_DIR):
        file_path = os.path.join(UNSTRUCTURED_DIR, file_name)
        with open(file_path, "r") as file:
            print(f"\nProcessing file: {file_name}")
            url, input_text = extract_content(file_path)
            process_text_with_llms(input_text, url)