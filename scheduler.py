import schedule
import time
from escalation import notify_human

STATS = {"chats": 0, "escalations": 0}

def daily_report():
    text = f"Daily Report: {STATS['chats']} chats, {STATS['escalations']} escalations."
    notify_human("system", text)


def start_scheduler():
    schedule.every().day.at("08:00").do(daily_report)
    while True:
        schedule.run_pending()
        time.sleep(60)