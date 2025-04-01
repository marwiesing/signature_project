from flask import Flask
from src.config import config
from src.models import db  
from src.routes import bp
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(config)
    logger.info("Initializing Flask app...")

    db.init_app(app)
    logger.info("SQLAlchemy initialized.")

    app.register_blueprint(bp)
    logger.info("Blueprint registered.")

    return app

