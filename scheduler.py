import schedule, time
from escalation import notify_human

STATS = {"chats": 0, "escalations": 0}

def daily_report():
    report = f"Daily Report: {STATS['chats']} chats, {STATS['escalations']} escalations."
    notify_human("SYSTEM", report)

def start():
    schedule.every().day.at("08:00").do(daily_report)
    while True:
        schedule.run_pending()
        time.sleep(60)
