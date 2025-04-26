import json

with open("faq_data.json") as f:
    FAQ_LIST = json.load(f)

def find_faq(question: str) -> str:
    q_lower = question.lower()
    for entry in FAQ_LIST:
        if entry["question"].lower() in q_lower:
            return entry["answer"]
    return None
