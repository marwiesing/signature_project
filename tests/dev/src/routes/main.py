from flask import Blueprint, request, render_template, redirect
from tests.dev.src.db.db_utils import PostgresDatabaseConnection

bp = Blueprint("main", __name__)
db = PostgresDatabaseConnection()

@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("content")
        if content:
            # Insert into chat and get the new id
            db.execute_query("INSERT INTO chatbot_schema.chat (user_id) VALUES (1);")
            chat_id_result = db.read_sql_query("SELECT MAX(idchat) FROM chatbot_schema.chat;")
            chat_id = chat_id_result.iloc[0, 0] 
            
            # Insert message
            db.execute_query(f"""
                INSERT INTO chatbot_schema.message (chat_id, sender, content)
                VALUES ({chat_id}, 'user', %s);
            """, (content,))

        return redirect("/")

    messages_df = db.read_sql_query("""
        SELECT * FROM chatbot_schema.message
        ORDER BY timestamp DESC;
    """)
    return render_template("index.html", messages=messages_df.to_dict(orient="records"))
