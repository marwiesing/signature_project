from flask import Blueprint, request, render_template, redirect, session, flash, g
from tests.dev.src.db.db_utils import PostgresDatabaseConnection

chat_bp = Blueprint("chat", __name__)
db = PostgresDatabaseConnection()

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

@chat_bp.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    user_id = session["user_id"]
    chat_id = session.get("chat_id")

    # Create chat if none exists
    if not chat_id:
        result = db.read_sql_query("""
            SELECT idchat FROM chatbot_schema.chat 
            WHERE user_id = %s ORDER BY created_at DESC LIMIT 1;
        """, (user_id,))
        if result:
            chat_id = result[0][0]
        else:
            db.execute_query("INSERT INTO chatbot_schema.chat (user_id) VALUES (%s);", (user_id,))
            result = db.read_sql_query("""
                SELECT idchat FROM chatbot_schema.chat 
                WHERE user_id = %s ORDER BY created_at DESC LIMIT 1;
            """, (user_id,))
            chat_id = result[0][0]
        session["chat_id"] = chat_id

    # Handle new message submission
    if request.method == "POST":
        content = request.form.get("content")
        selected_project_id = request.form.get("project_id") or None
        project_id = int(selected_project_id) if selected_project_id else None

        # Update chat with selected project if not already set
        db.execute_query("""
            UPDATE chatbot_schema.chat SET project_id = %s WHERE idchat = %s;
        """, (project_id, chat_id))

        if content:
            db.execute_query("""
                INSERT INTO chatbot_schema.message (chat_id, content)
                VALUES (%s, %s);
            """, (chat_id, content))

        session["selected_project_id"] = project_id
        return redirect("/chat")

    # Load messages
    rows = db.read_sql_query("""
        SELECT content, timestamp FROM chatbot_schema.message
        WHERE chat_id = %s ORDER BY timestamp;
    """, (chat_id,))
    messages = [{"content": row[0], "timestamp": row[1]} for row in rows] if rows is not None else []

    # Load current chat name
    chat_name_result = db.read_sql_query("SELECT name FROM chatbot_schema.chat WHERE idchat = %s;", (chat_id,))
    chat_name = chat_name_result[0][0] if chat_name_result else None

    # Load project list
    projects_df = db.read_sql_query("""
        SELECT idproject, name FROM chatbot_schema.project ORDER BY created_at DESC;
    """)
    projects = projects_df.to_dict(orient="records") if projects_df is not None else []

    return render_template("chat.html",
        messages=messages,
        chat_id=chat_id,
        chat_name=chat_name,
        username=session.get("username"),
        projects=projects,
        selected_project_id=session.get("selected_project_id")
    )

@chat_bp.route("/chat/rename", methods=["POST"])
@login_required
def rename_chat():
    new_name = request.form.get("new_name")
    chat_id = session.get("chat_id")
    if chat_id and new_name:
        db.execute_query("UPDATE chatbot_schema.chat SET name = %s WHERE idchat = %s;", (new_name, chat_id))
        flash("Chat renamed.", "success")
    return redirect("/chat")

@chat_bp.route("/chat/new", methods=["POST"])
@login_required
def new_chat():
    user_id = session["user_id"]
    db.execute_query("INSERT INTO chatbot_schema.chat (user_id) VALUES (%s);", (user_id,))
    new_chat_id = db.read_sql_query("""
        SELECT idchat FROM chatbot_schema.chat WHERE user_id = %s ORDER BY created_at DESC LIMIT 1;
    """, (user_id,))[0][0]
    session["chat_id"] = new_chat_id
    session["selected_project_id"] = None
    flash("New chat started.", "info")
    return redirect("/chat")
