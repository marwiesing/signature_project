from flask import Blueprint, render_template, request, redirect, session, flash, g
from ..utils.postgresdatabaseconnection import PostgresDatabaseConnection
from ..utils.validator import Validator
from .chat import get_sidebar_data
import pandas as pd

project_bp = Blueprint("project", __name__)
db = PostgresDatabaseConnection()

def ensure_dataframe(data, columns):
    if isinstance(data, list):
        return pd.DataFrame(data, columns=columns)
    return data

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

@project_bp.route("/projects", methods=["GET"])
@login_required
def view_projects():
    user_id = session["user_id"]
    project_df = ensure_dataframe(
        db.read_sql_query("""
            SELECT idproject, txname, txdescription, dtcreated
            FROM chatbot_schema.project
            WHERE idappuser = %s
            ORDER BY dtcreated DESC;
        """, (user_id,)),
        ["idproject", "txname", "txdescription", "dtcreated"]
    )

    projects = project_df.to_dict("records") if hasattr(project_df, "to_dict") else []
    sidebar_projects, unassigned_chats = get_sidebar_data(user_id)

    return render_template(
        "project.html",
        projects=projects,
        sidebar_projects=sidebar_projects,
        unassigned_chats=unassigned_chats,
        show_chat_sidebar=True
    )

@project_bp.route("/projects/create", methods=["POST"])
@login_required
def create_project():
    result = Validator.check([
        (request.form.get("name"), "Project name", 100, True),
        (request.form.get("description", ""), "Description", 500, False)
    ])
    if not result:
        return redirect("/projects")

    name, description = result
    user_id = session["user_id"]

    db.execute_query("""
        INSERT INTO chatbot_schema.project (txname, txdescription, idappuser)
        VALUES (%s, %s, %s);
    """, (name, description, user_id))
    flash("Project created", "success")
    return redirect("/projects")

@project_bp.route("/projects/<int:project_id>/rename", methods=["POST"])
@login_required
def rename_project(project_id):
    result = Validator.check([
        (request.form.get("new_name"), "New project name", 100, True)
    ])
    if not result:
        return redirect("/projects")

    new_name = result[0]
    user_id = session["user_id"]
    db.execute_query("""
        UPDATE chatbot_schema.project
        SET txname = %s
        WHERE idproject = %s AND idappuser = %s;
    """, (new_name, project_id, user_id))
    flash("Project renamed.", "success")
    return redirect("/projects")

@project_bp.route("/projects/<int:project_id>/update_desc", methods=["POST"])
@login_required
def update_description(project_id):
    print(f"[DEBUG] Description received: {request.form.get('description')}")
    result = Validator.check([
        (request.form.get("description"), "Project description", 500, False)
    ])
    if not result:
        return redirect("/projects")

    new_desc = result[0]
    user_id = session["user_id"]
    db.execute_query("""
        UPDATE chatbot_schema.project
        SET txdescription = %s
        WHERE idproject = %s AND idappuser = %s;
    """, (new_desc, project_id, user_id))
    flash("Description updated.", "success")
    return redirect("/projects")

@project_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    user_id = session["user_id"]
    db.execute_query("""
        DELETE FROM chatbot_schema.project
        WHERE idproject = %s AND idappuser = %s;
    """, (project_id, user_id))
    flash("Project deleted along with its chats and messages.", "danger")
    return redirect("/projects")

@project_bp.route("/projects/<int:project_id>")
@login_required
def project_detail(project_id):
    user_id = session["user_id"]

    project_df = ensure_dataframe(
        db.read_sql_query("""
            SELECT idproject, txname, txdescription, dtcreated
            FROM chatbot_schema.project
            WHERE idproject = %s AND idappuser = %s;
        """, (project_id, user_id)),
        ["idproject", "txname", "txdescription", "dtcreated"]
    )

    project_records = project_df.to_dict("records") if hasattr(project_df, "to_dict") else []
    if not project_records:
        flash("Project not found or unauthorized", "danger")
        return redirect("/projects")

    project = project_records[0]

    chats_df = ensure_dataframe(
        db.read_sql_query("""
            SELECT idchat, txname, dtcreated
            FROM chatbot_schema.chat
            WHERE idproject = %s AND idappuser = %s
            ORDER BY dtcreated DESC;
        """, (project_id, user_id)),
        ["idchat", "txname", "dtcreated"]
    )

    chats = chats_df.to_dict("records") if hasattr(chats_df, "to_dict") else []
    sidebar_projects, unassigned_chats = get_sidebar_data(user_id)

    return render_template("project_detail.html",
        project=project,
        chats=chats,
        sidebar_projects=sidebar_projects,
        unassigned_chats=unassigned_chats,
        show_chat_sidebar=True
    )

@project_bp.route("/projects/<int:project_id>/new_chat", methods=["POST"])
@login_required
def create_chat_in_project(project_id):
    user_id = session["user_id"]

    # Confirm the project belongs to this user
    project = db.read_sql_query("""
        SELECT idproject FROM chatbot_schema.project
        WHERE idproject = %s AND idappuser = %s;
    """, (project_id, user_id))

    if not project:
        flash("Unauthorized or missing project.", "danger")
        return redirect("/projects")

    # Create new chat assigned to this project
    db.execute_query("""
        INSERT INTO chatbot_schema.chat (idappuser, idproject, txname, idllm)
        VALUES (
            %s,
            %s,
            %s,
            (SELECT idllm FROM chatbot_schema.llm WHERE txname = 'deepseek-r1')
        );
    """, (user_id, project_id, "New Project Chat"))

    flash("New chat created in this project.", "success")

    # Get newly created chat ID
    chat_id_result = db.read_sql_query("""
        SELECT idchat FROM chatbot_schema.chat
        WHERE idappuser = %s AND idproject = %s
        ORDER BY dtcreated DESC LIMIT 1;
    """, (user_id, project_id))

    if chat_id_result:
        return redirect(f"/chat/{chat_id_result[0][0]}")
    return redirect("/projects")
