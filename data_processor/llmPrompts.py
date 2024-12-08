from openai import OpenAI
import os
import json
from util import validate_extracted_positions
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)
today_date = datetime.now().strftime("%Y-%m-%d")
print(f"Today's date: {today_date}")
def use_llm_for_extraction(text):
    """
    Uses an LLM to extract positions from the text.
    Returns a list of positions.
    """
    system_prompt = (
        "You are an expert assistant tasked with extracting specific government roles and positions from the provided text. "
        "Your job is to extract entries that meet the following strict criteria:\n\n"
        "1. Each entry must represent a **specific government role** (e.g., Mayor, City Council Member, County Clerk).\n"
        "2. Each entry must specify the **region** it applies to, such as a county, municipality, or township. "
        "Use the format: 'role: [specific position] of region: [specific location]'.\n"
        "3. General terms such as 'elections,' 'voting,' or 'processes' are NOT roles and must be excluded.\n"
        "4. If the role or the region is missing or incomplete, do NOT include the entry.\n\n"
        "### Examples of Valid Entries:\n"
        "- role: Mayor of region: Los Angeles\n"
        "- role: County Clerk of region: Cook County\n"
        "- role: Trustee of region: Plymouth Township\n\n"
        "### Examples of Invalid Entries:\n"
        "- 'Municipal elections' (This is an event, not a role.)\n"
        "- 'Voting process of region: Cook County' (This is a process, not a role.)\n"
        "- 'Elections in Plymouth Township' (General term, not a role.)\n"
        "- 'Mayor' (Missing region.)\n\n"
        "### Output Format:\n"
        "Output all valid entries as a comma-separated list of strings, with no additional text or explanations. "
        "If no valid entries are found, return an empty string."
    )

    
    user_prompt = f"Extract the roles with their positions from the following text:\n\n{text}"
    try:
        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL_MINI"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        extracted_text = response.choices[0].message.content
        positions = [pos.strip() for pos in extracted_text.split(",") if pos.strip()]
        validated_positions = validate_extracted_positions(positions)
        return validated_positions
    except Exception as e:
        print(f"Error extracting positions: {e}")
        return []


def use_llm_for_position_data(position, text):
    """
    Uses an LLM to extract structured data in JSON format for a specific position using a tool definition. 
    Extracts information like position title, description, election dates, filing window, and other details.
    Returns only the relevant extracted information in JSON format.
    """

    # Define the system prompt with integrated parameter instructions
    system_prompt = (
        f"You are a highly skilled data extraction specialist focused on extracting structured and accurate information about government positions. "
        f"Your task is to extract the following detailed information from the provided text, ensuring that each field is accurate and complete:\n\n"
        f"1. **Position_title**: The official title of the position.\n"
        f"2. **Description**: A clear and concise description of the responsibilities or role of the position.\n"
        f"3. **Next_election_date**: The date of the next election. \n"
        f"    - Include only dates after {today_date}. \n"
        f"    - If the term end date of the current position holder is mentioned but no election date is explicitly provided, use this term end date as the next election date and prefix it with 'after'. \n"
        f"    - If no date is specified, leave this field blank.\n"
        f"4. **Filing_window_start**: The start date of the filing window for candidates.\n"
        f"    - Include only dates after {today_date}.\n"
        f"    - If no start date is mentioned, leave this field blank.\n"
        f"5. **Filing_window_end**: The end date of the filing window for candidates.\n"
        f"    - Include only dates after {today_date}.\n"
        f"    - If no end date is mentioned, leave this field blank.\n"
        f"6. **Name_of_district**: The name of the district the position belongs to.\n"
        f"7. **State_of_district**: The state where the district is located.\n"
        f"8. **Other_relevant_info**: Any additional relevant information about the position.\n"
        f"9. **Vacancy_date**: The date when the position will become vacant.\n"
        f"    - Include only dates after {today_date}.\n"
        f"    - If no vacancy date is mentioned, leave this field blank.\n\n"
        f"**Formatting Guidelines**:\n"
        f"- Ensure the output is strictly in JSON format, with each field adhering to the specifications above.\n"
        f"- For fields lacking relevant information in the text, leave them blank (e.g., \"Filing_window_start\": \"\").\n"
        f"- Do not include speculative or inferred data. Use only the information explicitly mentioned in the text.\n"
        f"- Ensure completeness and precision. Avoid adding any extra comments, explanations, or text outside the JSON structure.\n\n"
        f"Focus on accuracy, ensuring that all extracted information is relevant to the position and formatted correctly."
    )
    # User prompt
    user_prompt = f"Extract all relevant data for the following position: '{position}'.\n\nText: {text}"

    try:
        # LLM call
        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL_LARGE"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        # Parse response to extract JSON
        # Assuming the response is in JSON format
        extracted_data = response.choices[0].message.content
        # print(f"Extracted data: {extracted_data}")
        position_data_dict = json.loads(extracted_data.strip("```json").strip("```"))
        print(f"Extracted data for position {position}: {position_data_dict}")
        print(f"Extracted dates: {position_data_dict['Next_election_date'] if position_data_dict['Next_election_date'] else 'N/A'}, {position_data_dict['Filing_window_start'] if position_data_dict['Filing_window_start'] else 'N/A'}, {position_data_dict['Filing_window_end'] if position_data_dict['Filing_window_end'] else 'N/A'}, {position_data_dict['Vacancy_date'] if position_data_dict['Vacancy_date'] else 'N/A'}")
        # Validate response content
        if not position_data_dict:
            print(f"No data extracted for position: {position}. Skipping this position.")
            return None

        return position_data_dict
    except Exception as e:
        print(f"Error extracting data for position {position}: {e}")
        return None
