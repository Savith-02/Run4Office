from openai import OpenAI
import os
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
        "You are an assistant tasked with extracting complete roles and positions mentioned in the following text. "
        "Only list entries where both a role and a specific position are present, and ignore any incomplete entries. "
        "Ensure that each entry includes a clear role and its corresponding position, such as a city, county, or municipality. "
        "Please provide the results in a comma-separated format without additional context or explanation. "
        "For example: 'Mayor of Los Angeles, County Clerk of Cook County, Trustee of Plymouth Township'."
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
    Uses an LLM to extract data for a specific position.
    """
    system_prompt = (
        "You are an expert in gathering detailed, role-specific data from textual content. "
        "Your task is to extract all relevant information about the given role from the provided text. "
        "Please ensure you capture the most up-to-date and relevant information, including election dates, filing deadlines, "
        "or any key responsibilities or events related to the role."
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
        return position_data
    except Exception as e:
        print(f"Error extracting data for position {position}: {e}")
        return None