from flask_migrate import upgrade
from app import create_app, db  # replace with your actual app factory

app = create_app()
with app.app_context():
    upgrade()  # applies migrations (no-op if already up to date)

    # Run health checks here


