from flask import Flask
from tests.dev.src.config import config
from tests.dev.src.routes.main import bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    app.register_blueprint(bp)

    return app
