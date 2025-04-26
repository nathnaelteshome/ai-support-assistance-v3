from textblob import TextBlob
import requests
from config import SLACK_WEBHOOK


def analyze_sentiment(msg: str) -> str:
    polarity = TextBlob(msg).sentiment.polarity
    return "negative" if polarity < 0 else "neutral" if polarity == 0 else "positive"


def notify_human(message: str, user_id: str = "unknown"):
    if not SLACK_WEBHOOK:
        return
    payload = {"text": f"*Escalation:* Request for a human intervation was asked: {message}"}
    try:
        requests.post(SLACK_WEBHOOK, json=payload, timeout=5)
    except requests.RequestException:
        pass

  