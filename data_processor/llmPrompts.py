from openai import OpenAI
import os
import json
from util import validate_extracted_positions

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

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
            model="gpt-4",
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
    Uses an LLM to extract structured data in JSON format for a specific position, 
    including position title, description, election dates, filing window, and other 
    relevant information. Returns only the relevant extracted information in JSON format.
    """
    system_prompt = (
        "You are an expert in gathering detailed, structured data from political positions. "
        "Your task is to extract only the relevant data from the provided text about the given position. "
        "Return the output strictly in JSON format without any additional descriptions, comments, or text. "
        "The fields to be extracted and returned in JSON format are as follows:\n"
        '{"Position_title": "Position title", '
        '"Description": "Description of the position", '
        '"Next_election_date": "Date of next election", '
        '"Filing_window_end": "End date of the filing window", '
        '"Filing_window_start": "Start date of the filing window", '
        '"Name_of_district": "District name", '
        '"State_of_district": "State of the district", '
        '"Other_relevant_info": "Other relevant information"}\n'
        "Do not include any other information or descriptions other than what is specified above. Only the extracted data should be returned in strict JSON format."
    )

    user_prompt = f"Extract all relevant data regarding the following position: '{position}'.\n\nText: {text}"

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        position_data = response.choices[0].message.content
        
        if not position_data or len(position_data.strip()) == 0:
            print(f"No data extracted for position: {position}. Skipping this position.")
            return None
        position_data_dict = json.loads(position_data)
        print(f"Extracted data for position {position}: {position_data_dict}")
        return position_data_dict
    except Exception as e:
        print(f"Error extracting data for position {position}: {e}")
        return None