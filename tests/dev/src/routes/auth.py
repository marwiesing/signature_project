from flask import Blueprint, request, render_template, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from tests.dev.src.db.db_utils import PostgresDatabaseConnection

auth_bp = Blueprint("auth", __name__)
db = PostgresDatabaseConnection()

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.read_sql_query("""
            SELECT * FROM chatbot_schema.app_user WHERE username = %s;
        """, (username,))

        if not user:
            flash("User not found", "danger")
            return redirect("/")

        user_row = user[0]
        stored_hash = user_row[2]

        if check_password_hash(stored_hash, password):
            session["user_id"] = user_row[0]
            session["username"] = user_row[1]
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

        existing = db.read_sql_query("""
            SELECT * FROM chatbot_schema.app_user WHERE username = %s;
        """, (username,))
        if existing:
            flash("Username already exists.", "warning")
            return redirect("/")

        hashed = generate_password_hash(password)
        db.execute_query("""
            INSERT INTO chatbot_schema.app_user (username, password)
            VALUES (%s, %s);
        """, (username, hashed))

        flash("Account created. Please log in.", "success")
        return redirect("/")

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect("/")
