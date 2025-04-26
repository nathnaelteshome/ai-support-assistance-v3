from gemini_client import call_gemini
import json

# System-level instructions (persona and behavior)
SYSTEM_PROMPT = (
    "You are AcmeCorp's AI Customer Support Assistant. "
    "Be polite, clear, and helpful. "
    "If you need more information, ask for it politely."
)


def get_intent_and_entities(user_msg: str) -> dict:
    """
    Uses Gemini to classify intent and extract entities from the user's message.
    Expects a JSON response from the model.
    """
    prompt = (
        f"System: {SYSTEM_PROMPT}\n"
        f"User: {user_msg}\n"
        "Assistant: Determine intent and extract relevant entities as JSON. "
        "Possible intents: FAQ, OrderStatus, ProductInfo, Escalation, Other."
    )
    out = call_gemini(prompt, max_tokens=150, temperature=0.2)
    # --- Fix: Strip code fences if present ---
    if out.strip().startswith("```"):
        out = out.strip().strip("`")
        # Remove the first line (e.g., 'json') and the last line if it's a code fence
        lines = out.splitlines()
        # Remove the first line if it starts with 'json'
        if lines and lines[0].strip().lower().startswith("json"):
            lines = lines[1:]
        # Remove the last line if it's a code fence
        if lines and lines[-1].strip() == "":
            lines = lines[:-1]
        out = "\n".join(lines)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"intent": "Other", "order_id": None, "product_id": None}


def generate_reply(history: list, user_msg: str, knowledge: str = "") -> str:
    """
    Generates a reply via Gemini, given conversation history, user input, and optional factual knowledge.
    """
    # Build prompt with system + history + user
    system = f"System: {SYSTEM_PROMPT}"
    lines = [system]
    for turn in history[-6:]:
        role = "User" if turn["role"] == "user" else "Assistant"
        lines.append(f"{role}: {turn['msg']}")
    lines.append(f"User: {user_msg}")
    if knowledge:
        lines.append(f"Assistant: (Info: {knowledge})")
    lines.append("Assistant:")
    full_prompt = "\n".join(lines)
    return call_gemini(full_prompt, max_tokens=200, temperature=0.6)
