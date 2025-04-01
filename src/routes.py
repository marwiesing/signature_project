from flask import Blueprint, request, render_template, redirect
from src.models import db, Message, Chat

bp = Blueprint("main", __name__)

@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("content")
        if content:
            chat = Chat(user_id=1)
            db.session.add(chat)
            db.session.flush()  # Get the ID without committing yet

            # Now insert the message using the real chat ID
            message = Message(chat_id=chat.idchat, sender="user", content=content)
            db.session.add(message)
            db.session.commit()
        return redirect("/")

    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template("index.html", messages=messages)
