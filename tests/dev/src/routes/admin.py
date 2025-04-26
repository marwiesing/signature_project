from flask import Blueprint, render_template, session
from tests.dev.src.utils.auth_utils import require_role
from tests.dev.src.utils.postgresdatabaseconnection import PostgresDatabaseConnection

admin_bp = Blueprint("admin", __name__)
db = PostgresDatabaseConnection()

@admin_bp.route("/admin")
@require_role("Admin")
def admin_dashboard():
    stats = {
        "users": db.read_sql_query("SELECT COUNT(*) FROM chatbot_schema.app_user")[0][0],
        "chats": db.read_sql_query("SELECT COUNT(*) FROM chatbot_schema.chat")[0][0],
    }
    return render_template("admin.html", stats=stats)
