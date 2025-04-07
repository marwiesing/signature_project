from flask import Blueprint, render_template, request, redirect, session, flash, g
from tests.dev.src.db.db_utils import PostgresDatabaseConnection
import pandas as pd

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

# Improved version with logging:
def get_sidebar_data(user_id):
    sidebar_projects = []

    # Read projects
    project_data = db.read_sql_query("""
        SELECT idproject, name, description
        FROM chatbot_schema.project
        WHERE user_id = %s
        ORDER BY created_at DESC;
    """, (user_id,))

    # Normalize to DataFrame
    if isinstance(project_data, list):
        project_df = pd.DataFrame(project_data, columns=["idproject", "name", "description"])
    else:
        project_df = project_data

    print("[DEBUG] project_df:", project_df)

    if project_df is not None and not project_df.empty:
        for _, row in project_df.iterrows():
            project_id = row["idproject"]
            name = row["name"]
            description = row.get("description") or ""

            chats_df = db.read_sql_query("""
                SELECT idchat, name FROM chatbot_schema.chat
                WHERE user_id = %s AND project_id = %s
                ORDER BY created_at DESC;
            """, (user_id, project_id))

            print(f"[DEBUG] Chats for project {name}:", chats_df)

            chats = []
            if hasattr(chats_df, "to_dict"):
                chats = chats_df.to_dict("records")
            elif isinstance(chats_df, list):
                chats = [{"idchat": row[0], "name": row[1]} for row in chats_df]

            sidebar_projects.append({
                "idproject": project_id,
                "name": name,
                "description": description,
                "chats": chats
            })
    else:
        print("[DEBUG] No projects found for user_id =", user_id)

    # Unassigned chats
    unassigned_df = db.read_sql_query("""
        SELECT idchat, name FROM chatbot_schema.chat
        WHERE user_id = %s AND project_id IS NULL
        ORDER BY created_at DESC;
    """, (user_id,))

    if isinstance(unassigned_df, list):
        unassigned_chats = [{"idchat": row[0], "name": row[1]} for row in unassigned_df]
    elif hasattr(unassigned_df, "to_dict"):
        unassigned_chats = unassigned_df.to_dict("records")
    else:
        unassigned_chats = []

    print("[DEBUG] Final sidebar_projects:", sidebar_projects)
    print("[DEBUG] Final unassigned_chats:", unassigned_chats)
    
    return sidebar_projects, unassigned_chats

@chat_bp.route("/chat")
@login_required
def chat():
    return redirect("/chat/current")

@chat_bp.route("/chat/current")
@login_required
def chat_current():
    user_id = session["user_id"]
    chat_id = session.get("chat_id")

    if not chat_id:
        latest = db.read_sql_query("""
            SELECT idchat FROM chatbot_schema.chat
            WHERE user_id = %s
            ORDER BY created_at DESC LIMIT 1;
        """, (user_id,))
        if latest:
            chat_id = latest[0][0]
            session["chat_id"] = chat_id
        else:
            return redirect("/chat/new")

    return redirect(f"/chat/{chat_id}")

@chat_bp.route("/chat/<int:chat_id>", methods=["GET", "POST"])
@login_required
def chat_view(chat_id):
    user_id = session["user_id"]
    session["chat_id"] = chat_id

    if request.method == "POST":
        content = request.form.get("content")
        if content:
            db.execute_query("""
                INSERT INTO chatbot_schema.message (chat_id, content)
                VALUES (%s, %s);
            """, (chat_id, content))
        return redirect(f"/chat/{chat_id}")

    messages = db.read_sql_query("""
        SELECT content, timestamp
        FROM chatbot_schema.message
        WHERE chat_id = %s
        ORDER BY timestamp ASC;
    """, (chat_id,)) or []
    messages = [{"content": row[0], "timestamp": row[1]} for row in messages]

    sidebar_projects, unassigned = get_sidebar_data(user_id)

    return render_template("chat.html",
        messages=messages,
        username=session.get("username"),
        sidebar_projects=sidebar_projects,
        unassigned_chats=unassigned,
        chat_id=chat_id,
        show_chat_sidebar=True
    )

@chat_bp.route("/chat/new")
@login_required
def chat_new():
    user_id = session["user_id"]
    project_id = request.args.get("project_id")  # Optional

    db.execute_query("""
        INSERT INTO chatbot_schema.chat (user_id, name, project_id)
        VALUES (%s, %s, %s);
    """, (user_id, "Untitled Chat", project_id if project_id else None))

    result = db.read_sql_query("""
        SELECT idchat FROM chatbot_schema.chat
        WHERE user_id = %s
        ORDER BY created_at DESC LIMIT 1;
    """, (user_id,))
    if result:
        session["chat_id"] = result[0][0]
        return redirect(f"/chat/{result[0][0]}")
    flash("Failed to create new chat", "danger")
    return redirect("/chat")

# --- New Features for Chat Actions ---

@chat_bp.route("/chat/<int:chat_id>/rename", methods=["POST"])
@login_required
def rename_chat(chat_id):
    new_name = request.form.get("new_name")
    if new_name:
        db.execute_query("""
            UPDATE chatbot_schema.chat
            SET name = %s
            WHERE idchat = %s;
        """, (new_name, chat_id))
        flash("Chat renamed.", "success")
    return redirect(f"/chat/{chat_id}")

@chat_bp.route("/chat/<int:chat_id>/assign", methods=["POST"])
@login_required
def assign_to_project(chat_id):
    project_id = request.form.get("project_id")
    if project_id:
        db.execute_query("""
            UPDATE chatbot_schema.chat
            SET project_id = %s
            WHERE idchat = %s;
        """, (project_id, chat_id))
        flash("Chat assigned to project.", "success")
    return redirect(f"/chat/{chat_id}")

@chat_bp.route("/chat/<int:chat_id>/remove", methods=["POST"])
@login_required
def remove_from_project(chat_id):
    db.execute_query("""
        UPDATE chatbot_schema.chat
        SET project_id = NULL
        WHERE idchat = %s;
    """, (chat_id,))
    flash("Chat removed from project.", "warning")
    return redirect(f"/chat/{chat_id}")

@chat_bp.route("/chat/<int:chat_id>/delete", methods=["POST"])
@login_required
def delete_chat(chat_id):
    db.execute_query("""
        DELETE FROM chatbot_schema.message WHERE chat_id = %s;
        DELETE FROM chatbot_schema.chat WHERE idchat = %s;
    """, (chat_id, chat_id))
    flash("Chat deleted.", "danger")
    return redirect("/chat")
