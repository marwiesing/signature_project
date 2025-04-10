from flask import Flask
from .auth import auth_bp
from .chat import chat_bp
from .project import project_bp
from src.utils.formatting import format_timestamp 
from markdown import markdown
import os

def create_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_path = os.path.join(base_dir, "..", "templates")
    static_path = os.path.join(base_dir, "..", "static")

    app = Flask(__name__, template_folder=templates_path, static_folder=static_path)
    app.secret_key = "your_secret_key"
    app.jinja_env.filters["format_timestamp"] = format_timestamp
    app.jinja_env.filters["markdown"] = markdown     

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(project_bp)

    return app
