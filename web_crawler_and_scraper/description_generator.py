import os
import json
import re
import openai
from openai import OpenAI

# Set your OpenAI API key
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def generate_description(content):
    system_prompt = """
    Extract the following from the web page:
    1. An appropriate title for the page based on its content.
    2. A list of actions or services a user can perform on the page, including:
    - Any forms the user can fill out and their purpose.
    - Any data processing details or steps mentioned.
    - Any options the user can select.

    Output in the following JSON format:
    {
        "title": "Appropriate Title Here",
        "actions": ["Action 1", "Action 2", ...]
        ]
    }
    """
    
    # Send the content to the OpenAI API to generate a summary
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Use the gpt-4o-mini model
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": system_prompt + content}
                ],
            }
        ],
    )

    # Extract and return the generated description from the response
    return response.choices[0].message.content.strip('```json\n').strip('```')

def extract_url(content):
    # Extract the URL from the content (assumes URL is present in the content text)
    match = re.search(r'https?://[^\s]+', content)
    if match:
        return match.group(0)
    return None

# Directory path with .txt files
directory = "./web_crawler_and_scraper/formatted_files"
checkpoint_file = "checkpoint.txt"
description_directory = "./vector_db/descriptions"

def generate_descriptions():
    print("Generating descriptions...")
    if not os.path.exists(description_directory):
        os.makedirs(description_directory)
    
    # Load last processed file from checkpoint
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            lines = f.readlines()
            if len(lines) > 1:
                last_processed = lines[1].strip()  # Read from the second line
            else:
                last_processed = None
    else:
        last_processed = None

    # Optional: Set an upper limit on the number of files to process
    max_files_to_process = 5
    files_processed = 0

    # Process files, starting from the checkpoint
    resume_processing = last_processed is None
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".txt"):
            print(f"Generating description for {filename}")
            # Check if processing should resume and limit files if max is set
            if resume_processing or filename == last_processed:
                resume_processing = True
                file_path = os.path.join(directory, filename)

                # Read file content
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                try:
                    # Extract URL from the content
                    url = extract_url(content)
                    if not url:
                        print(f"URL not found in {filename}. Skipping...")
                        continue

                    # Generate description using the OpenAI API
                    description = generate_description(content)
                    print(description)
                    # Create a dictionary to save as JSON
                    result = {
                        "link": url,
                        "description": description
                    }
                    
                    # Save the result to a new file with the same name
                    new_filename = os.path.splitext(filename)[0] + "_description.json"
                    new_filepath = os.path.join(description_directory, new_filename)
                    
                    with open(new_filepath, 'w', encoding='utf-8') as json_file:
                        json.dump(result, json_file, ensure_ascii=False, indent=4)
                    
                    print(f"Description for {filename} saved as {new_filename}\n")
                    
                    # Update checkpoint after successful processing
                    with open(checkpoint_file, "r") as f:
                        lines = f.readlines()
                    if len(lines) > 1:
                        lines[1] = f"{filename}\n"
                    else:
                        lines.append(f"{filename}\n")
                    with open(checkpoint_file, "w") as f:
                        f.writelines(lines)
                        
                    files_processed += 1
                    if files_processed >= max_files_to_process:
                        print("Reached the maximum file processing limit.")
                        break
                
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    break