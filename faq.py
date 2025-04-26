import json

# Load FAQ data from disk
with open("faq_data.json") as f:
    FAQ_LIST = json.load(f)


def find_faq(question: str) -> str:
    q = question.lower()
    for entry in FAQ_LIST:
        if entry["question"].lower() in q:
            return entry["answer"]
    return None