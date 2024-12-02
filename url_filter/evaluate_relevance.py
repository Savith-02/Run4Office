from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def evaluate_relevance(content):
    """
    Sends the content to the LLM for relevance evaluation based on timeliness and presence of specific details.
    Returns a confidence score (0 to 10) based on relevance to U.S. local government elections.
    Retries up to 3 times if the response is not valid.
    """
    attempt = 0
    while attempt < 1:
        try:
            # Example of LLM API call (adjust as per your setup)
            print("Evaluating relevance of content")
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Replace with your LLM model name
                messages=[
                    {"role": "system", "content": (
                        "You are an expert in analyzing content related to U.S. local government elections. "
                        "Your task is to evaluate whether the provided text contains relevant and timely information about:\n"
                        "1. Next election dates.\n"
                        "2. Filing window start and end dates.\n"
                        "3. Details tied to any U.S. local government positions (e.g., counties, municipalities, or townships).\n\n"
                        "Relevance and Timeliness Instructions:\n"
                        "- The information must be future-related and not outdated.\n"
                        "- Assign higher scores to content with clear and unambiguous future election data.\n"
                        "- Assign lower scores if the information is outdated or vague.\n\n"
                        "Scoring Guidelines:\n"
                        "- 0: No relevant or timely info.\n"
                        "- 1-4: Limited or partially relevant information.\n"
                        "- 5-7: Moderately relevant and timely info.\n"
                        "- 8-10: Highly relevant, clear, and updated info.\n"
                        "Respond with **only** the numeric score (0 to 10)."
                    )},
                    {"role": "user", "content": content}
                ]
            )

            # Parse the response
            score = response.choices[0].message.content.strip()
            score = float(score)
            print(f"Score: {score}")
            # Ensure score is within range
            if 0 <= score <= 10:
                return score
            else:
                raise ValueError(f"Score out of range: {score}")
        except (ValueError, KeyError, Exception) as e:
            print(f"Attempt {attempt + 1}: Error parsing response - {e}")
            attempt += 1

    # Return 0 if all attempts fail
    print("Failed to get a valid score after 3 attempts. Returning 0.")
    return 0
