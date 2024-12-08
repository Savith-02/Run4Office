import os
from openai import OpenAI
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import argparse
from dotenv import load_dotenv
load_dotenv()

from utils import extract_content

# Directories
FILTERED_DIR = "./filtered"
OUTPUT_DIR = "./../shared_data/unstructured_data"

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


# Create output directory if not exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define the prompt for unstructured data extraction
def generate_extraction_prompt(text):
    return f"""
    You are an expert in analyzing data related to U.S. local government elections and positions. 
    Extract all potentially relevant information from the following text, including:
    - Election dates (next election, filing windows).
    - Position titles and descriptions tied to counties, municipalities, and townships.
    - Any future-related updates that are useful.
    Provide the extracted information in an unstructured format as found in the text.
    Text:
    {text}
    """

# Function to process a single file
def process_file(content, model=os.getenv("GPT_MODEL_MINI")):
    try:
        # Create the extraction prompt
        prompt = generate_extraction_prompt(content)

        # Interact with the LLM
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.2
        )
        
        # Extract LLM response
        extracted_data = response.choices[0].message.content
        return extracted_data
    except Exception as e:
        print(f"Error processing file: {e}")
        return None

# Process all files in the filtered directory
def process_all_files(count=None):
    for file_name in os.listdir(FILTERED_DIR)[:count] if count else os.listdir(FILTERED_DIR):
        file_path = os.path.join(FILTERED_DIR, file_name)
        if os.path.isfile(file_path):
            url, content = extract_content(file_path)
            extracted_data = process_file(content)

            if extracted_data:
                # Save unstructured data to the output directory
                output_file_path = os.path.join(OUTPUT_DIR, f"{file_name}_unstructured.txt")
                with open(output_file_path, "w") as output_file:
                    output_file.write(f"{url}\n")
                    output_file.write(extracted_data)
                print(f"Saved unstructured data to {output_file_path}")
            else:
                print(f"Skipping: {file_name} due to errors.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process all files in the filtered directory.")
    parser.add_argument("--count", type=int, default=None, help="Number of files to process. If not specified, all files will be processed.")
    args = parser.parse_args()
    print(f"Processing {args.count if args.count else 'all'} files.")
    process_all_files(args.count)
