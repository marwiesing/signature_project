from flask import Blueprint, request, render_template, redirect, session, flash, g
from ..utils.postgresdatabaseconnection import PostgresDatabaseConnection
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint("main", __name__)
db = PostgresDatabaseConnection()

@bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.read_sql_query("""
            SELECT * FROM chatbot_schema.app_user WHERE txusername = %s;
        """, (username,))

        if not user:
            flash("User not found", "danger")
            return redirect("/")

        user_row = user[0]
        stored_hash = user_row[2]  # password is 3rd column

        if check_password_hash(stored_hash, password):
            session["user_id"] = user_row[0]  # idAppUser
            session["username"] = user_row[1]  # txUsername
            flash("Logged in!", "success")
            return redirect("/chat")
        else:
            flash("Incorrect password", "danger")

    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        existing = db.read_sql_query("""
            SELECT * FROM chatbot_schema.app_user WHERE txusername = %s;
        """, (username,))
        if existing:
            flash("Username already exists.", "warning")
            return redirect("/")

        hashed = generate_password_hash(password)
        db.execute_query("""
            INSERT INTO chatbot_schema.app_user (txusername, password)
            VALUES (%s, %s);
        """, (username, hashed))

        flash("Account created. Please log in.", "success")
        return redirect("/")

    return render_template("register.html")


def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in", "danger")
            return redirect("/")
        g.user_id = session["user_id"]
        return f(*args, **kwargs)
    return wrapper


@bp.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    user_id = session["user_id"]

    if request.method == "POST":
        content = request.form.get("content")
        if content:
            # Insert new chat (minimum viable insert)
            db.execute_query("""
                INSERT INTO chatbot_schema.chat (idappuser, txname, idllm)
                VALUES (%s, %s, (SELECT idllm FROM chatbot_schema.llm WHERE txname = 'deepseek-r1'));
            """, (user_id, 'Untitled Chat'))

            # Get new chat ID
            chat_id_result = db.read_sql_query("""
                SELECT MAX(idchat) FROM chatbot_schema.chat WHERE idappuser = %s;
            """, (user_id,))
            chat_id = chat_id_result[0][0]

            # Insert user message
            db.execute_query("""
                INSERT INTO chatbot_schema.message (idchat, txcontent)
                VALUES (%s, %s);
            """, (chat_id, content))

        return redirect("/chat")

    messages_df = db.read_sql_query("""
        SELECT m.txContent, m.dtCreated 
        FROM chatbot_schema.message m
        JOIN chatbot_schema.chat c ON m.idchat = c.idchat
        WHERE c.idappuser = %s
        ORDER BY m.dtCreated DESC;
    """, (user_id,))

    return render_template("chat.html", messages=messages_df or [])


@bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect("/")
