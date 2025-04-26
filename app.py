from flask import Flask, request, session, jsonify
import threading

from nlu import get_intent_and_entities, generate_reply
from faq import find_faq
from orders_api import get_order, get_product
from escalation import analyze_sentiment, notify_human
from scheduler import start_scheduler, STATS

app = Flask(__name__)
app.secret_key = "replace-with-secure-key"

# Start scheduler in background
threading.Thread(target=start_scheduler, daemon=True).start()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "No message provided."}), 400

    history = session.get("history", [])
    STATS["chats"] += 1

    # 1) NLU classification
    intel = get_intent_and_entities(user_msg)
    intent = intel.get("intent")

    reply = None
    # 2) Handle intents
    if intent == "FAQ":
        answer = find_faq(user_msg)
        if answer:
            reply = generate_reply(history, user_msg, knowledge=answer)
        else:
            reply = generate_reply(history, user_msg)

    elif intent == "OrderStatus":
        entities = intel.get("entities")
        oid = entities.get("order_id")

        if oid:
            order = get_order(int(oid))
            if order:
                summary = f"Order {oid}: Status {order['status']}, total ${order['total']}."
                reply = generate_reply(history, user_msg, knowledge=summary)
            else:
                reply = "Sorry, I couldn't find that order. Could you check the ID?"
        else:
            reply = "Sure—could you please provide your order ID?"

    elif intent == "ProductInfo":
        pid = intel.get("product_id")
        if pid:
            prod = get_product(int(pid))
            if prod:
                info = f"{prod['title']} costs ${prod['price']}. {prod['description']}"
                reply = generate_reply(history, user_msg, knowledge=info)
            else:
                reply = "I couldn't find that product. Could you check the product ID?"
        else:
            reply = "Which product ID would you like info on?"

    elif intent == "Escalation":
        reply = "I’m connecting you to a human agent now. Please hold."
        notify_human(user_msg)
        STATS['escalations'] += 1

    else:
        # Fallback: small talk or unknown
        reply = generate_reply(history, user_msg)

    # Sentiment-based escalation
    if analyze_sentiment(user_msg) == "negative" and intent != "Escalation":
        reply = "I'm sorry you're upset—I'll get a human to help you right away."
        notify_human(user_msg)
        STATS['escalations'] += 1

    # Update session history (keep last 10 turns)
    history.append({"role": "user", "msg": user_msg})
    history.append({"role": "assistant", "msg": reply})
    session["history"] = history[-10:]

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
