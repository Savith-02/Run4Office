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

def save_position_data_json(position, data, url, base_dir=f"{SHARED_DATA_DIR}/structured_data"):
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
            data_dict["url"] = url
            file.write(json.dumps(data_dict, indent=4))
        print(f"Data for '{position}' saved to {file_path}")
    except Exception as e:
        print(f"Error saving data for position {position}: {e}")

import csv
import os
from typing import List

def save_position_data_csv(position: str, data, url: str, csv_file_path: str = "positions_data.csv"):
    # Define the CSV headers
    headers = [
        "Position_title", "Description", "Next_election_date", "Filing_window_start",
        "Filing_window_end", "Name_of_district", "State_of_district", "Other_relevant_info", "url"
    ]
    
    # Convert Pydantic data to a dictionary
    try:
        data_dict = data.model_dump()
        data_dict["url"] = url
    except AttributeError:
        print(f"Invalid data format for position '{position}'.")
        return

    # Read existing data
    records = []
    position_exists = False
    if os.path.exists(csv_file_path):
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                # If position exists, update its data
                if row["Position_title"] == data_dict["Position_title"]:
                    row.update(data_dict)
                    position_exists = True
                records.append(row)

    # If position doesn't exist, add it
    if not position_exists:
        records.append(data_dict)
    
    # Write updated data back to the CSV
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"Data for '{position}' has been {'updated' if position_exists else 'added'} in {csv_file_path}")

def extract_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        url = lines[0].strip()
        content = "".join(lines[1:]).strip()
    return url, content