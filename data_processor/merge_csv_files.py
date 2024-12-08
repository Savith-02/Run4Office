import os
import pandas as pd
from openai import OpenAI
import json

# Configure OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Directory containing the CSV files
input_folder = "./shared_data/structured_data_csv"
output_file = "./shared_data/final_merged_data.csv"

# Prompt template for merging records
PROMPT_TEMPLATE = """
You are an assistant tasked with merging multiple records for the same government position. The goal is to merge the records into a single, high-quality record using the following rules:

1. Prefer precise data over approximate data (e.g., "23-Dec-24" is better than "after December 3, 2024").
2. If only approximate data is available, include it with "after" in the final record.
3. Ensure the final record includes only the best and most accurate data for each field.
4. Combine all URLs that contributed to the final record into a single field called 'urls'.
5. Remove unused URLs from the final record.
6. Provide the merged record in JSON format.

Fields to merge:
- Position_title
- Description
- Next_election_date
- Filing_window_start
- Filing_window_end
- Name_of_district
- State_of_district
- Other_relevant_info
- Vacancy_date
- urls (all contributing URLs)

Input records:
{records}

Output the final merged record as a JSON object. Do not include any additional text or explanations.
"""

# Function to process a single CSV file
def process_csv(file_path, output_file):
    print(f"Processing {file_path}...")
    df = pd.read_csv(file_path)

    # Group by Position_title
    grouped = df.groupby("Position_title")
    processed_records = []

    for position, group in grouped:
        records = group.to_dict(orient="records")
        # Prepare the prompt
        prompt = PROMPT_TEMPLATE.format(records=records)

        # Call OpenAI LLM
        try:
            response = client.chat.completions.create(
                model=os.getenv("GPT_MODEL_MINI"),
                messages=[
                    {"role": "system", "content": "You are an expert assistant."},
                    {"role": "user", "content": prompt},
                ],
            )
            merged_record = response.choices[0].message.content
            formatted_merged_record = merged_record.replace("```json", "").replace("```", "")
            processed_records.append(json.loads(formatted_merged_record))  # Convert JSON string to dict
        except Exception as e:
            print(f"Error processing position {position}: {e}")
            continue

    # Write the processed records to the output file immediately
    if processed_records:
        pd.DataFrame(processed_records).to_csv(output_file, mode='a', index=False, header=not os.path.exists(output_file))
        print(f"Processed records from {file_path} have been written to {output_file}.")

# Main function to process all CSVs in the folder
def process_all_csvs(input_folder, output_file):
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".csv"):
            file_path = os.path.join(input_folder, file_name)
            try:
                process_csv(file_path, output_file)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    print(f"All files processed. Final merged CSV saved to {output_file}")

# Run the script
if __name__ == "__main__":
    process_all_csvs(input_folder, output_file)
