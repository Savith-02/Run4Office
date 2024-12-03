import os
import json

SHARED_DATA_DIR = "./../shared_data"

def validate_extracted_positions(positions):
    """
    Validates the extracted positions list to ensure it contains valid role names.
    """
    if not positions:
        raise ValueError("No roles were extracted from the text. Ensure the text contains role information.")
    for pos in positions:
        if not isinstance(pos, str) or len(pos.strip()) == 0:
            raise ValueError(f"Invalid role detected: {pos}. Ensure roles are properly formatted.")
    return positions

def save_position_data_json(position, data, url, base_dir=f"{SHARED_DATA_DIR}/structured_data_json"):
    """
    Saves data for a specific position into its corresponding directory and file.
    Creates a directory if it doesn't already exist.
    """
    # Create a safe folder name for the position
    folder_name = position.replace(" ", "_").replace(",", "")
    folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    # Create a unique file name if needed
    file_index = 1
    while os.path.exists(os.path.join(folder_path, f"data_{file_index}.txt")):
        file_index += 1
    file_path = os.path.join(folder_path, f"data_{file_index}.txt")
    
    try:
        # Save data to the file
        with open(file_path, "w") as file:
            data_dict = data.model_dump()
            data_dict["url"] = url.split(": ")[1]
            file.write(json.dumps(data_dict, indent=4))
        print(f"Data for '{position}' saved to {file_path}")
    except Exception as e:
        print(f"Error saving data for position {position}: {e}")

import csv
from typing import Dict

def save_position_data_csv(position: str, data: Dict, url: str, base_dir: str = f"{SHARED_DATA_DIR}/structured_data_csv"):
    """
    Saves data for a specific position into its corresponding CSV file.
    Creates a directory and CSV file if they don't already exist.
    If the position CSV exists, appends new records to it.
    """
    # Create a safe folder name for the position
    os.makedirs(base_dir, exist_ok=True)
    folder_name = position.replace(" ", "_").replace(",", "")

    # Define the path for the CSV file
    csv_file_path = os.path.join(base_dir, f"{folder_name}.csv")

    # Convert the data into a dictionary and add the URL
    data_dict = data.model_dump() if hasattr(data, "model_dump") else data
    data_dict["url"] = url.split(": ")[1]

    # Define the header based on the keys in the data dictionary
    headers = list(data_dict.keys())

    # Check if the CSV file exists and write data accordingly
    file_exists = os.path.isfile(csv_file_path)
    try:
        with open(csv_file_path, mode="a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            
            # Write the header only if the file doesn't already exist
            if not file_exists:
                writer.writeheader()
            
            # Write the data row
            writer.writerow(data_dict)
        
        print(f"Data for '{position}' saved to {csv_file_path}")
    except Exception as e:
        print(f"Error saving data for position '{position}' in CSV: {e}")


def extract_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        url = lines[0].strip()
        content = "".join(lines[1:]).strip()
    return url, content