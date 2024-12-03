import os
from openai import OpenAI
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Directories
FILTERED_DIR = "./filtered"
OUTPUT_DIR = "./unstructured_data"

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
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
def process_file(file_path, model="gpt-4o-mini"):
    try:
        with open(file_path, "r") as file:
            content = file.read()

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
        print(f"Error processing file {file_path}: {e}")
        return None

# Process all files in the filtered directory
def process_all_files():
    for file_name in os.listdir(FILTERED_DIR):
        file_path = os.path.join(FILTERED_DIR, file_name)
        if os.path.isfile(file_path):
            print(f"Processing: {file_name}")
            extracted_data = process_file(file_path)

            if extracted_data:
                # Save unstructured data to the output directory
                output_file_path = os.path.join(OUTPUT_DIR, f"{file_name}_unstructured.txt")
                with open(output_file_path, "w") as output_file:
                    output_file.write(extracted_data)
                print(f"Saved unstructured data to {output_file_path}")
            else:
                print(f"Skipping: {file_name} due to errors.")

if __name__ == "__main__":
    # Process all files
    process_all_files()
