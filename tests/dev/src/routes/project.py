from flask import Blueprint, request, redirect, render_template, session, flash
from tests.dev.src.db.db_utils import PostgresDatabaseConnection

project_bp = Blueprint("project", __name__)
db = PostgresDatabaseConnection()

@project_bp.route("/projects", methods=["GET", "POST"])
def projects():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/")

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        if name:
            db.execute_query("""
                INSERT INTO chatbot_schema.project (name, description)
                VALUES (%s, %s)
            """, (name, description or ""))
            flash("New project created!", "success")
            return redirect("/projects")

    result = db.read_sql_query("""
        SELECT * FROM chatbot_schema.project
        ORDER BY created_at DESC
    """)
    projects = result.to_dict(orient="records") if result is not None else []

    return render_template("projects.html", projects=projects)
