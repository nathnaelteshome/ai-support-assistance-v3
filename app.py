from flask import Flask, request, session, jsonify
import threading

from nlu import get_intent_and_entities, generate_reply
from faq import find_faq
from orders_api import get_order, get_product
from escalation import analyze_sentiment, notify_human
from scheduler import start, STATS

app = Flask(__name__)
app.secret_key = "replace-with-your-secret"

# Launch scheduler
threading.Thread(target=start, daemon=True).start()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_msg   = data.get("message", "")
    session_id = session.get("id") or request.remote_addr
    session["id"] = session_id

    # Init session history
    history = session.get("history", [])
    STATS["chats"] += 1

    # 1) Full NLU via Gemini
    intel = get_intent_and_entities(user_msg)
    intent = intel.get("intent")

    assistant_reply = ""
    # 2) Route by intent 
    if intent == "FAQ":
        faq_ans = find_faq(user_msg)
        if faq_ans:
            assistant_reply = generate_reply(history, user_msg, knowledge=faq_ans)
        else:
            assistant_reply = generate_reply(history, user_msg)
    elif intent == "OrderStatus":
        oid = intel.get("order_id")
        if oid:
            order_data = get_order(int(oid))
            if order_data:
                # Summarize order data
                summary = f"Order {oid} – Status: {order_data['status']}, Total: ${order_data['total']}."
                assistant_reply = generate_reply(history, user_msg, knowledge=summary)
            else:
                assistant_reply = "I couldn’t find that order. Could you check the ID?"
        else:
            assistant_reply = "Sure – may I have your order ID please?"
    elif intent == "ProductInfo":
        pid = intel.get("product_id") or intel.get("product_name")
        if pid and pid.isdigit():
            prod = get_product(int(pid))
            if prod:
                info = f"{prod['title']} costs ${prod['price']}. {prod['description']}"
                assistant_reply = generate_reply(history, user_msg, knowledge=info)
            else:
                assistant_reply = "I couldn’t locate that product ID."
        else:
            assistant_reply = "Absolutely – which product ID or name?"
    elif intent == "Escalation":
        assistant_reply = "I’ll connect you to a human agent right away. Please hold."
        notify_human(session_id, user_msg)
        STATS["escalations"] += 1
    else:
        # Fallback small talk or unknown
        assistant_reply = generate_reply(history, user_msg)

    # 3) Sentiment-based escalation
    if analyze_sentiment(user_msg) == "negative" and intent != "Escalation":
        assistant_reply = "I’m sorry you’re upset—let me connect you to a human right now."
        notify_human(session_id, user_msg)
        STATS["escalations"] += 1

    # Update history
    history.append({"role": "user", "msg": user_msg})
    history.append({"role": "assistant", "msg": assistant_reply})
    session["history"] = history[-10:]  # keep last 10 turns

    return jsonify({"reply": assistant_reply})

if __name__ == "__main__":
    app.run(debug=True)
