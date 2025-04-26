from flask import Blueprint, request, render_template, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from tests.dev.src.utils.postgresdatabaseconnection import PostgresDatabaseConnection
from tests.dev.src.utils.llm import LLMHelper
from tests.dev.src.utils.validator import Validator


auth_bp = Blueprint("auth", __name__)
db = PostgresDatabaseConnection()
llm = LLMHelper()

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("username")
        password = request.form.get("password")

        # Try to find user by username or email
        user = db.read_sql_query("""
            SELECT a.idappuser, a.txusername, a.password, r.txname AS role
            FROM chatbot_schema.app_user a
            JOIN chatbot_schema.user_role ur ON a.idappuser = ur.idappuser
            JOIN chatbot_schema.role r ON r.idrole = ur.idrole
            WHERE a.txusername = %s OR a.txemail = %s;
        """, (identifier, identifier))

        if not user:
            flash("User not found", "danger")
            return redirect("/")

        user_row = user[0] # idAppUser
        stored_hash = user_row[2]  # password   

        if check_password_hash(stored_hash, password):
            session["user_id"] = user_row[0]   # idAppUser
            session["username"] = user_row[1]  # txUsername
            session["role"] = user_row[3]  # 'Admin' or 'User'
            flash("Logged in!", "success")
            return redirect("/chat")
        else:
            flash("Incorrect password", "danger")

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        # 1. Validate inputs
        cleaned = Validator.check([
            (username, "Username", 50, True),
            (password, "Password", 100, True)
        ])
        if not cleaned:
            return redirect("/register")

        username, password = cleaned
        email = Validator.check_email(email)
        if not email or email == "Invalid email address.":
            return redirect("/register")        

        # 2. Check for duplicates
        existing_user = db.read_sql_query("""
            SELECT * FROM chatbot_schema.app_user WHERE txusername = %s;
        """, (username,))
        if existing_user:
            flash("Username already exists.", "warning")
            return redirect("/register")

        existing_email = db.read_sql_query("""
            SELECT * FROM chatbot_schema.app_user WHERE txemail = %s;
        """, (email,))
        if existing_email:
            flash("Email already registered.", "warning")
            return redirect("/register")        

        # 3. Register user
        hashed = generate_password_hash(password)
        db.execute_query("""
            INSERT INTO chatbot_schema.app_user (txusername, password, txemail)
            VALUES (%s, %s, %s);
        """, (username, hashed, email))

        # 4. Get the new user_id
        user_result = db.read_sql_query("""
            SELECT idappuser FROM chatbot_schema.app_user
            WHERE txusername = %s;
        """, (username,))
        user_id = user_result[0][0] if user_result else None
        
        if user_id:
            # 5. Assign default role            
            db.execute_query("""
                INSERT INTO chatbot_schema.user_role (idappuser, idrole)
                VALUES (%s, %s);
            """, (user_id, 2))

            # 6. Insert initial chat
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
