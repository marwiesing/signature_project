from flask import Blueprint, render_template, request, redirect, session, flash, g, Response
from threading import Thread
from src.utils.postgresdatabaseconnection import PostgresDatabaseConnection
from src.utils.validator import Validator
from src.utils.llm import LLMHelper
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

def get_sidebar_data(user_id):
    sidebar_projects = []
    project_data = db.read_sql_query("""
        SELECT idproject, txname, txdescription
        FROM chatbot_schema.project
        WHERE idappuser = %s
        ORDER BY dtcreated DESC;
    """, (user_id,))

    if isinstance(project_data, list):
        project_df = pd.DataFrame(project_data, columns=["idproject", "txname", "txdescription"])
    else:
        project_df = project_data

    if project_df is not None and not project_df.empty:
        for _, row in project_df.iterrows():
            project_id = row["idproject"]
            name = row["txname"]
            description = row.get("txdescription") or ""
            chats_df = db.read_sql_query("""
                SELECT idchat, txname FROM chatbot_schema.chat
                WHERE idappuser = %s AND idproject = %s
                ORDER BY dtcreated DESC;
            """, (user_id, project_id))
            chats = chats_df.to_dict("records") if hasattr(chats_df, "to_dict") else [
                {"idchat": row[0], "txname": row[1]} for row in chats_df]
            sidebar_projects.append({
                "idproject": project_id,
                "name": name,
                "description": description,
                "chats": chats
            })

    unassigned_df = db.read_sql_query("""
        SELECT idchat, txname FROM chatbot_schema.chat
        WHERE idappuser = %s AND idproject IS NULL
        ORDER BY dtcreated DESC;
    """, (user_id,))

    unassigned_chats = unassigned_df.to_dict("records") if hasattr(unassigned_df, "to_dict") else [
        {"idchat": row[0], "txname": row[1]} for row in unassigned_df]

    return sidebar_projects, unassigned_chats

def update_response_async(prompt, model_name, chat_id, id_message):
    def run():
        markdown_text, response_html = llm.query_ollama(prompt, model_name)
        db.execute_query("""
            UPDATE chatbot_schema.response
            SET txcontent = %s,
                txmarkdown = %s
            WHERE idmessage = %s AND idchat = %s;
        """, (response_html, markdown_text, id_message, chat_id))
    Thread(target=run).start()

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
            WHERE idappuser = %s
            ORDER BY dtcreated DESC LIMIT 1;
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
        # 1. Validate user input
        result = Validator.check([
            (request.form.get("content"), "Message", 5000, True)
        ])
        if not result:
            return redirect(f"/chat/{chat_id}")

        prompt = result[0]

        # 2. Store user message
        db.execute_query("""
            INSERT INTO chatbot_schema.message (idchat, txcontent)
            VALUES (%s, %s);
        """, (chat_id, prompt))

        # 3. Fetch last inserted message ID
        message_id_result = db.read_sql_query("""
            SELECT idmessage FROM chatbot_schema.message
            WHERE idchat = %s
            ORDER BY dtcreated DESC LIMIT 1;
        """, (chat_id,))
        id_message = message_id_result[0][0] if message_id_result else None

        # 4. Get model name for this chat
        model_result = db.read_sql_query("""
            SELECT l.txname FROM chatbot_schema.chat c
            JOIN chatbot_schema.llm l ON c.idllm = l.idllm
            WHERE c.idchat = %s;
        """, (chat_id,))
        model_name = model_result[0][0] if model_result else "deepseek-r1"

        # 5. Store temporary placeholder first
        db.execute_query("""
            INSERT INTO chatbot_schema.response (idchat, idmessage, idllm, txcontent, txmarkdown)
            VALUES (
                %s,
                %s,
                (SELECT idllm FROM chatbot_schema.chat WHERE idchat = %s),
                '🧠 Thinking...',
                '🧠 Thinking...'
            );
        """, (chat_id, id_message, chat_id))

    #     # 6. Send prompt to LLM
    #     markdown_text, response_html = llm.query_ollama(prompt, model_name)

    #     # 7. Then update the response after model finishes
    #     db.execute_query("""
    #         UPDATE chatbot_schema.response
    #         SET txcontent = %s,
    #             txmarkdown = %s
    #         WHERE idmessage = %s AND idchat = %s;
    #     """, (response_html, markdown_text, id_message, chat_id))


    #     return redirect(f"/chat/{chat_id}")

        update_response_async(prompt, model_name, chat_id, id_message)
        return redirect(f"/chat/{chat_id}")

    # === GET METHOD ===

    # Sidebar: Projects + Chats
    sidebar_projects, unassigned = get_sidebar_data(user_id)

    ### Try to get the llm.txShortname:

    # Current model info
    model_result = db.read_sql_query("""
        SELECT idllm FROM chatbot_schema.chat WHERE idchat = %s;
    """, (chat_id,))
    current_model_id = model_result[0][0] if model_result else llm.get_default_model_id()
#    current_model_name = llm.get_model_name_by_id(current_model_id)
    current_model_short = next((m["short"] for m in llm_models if m["id"] == current_model_id),llm.get_model_name_by_id(current_model_id))

    # Fetch all user messages and LLM responses (paired)
    rows = db.read_sql_query("""
        SELECT
            m.txContent AS message,
            m.dtCreated AS message_time,
            r.idllm AS response_llm_id,
            r.txContent AS response,
            r.dtCreated AS response_time
        FROM chatbot_schema.message m
        LEFT JOIN chatbot_schema.response r ON m.idmessage = r.idmessage
        WHERE m.idchat = %s
        ORDER BY m.dtcreated ASC;
    """, (chat_id,))

#    message_pairs = [{
#        "message": row[0],
#        "message_time": row[1],
#        "response": row[2],
#        "response_time": row[3],
#    } for row in rows]

    message_pairs = []
    for message, message_time, response_llm_id, response, response_time in rows:
        resp_llm_id = response_llm_id or current_model_id
        resp_short = next((m["short"] for m in llm_models if m["id"] == resp_llm_id),current_model_short)

        message_pairs.append({
            "message":       message,
            "message_time":  message_time,
            "response":      response,
            "response_time": response_time,
            "response_short": resp_short
        })

    # ─── Fetch this chat's name and its project (if any) ──────────────────
    info = db.read_sql_query("""
        SELECT
          c.txname   AS chat_name,
          p.txname   AS project_name
        FROM chatbot_schema.chat c
        LEFT JOIN chatbot_schema.project p
          ON c.idproject = p.idproject
        WHERE c.idchat = %s;
    """, (chat_id,))

    if info:
        # If the chat has a name and possibly a project
        chat_name    = info[0][0]
        project_name = info[0][1]
    else:
        chat_name    = "Chat"
        project_name = None

    return render_template("chat.html",
        messages=message_pairs,
        username=session.get("username"),
        sidebar_projects=sidebar_projects,
        unassigned_chats=unassigned,
        chat_id=chat_id,
        show_chat_sidebar=True,
        llm_models=llm_models,
        current_model_id=current_model_id,
        current_model_short=current_model_short,
        chat_name=chat_name,
        project_name=project_name
    )

@chat_bp.route("/chat/<int:chat_id>/rename", methods=["POST"])
@login_required
def rename_chat(chat_id):
    result = Validator.check([
        (request.form.get("new_name"), "Chat name", 100, True)
    ])
    if not result:
        return redirect(f"/chat/{chat_id}")

    new_name = result[0]
    user_id = session["user_id"]  

    db.execute_query("""
        UPDATE chatbot_schema.chat
        SET txname = %s
        WHERE idchat = %s AND idappuser = %s;
    """, (new_name, chat_id, user_id))
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
        SET idproject = %s
        WHERE idchat = %s;
    """, (project_id, chat_id))
    flash("Chat assigned to project.", "success")
    return redirect(f"/chat/{chat_id}")

@chat_bp.route("/chat/<int:chat_id>/remove", methods=["POST"])
@login_required
def remove_from_project(chat_id):
    db.execute_query("""
        UPDATE chatbot_schema.chat
        SET idproject = NULL
        WHERE idchat = %s;
    """, (chat_id,))
    flash("Chat removed from project.", "warning")
    return redirect(f"/chat/{chat_id}")

@chat_bp.route("/chat/<int:chat_id>/delete", methods=["POST"])
@login_required
def delete_chat(chat_id):
    db.execute_query("""
        DELETE FROM chatbot_schema.message WHERE idchat = %s;
        DELETE FROM chatbot_schema.chat WHERE idchat = %s;
    """, (chat_id, chat_id))
    flash("Chat deleted.", "danger")
    return redirect("/chat")

@chat_bp.route("/chat/<int:chat_id>/set_model", methods=["POST"])
@login_required
def change_model(chat_id):
    llm_id = request.form.get("llm_id")
    llm.update_chat_model(chat_id, llm_id)
    flash("LLM model updated for this chat.", "success")
    return redirect(f"/chat/{chat_id}")

@chat_bp.route("/chat/new")
@login_required
def create_new_chat():
    user_id = session["user_id"]

    # Insert a new chat with default model and placeholder name
    db.execute_query("""
        INSERT INTO chatbot_schema.chat (idappuser, txname, idllm)
        VALUES (
            %s,
            %s,
            (SELECT idllm FROM chatbot_schema.llm WHERE txname = 'deepseek-r1')
        );
    """, (user_id, 'Untitled Chat'))

    # Fetch the newly created chat ID
    new_chat_id_result = db.read_sql_query("""
        SELECT idchat FROM chatbot_schema.chat
        WHERE idappuser = %s
        ORDER BY dtcreated DESC LIMIT 1;
    """, (user_id,))
    
    new_chat_id = new_chat_id_result[0][0] if new_chat_id_result else None

    if new_chat_id:
        session["chat_id"] = new_chat_id
        flash("New chat started!", "success")
        return redirect(f"/chat/{new_chat_id}")
    else:
        flash("Failed to create chat.", "danger")
        return redirect("/chat")

# @chat_bp.route("/chat/<int:chat_id>/export", methods=["GET"])
# @login_required
# def export_chat_markdown(chat_id):
#     user_id = session["user_id"]

#     # Fetch messages and responses
#     rows = db.read_sql_query("""
#         SELECT
#             m.txContent AS message,
#             m.dtCreated AS message_time,
#             r.txContent AS response,
#             r.dtCreated AS response_time
#         FROM chatbot_schema.message m
#         LEFT JOIN chatbot_schema.response r ON m.idmessage = r.idmessage
#         WHERE m.idchat = %s AND m.idappuser = %s
#         ORDER BY m.dtcreated ASC;
#     """, (chat_id, user_id))

#     # Convert to Markdown format
#     markdown_lines = [f"# 🧠 Chat Export (Chat ID: {chat_id})\n"]
#     for row in rows:
#         msg_time = row[1].strftime("%Y-%m-%d %H:%M:%S")
#         resp_time = row[3].strftime("%Y-%m-%d %H:%M:%S") if row[3] else ""
#         markdown_lines.append(f"### 🧑 You ({msg_time})\n{row[0]}\n")
#         if row[2]:
#             markdown_lines.append(f"### 🤖 Bot ({resp_time})\n{row[2]}\n")

#     markdown_content = "\n".join(markdown_lines)

#     return render_template("export_chat.html", markdown=markdown_content, chat_id=chat_id)

@chat_bp.route("/chat/<int:chat_id>/download", methods=["GET"])
@login_required
def download_chat_markdown(chat_id):
    user_id = session["user_id"]

    rows = db.read_sql_query("""
        SELECT
            m.txContent AS message,
            m.dtCreated AS message_time,
            r.txmarkdown AS response, 
            r.dtCreated AS response_time
        FROM chatbot_schema.message m
        LEFT JOIN chatbot_schema.response r ON m.idmessage = r.idmessage
        JOIN chatbot_schema.chat c ON m.idchat = c.idchat
        WHERE m.idchat = %s AND c.idappuser = %s
        ORDER BY m.dtcreated ASC;
    """, (chat_id, user_id))

    if not rows:
        flash("No messages found or access denied.", "danger")
        return redirect(f"/chat/{chat_id}")

    markdown_lines = [f"# 🧠 Chat Export (Chat ID: {chat_id})\n"]
    for row in rows:
        msg_time = row[1].strftime("%Y-%m-%d %H:%M:%S")
        resp_time = row[3].strftime("%Y-%m-%d %H:%M:%S") if row[3] else ""
        markdown_lines.append(f"### 🧑 You ({msg_time})\n{row[0]}\n")
        if row[2]:
            markdown_lines.append(f"### 🤖 Bot ({resp_time})\n{row[2]}\n")

    markdown_content = "\n".join(markdown_lines)
    return Response(markdown_content, mimetype="text/markdown",
                    headers={"Content-Disposition": f"attachment;filename=chat_{chat_id}.md"})
