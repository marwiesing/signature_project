from sqlalchemy import create_engine, text
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import config  # this imports your Config instance

def test_connection():
    try:
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI, **config.SQLALCHEMY_ENGINE_OPTIONS)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database(), current_schema();"))
            db_name, schema = result.fetchone()
            print(f"✅ Connected to database: {db_name}, schema: {schema}")
    except Exception as e:
        print("❌ Failed to connect to the database.")
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()
