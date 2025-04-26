import requests
import json  # Import json for potential detailed error parsing if needed
from config import GEMINI_API_KEY


API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
MODEL_NAME = "gemini-1.5-pro-001"


def call_gemini(
    user_message: str,
    system_message: str = None,
    max_tokens: int = 200,
    temperature: float = 0.6,
) -> str:
    """
    Sends a prompt to Gemini via the Generative Language API and returns the generated text.
    """
    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        },
    }

    # Optionally include system instruction if provided (this part was correct)
    if system_message:
        payload["systemInstruction"] = {"parts": [{"text": system_message}]}
    # --- End of Corrected Payload Structure ---

    # Call the generateContent endpoint
    url = f"{API_URL}/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"

    try:
        resp = requests.post(
            url, headers=headers, json=payload, timeout=20
        )  # Increased timeout slightly

        if resp.status_code != 200:
            error_details = resp.text  # Default to raw text
            try:
                error_json = resp.json()
                error_details = json.dumps(error_json, indent=2)
            except json.JSONDecodeError:
                pass
            print(f">> Gemini API Error {resp.status_code}:\n{error_details}")
            resp.raise_for_status()  # Raise the exception after printing details

        data = resp.json()

        # Safely access the response parts
        # Check structure more robustly before accessing elements
        candidates = data.get("candidates")
        if candidates and isinstance(candidates, list) and len(candidates) > 0:
            first_candidate = candidates[0]
            content = first_candidate.get("content")
            if content and isinstance(content, dict):
                parts = content.get("parts")
                if parts and isinstance(parts, list) and len(parts) > 0:
                    first_part = parts[0]
                    text = first_part.get("text")
                    if text and isinstance(text, str):
                        return text

        print(f">> Unexpected API response structure: {json.dumps(data, indent=2)}")
        return "Error: Could not parse response from Gemini API."

    except requests.exceptions.RequestException as e:
        # Handle potential network errors, timeouts, etc.
        print(f">> Request failed: {e}")
        # Depending on your Flask app's error handling, you might want to
        # return an error message or raise a custom exception.
        return f"Error: Failed to connect to Gemini API - {e}"
    except Exception as e:
        # Catch other unexpected errors during the process
        print(f">> An unexpected error occurred: {e}")
        return "Error: An internal error occurred while processing the request."

