import requests
from config import GEMINI_API_KEY

# Google Generative Language API base (v1beta)
API_URL = "https://generativelanguage.googleapis.com/v1beta"
# Recommended model for customer support
MODEL_NAME = "models/gemini-1.5-pro-001"


def call_gemini(user_message: str, system_message: str = None,
                max_tokens: int = 200, temperature: float = 0.6) -> str:
    """
    Sends a prompt to Gemini via the Generative Language API and returns the generated text.
    """
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": user_message}]}  # user input
        ]
    }
    if system_message:
        payload["systemInstruction"] = {
            "role": "system",
            "parts": [{"text": system_message}]
        }
    url = f"{API_URL}/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    # Extract the first candidate's content
    return data["candidates"][0]["content"]
