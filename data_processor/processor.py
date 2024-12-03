import os
from llmPrompts import use_llm_for_extraction, use_llm_for_position_data
from util import save_position_data_json, extract_content
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from dataTemplate import PositionDataTemplate

SHARED_DATA_DIR = "./../shared_data"
UNSTRUCTURED_DIR = f"{SHARED_DATA_DIR}/unstructured_data"
os.makedirs(UNSTRUCTURED_DIR, exist_ok=True)
POSITION_LIMIT_PER_FILE = 5

def process_text_with_llms(text, url, base_dir=f"{SHARED_DATA_DIR}/structured_data"):
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
        print(f"Processing data for: {position}")
        
        # Fetch position-specific data using LLM

        position_data = use_llm_for_position_data(position, text)
        try:
            position_data = PositionDataTemplate(**position_data)
            save_position_data_json(position, position_data, url, base_dir)
        except Exception as e:
            print(f"Error processing data for {position}: {e}")
            continue

# Example usage
if __name__ == "__main__":
  for file_name in os.listdir(UNSTRUCTURED_DIR):
    file_path = os.path.join(UNSTRUCTURED_DIR, file_name)
    with open(file_path, "r") as file:
      print(f"Processing file: {file_name}")
      url, input_text = extract_content(file_path)
      process_text_with_llms(input_text, url)
