import json

from gemini_client import call_gemini

# Load FAQ data from disk
with open("faq_data.json") as f:
    FAQ_LIST = json.load(f)


# def find_faq(question: str) -> str:
#     q = question.lower()
#     for entry in FAQ_LIST:
#         if entry["question"].lower() in q:
#             return entry["answer"]
#     return None

def find_faq(user_msg: str) -> str:
    # Load FAQ data
    with open("faq_data.json", "r") as f:
        faq_data = json.load(f)

    # Build a numbered list of questions for Gemini
    questions = [faq["question"] for faq in faq_data]
    numbered_questions = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

    prompt = (
        "You are a helpful assistant. Given the user's question and a list of FAQs, "
        "choose the number of the FAQ that best matches the user's question. "
        "If none match, reply with 0.\n\n"
        f"User question: {user_msg}\n"
        f"FAQs:\n{numbered_questions}\n\n"
        "Reply with only the number of the best matching FAQ, or 0 if none match."
    )

    # Get Gemini's response
    out = call_gemini(prompt, max_tokens=5, temperature=0.0).strip()

    # Try to extract the number from Gemini's response
    try:
        idx = int(out)
        if 1 <= idx <= len(faq_data):
            return faq_data[idx - 1]["answer"]
    except Exception:
        pass

    return None