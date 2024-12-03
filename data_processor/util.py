import os
  
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

def save_position_data(position, data, base_dir="shared_data/structured_data"):
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
            file.write(data)
        print(f"Data for '{position}' saved to {file_path}")
    except Exception as e:
        print(f"Error saving data for position {position}: {e}")