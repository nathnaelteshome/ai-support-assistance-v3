import json
from gemini_client import call_gemini

# System prompt to guide the assistant’s persona & behavior
SYSTEM_PROMPT = """
You are AcmeCorp’s AI support assistant. 
Be friendly, polite, and helpful. Use full sentences.
If you need more info (like an order ID), ask politely.
"""

def get_intent_and_entities(user_msg: str) -> dict:
    prompt = (
        f"{SYSTEM_PROMPT}\n"
        f"User: {user_msg}\n"
        "Assistant: Determine intent and extract entities (JSON only)."
    )
    out = call_gemini(prompt, max_tokens=100, temperature=0.2)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {"intent": "Other", "order_id": None, "product_name": None}

def generate_reply(conversation: list, user_msg: str, knowledge: str = "") -> str:
    """
    conversation: list of dicts [{"role":"user"/"assistant","msg":...}, ...]
    knowledge: factual info string (FAQ answer, order data, etc.)
    """
    # Build prompt
    prompt_lines = [f"System: {SYSTEM_PROMPT}"]
    for turn in conversation[-6:]:  # keep last 6 turns
        role = "User" if turn["role"] == "user" else "Assistant"
        prompt_lines.append(f"{role}: {turn['msg']}")
    prompt_lines.append(f"User: {user_msg}")
    if knowledge:
        prompt_lines.append(f"Assistant: (Info: {knowledge})")
    prompt_lines.append("Assistant:")
    prompt = "\n".join(prompt_lines)
    return call_gemini(prompt, max_tokens=200, temperature=0.6)
