import os
import shutil

# Initialize the scraped files directory
def initialize_directories():
    os.makedirs("./logs", exist_ok=True)
    os.makedirs("./scraped_files", exist_ok=True)
    # Call this function during initialization if needed

def clear_scraped_files():
    folder = "./scraped_files"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove the file or link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove the directory
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


    