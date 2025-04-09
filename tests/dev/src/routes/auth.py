from flask import Blueprint, request, render_template, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from tests.dev.src.utils.postgresdatabaseconnection import PostgresDatabaseConnection
from tests.dev.src.utils.llm import LLMHelper



auth_bp = Blueprint("auth", __name__)
db = PostgresDatabaseConnection()
llm = LLMHelper()

@auth_bp.route("/", methods=["GET", "POST"])
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
        stored_hash = user_row[2]  # password

        if check_password_hash(stored_hash, password):
            session["user_id"] = user_row[0]   # idAppUser
            session["username"] = user_row[1]  # txUsername
            flash("Logged in!", "success")
            return redirect("/chat")
        else:
            flash("Incorrect password", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # 1. Check if username exists
        existing = db.read_sql_query("""
            SELECT * FROM chatbot_schema.app_user WHERE txusername = %s;
        """, (username,))
        if existing:
            flash("Username already exists.", "warning")
            return redirect("/")

        # 2. Insert new user
        hashed = generate_password_hash(password)
        db.execute_query("""
            INSERT INTO chatbot_schema.app_user (txusername, password)
            VALUES (%s, %s);
        """, (username, hashed))

        # 3. Get the new user_id
        user_result = db.read_sql_query("""
            SELECT idappuser FROM chatbot_schema.app_user
            WHERE txusername = %s;
        """, (username,))
        user_id = user_result[0][0] if user_result else None

        # 5. Insert initial chat
        if user_id:
            db.execute_query("""
                INSERT INTO chatbot_schema.chat (idappuser, txname, idllm)
                VALUES (%s, %s, %s);
            """, (user_id, 'Welcome Chat', llm.get_default_model_id()))

        flash("Account created. Please log in.", "success")
        return redirect("/")

    return render_template("register.html")



@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect("/")
