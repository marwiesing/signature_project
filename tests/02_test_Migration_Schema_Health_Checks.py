from flask_migrate import upgrade
from sqlalchemy import inspect, text
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tests.dev.src.app import create_app, db

REQUIRED_TABLES = ["alembic_version", "app_user", "chat", "message", "project"]  # adjust to your models

def test_database():
    app = create_app()
    with app.app_context():
        print("✅ Running migration upgrade check...")
        upgrade()  # Safe to run repeatedly – applies only new migrations

        engine = db.engine  # Updated to avoid deprecation warning
        inspector = inspect(engine)

        # Get current schema and connected DB
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), current_schema();"))
            db_name, schema = result.fetchone()
            print(f"✅ Connected to database: {db_name}, schema: {schema}")

        # Check if required tables exist
        print("🔎 Checking for required tables...")
        existing_tables = inspector.get_table_names(schema=schema)
        missing_tables = [table for table in REQUIRED_TABLES if table not in existing_tables]
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}")
        else:
            print("✅ All required tables are present.")


        # Check current Alembic version
        try:
            with engine.connect() as conn:
                query = text(f"SELECT version_num FROM {schema}.alembic_version")
                result = conn.execute(query)
                version = result.scalar()
                print(f"📌 Current Alembic version: {version}")
        except Exception as e:
            print("⚠️ Could not retrieve Alembic version.")
            print(f"   ↳ {type(e).__name__}: {e}")

        # Optional test: run a simple query
        try:
            with engine.connect() as conn:
                query = text(f"SELECT COUNT(*) FROM {schema}.app_user")
                conn.execute(query)
                print("✅ app_user table is queryable.")
        except Exception as e:
            print("⚠️ Could not query app_user table.")
            print(f"   ↳ {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_database()
