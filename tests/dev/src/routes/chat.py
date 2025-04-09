from flask import Blueprint, render_template, request, redirect, session, flash, g
from tests.dev.src.utils.postgresdatabaseconnection import PostgresDatabaseConnection
from tests.dev.src.utils.validator import Validator
from tests.dev.src.utils.llm import LLMHelper
import pandas as pd

chat_bp = Blueprint("chat", __name__)
db = PostgresDatabaseConnection()
llm = LLMHelper()

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
    llm_models = llm.get_all_models()

    if request.method == "POST":
        result = Validator.check([
            (request.form.get("content"), "Message", 5000, True)
        ])
        if not result:
            return redirect(f"/chat/{chat_id}")

        content = result[0]
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

    current_llm_id_result = db.read_sql_query("""
    SELECT idllm FROM chatbot_schema.chat WHERE idchat = %s;
    """, (chat_id,))
    current_model_id = current_llm_id_result[0][0] if current_llm_id_result else None
    current_model_name = llm.get_model_name_by_id(current_model_id)

    return render_template("chat.html",
        messages=messages,
        username=session.get("username"),
        sidebar_projects=sidebar_projects,
        unassigned_chats=unassigned,
        chat_id=chat_id,
        show_chat_sidebar=True,
        llm_models=llm_models,
        current_model_id=current_model_id,
        current_model_name=current_model_name
    )

@chat_bp.route("/chat/new")
@login_required
def chat_new():
    user_id = session["user_id"]
    project_id = request.args.get("project_id")  # Optional

    db.execute_query("""
        INSERT INTO chatbot_schema.chat (user_id, name, project_id, idllm)
        VALUES (%s, %s, %s, %s);
    """, (user_id, "Untitled Chat", project_id if project_id else None, llm.get_default_model_id()))

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
    result = Validator.check([
        (request.form.get("new_name"), "Chat name", 100, True)
    ])
    if not result:
        return redirect(f"/chat/{chat_id}")

    new_name = result[0]
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
    result = Validator.check([
        (request.form.get("project_id"), "Project ID", 10, True)
    ])
    if not result:
        return redirect(f"/chat/{chat_id}")

    project_id = result[0]
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

@chat_bp.route("/chat/<int:chat_id>/set_model", methods=["POST"])
@login_required
def change_model(chat_id):
    llm_id = request.form.get("llm_id")
    llm = LLMHelper()
    llm.update_chat_model(chat_id, llm_id)
    flash("LLM model updated for this chat.", "success")
    return redirect(f"/chat/{chat_id}")
