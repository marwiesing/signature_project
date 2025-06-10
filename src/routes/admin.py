from flask import Blueprint, render_template, session, redirect, url_for, flash
from src.utils.auth_utils import require_role
from src.utils.postgresdatabaseconnection import PostgresDatabaseConnection

admin_bp = Blueprint("admin", __name__)
db = PostgresDatabaseConnection()

@admin_bp.route("/admin")
@require_role("Admin")
def admin_dashboard():
    stats = {
        "users": db.read_sql_query("SELECT COUNT(*) FROM chatbot_schema.app_user;").iloc[0, 0],
        "chats": db.read_sql_query("SELECT COUNT(*) FROM chatbot_schema.chat;").iloc[0, 0],
    }

    user_list = db.read_sql_query("""
        SELECT u.idappuser, u.txusername, u.txemail, r.txname AS role, u.dtcreated, COUNT(DISTINCT p.idProject) AS project_count, COUNT(DISTINCT c.idChat) AS chat_count
        FROM chatbot_schema.app_user u
        JOIN chatbot_schema.user_role ur ON u.idappuser = ur.idappuser
        JOIN chatbot_schema.role r ON ur.idrole = r.idrole
        LEFT JOIN chatbot_schema.project p ON p.idappuser = u.idappuser
        LEFT JOIN chatbot_schema.chat c ON c.idappuser = u.idappuser
        GROUP BY u.idappuser, u.txusername, u.txemail, r.txname, u.dtcreated
        ORDER BY u.idappuser;
    """).values.tolist()

    return render_template("admin.html", stats=stats, users=user_list)


@admin_bp.route("/admin/promote/<int:user_id>")
@require_role("Admin")
def promote_user(user_id):
    db.execute_query("""
        UPDATE chatbot_schema.user_role
        SET idrole = 1
        WHERE idappuser = %s;
    """, (user_id,))
    flash("User promoted to Admin.", "success")
    return redirect(url_for("admin.admin_dashboard"))
