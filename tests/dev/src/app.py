from flask import Flask
from tests.dev.src.config import config
from tests.dev.src.models import db  
from tests.dev.src.routes import bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # Init DB
    db.init_app(app)

    app.register_blueprint(bp)

    return app
