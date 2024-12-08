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
        "You are an assistant tasked with extracting roles and positions mentioned in the provided text. "
        "Each extracted entry must strictly follow this format: "
        "'role: [local government position] of region: [county/municipality/township]'.\n"
        "If the entry does not fit this format, it should not be included.\n\n"
        "Examples of valid entries:\n"
        "- role: Mayor of region: Los Angeles\n"
        "- role: County Clerk of region: Cook County\n"
        "- role: Trustee of region: Plymouth Township\n\n"
        "Examples of invalid entries (to be ignored):\n"
        "- Mayor (missing region)\n"
        "- County Clerk Cook County (missing 'of region:')\n"
        "- Plymouth Township (missing role and 'of region:')\n\n"
        "Output the extracted positions as a comma-separated list, with no additional text or explanation."
    )
    
    user_prompt = f"Extract the roles and positions from the following text:\n\n{text}"
    try:
        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL_LARGE"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
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
    # Tool definition
    tools = [
        {
            "type": "function",
            "function": {
                "name": "extract_government_positions",
                "description": "Extract government position details from the provided text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "Position_title": {"type": "string", "description": "Title of the position."},
                        "Description": {"type": "string", "description": "Description of the position."},
                        "Next_election_date": {"type": "string", "format": "date", "description": f"Date of the next election. Only dates after {today_date} are relevant or if the date is not specified, leave it blank."},
                        "Filing_window_start": {"type": "string", "format": "date", "description": f"Start date of the filing window. Only dates after {today_date} are relevant or if the date is not specified, leave it blank."},
                        "Filing_window_end": {"type": "string", "format": "date", "description": f"End date of the filing window. Only dates after {today_date} are relevant or if the date is not specified, leave it blank."},
                        "Name_of_district": {"type": "string", "description": "Name of the district."},
                        "State_of_district": {"type": "string", "description": "State of the district."},
                        "Other_relevant_info": {"type": "string", "description": "Any other relevant information."},
                        "Vacancy_date": {"type": "string", "format": "date", "description": f"Date when the position will be vacant. Only dates after {today_date} are relevant or if the date is not specified, leave it blank."}
                    },
                    "additionalProperties": False
                }
            }
        }
    ]

    # System prompt with tool description
    system_prompt = (
        "You are a highly skilled data extraction specialist focused on government positions. "
        "Your task is to extract detailed and structured information from the provided text. "
        "Ensure that the extracted data adheres strictly to the specified parameter definitions and output format. "
        "The output must be in JSON format, precisely matching the tool's parameters. "
        "If certain fields lack relevant data, leave them blank. "
        "Avoid including any speculative or imaginary dates. "
        "Focus on accuracy and completeness, ensuring that all extracted information is relevant and correctly formatted."
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
            tools=tools,  # Pass tools definition
            tool_choice={"type": "function", "function": {"name": "extract_government_positions"}}  # Explicitly invoke the defined tool
        )

        # Parse response to extract JSON
        extracted_data = response.choices[0].message.tool_calls[0].function.arguments
        position_data_dict = json.loads(extracted_data)
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
