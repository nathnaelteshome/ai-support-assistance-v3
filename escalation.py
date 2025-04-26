from textblob import TextBlob
import requests
from config import SLACK_WEBHOOK

def analyze_sentiment(msg: str) -> str:
    polarity = TextBlob(msg).sentiment.polarity
    return "negative" if polarity < 0 else "neutral" if polarity == 0 else "positive"

def notify_human(user_id: str, user_msg: str):
    text = f"*Escalation Alert* from `{user_id}`: {user_msg}"
    requests.post(SLACK_WEBHOOK, json={"text": text}, timeout=5)
