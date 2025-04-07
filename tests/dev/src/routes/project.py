from flask import Blueprint, render_template, request, redirect, session, flash, g
from tests.dev.src.db.db_utils import PostgresDatabaseConnection
from tests.dev.src.routes.chat import get_sidebar_data

project_bp = Blueprint("project", __name__)
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


@project_bp.route("/projects", methods=["GET"])
@login_required
def view_projects():
    user_id = session["user_id"]
    project_df = db.read_sql_query("""
        SELECT idproject, name, description, created_at
        FROM chatbot_schema.project
        WHERE user_id = %s
        ORDER BY created_at DESC;
    """, (user_id,))

    projects = project_df.to_dict("records") if hasattr(project_df, "to_dict") else []

    sidebar_projects, unassigned_chats = get_sidebar_data(user_id)
    print("[PROJECT VIEW] sidebar_projects =", sidebar_projects)
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
    name = request.form.get("name")
    description = request.form.get("description", "")
    user_id = session["user_id"]
    if name:
        db.execute_query(
            """
            INSERT INTO chatbot_schema.project (name, description, user_id)
            VALUES (%s, %s, %s);
            """,
            (name, description, session["user_id"]))
        flash("Project created", "success")
    return redirect("/projects")


@project_bp.route("/projects/<int:project_id>/rename", methods=["POST"])
@login_required
def rename_project(project_id):
    new_name = request.form.get("new_name")
    user_id = session["user_id"]
    if new_name:
        db.execute_query(
            """
            UPDATE chatbot_schema.project
            SET name = %s
            WHERE idproject = %s AND user_id = %s;
            """,
            (new_name, project_id, user_id),
        )
        flash("Project renamed.", "success")
    return redirect("/projects")


@project_bp.route("/projects/<int:project_id>/update_desc", methods=["POST"])
@login_required
def update_description(project_id):
    new_desc = request.form.get("description")
    user_id = session["user_id"]
    db.execute_query(
        """
        UPDATE chatbot_schema.project
        SET description = %s
        WHERE idproject = %s AND user_id = %s;
        """,
        (new_desc, project_id, user_id),
    )
    flash("Description updated.", "success")
    return redirect("/projects")


@project_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    user_id = session["user_id"]
    db.execute_query(
        """
        DELETE FROM chatbot_schema.project
        WHERE idproject = %s AND user_id = %s;
        """,
        (project_id, user_id),
    )
    flash("Project deleted (and associated chats).", "danger")
    return redirect("/projects")
