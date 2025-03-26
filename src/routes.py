from flask import request, jsonify, current_app
from src.models import db, Chat, Message

# No Flask() creation here anymore!

@current_app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    chat = Chat(user_id=1)  # 👈 placeholder until you have user mgmt
    db.session.add(chat)
    db.session.commit()

    message = Message(chat_id=chat.idchat, sender="user", content=user_message)
    db.session.add(message)
    db.session.commit()

    return jsonify({"chat_id": chat.idchat, "message": user_message})
