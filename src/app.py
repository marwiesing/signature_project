from flask import Flask
from flask_migrate import Migrate
from src.config import config
from src.models import db  # includes all models
from src.routes import bp

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # Init DB + Migrations
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(bp)

    return app
