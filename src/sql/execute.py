from sqlalchemy import create_engine, text
import os
from pathlib import Path
from dotenv import load_dotenv; load_dotenv()

# Define schema and required table(s)
SCHEMA_NAME = "chatbot_schema"
REQUIRED_TABLES = ["app_user", "project", "chat", "message"]

def schema_already_initialized(connection):
    check_query = text(f"""
        SELECT tablename
        FROM pg_catalog.pg_tables
        WHERE schemaname = :schema
          AND tablename = ANY(:tables)
    """)
    result = connection.execute(
        check_query, {"schema": SCHEMA_NAME, "tables": REQUIRED_TABLES}
    ).fetchall()
    
    found_tables = {row[0] for row in result}
    return found_tables >= set(REQUIRED_TABLES)  # all required tables exist


if __name__ == "__main__":
    # Setup DB connection
    engine = create_engine(
        f"postgresql://{os.getenv('PSQL_USER')}:{os.getenv('PSQL_PASSWORD')}@{os.getenv('PSQL_HOST')}:{os.getenv('PSQL_PORT')}/{os.getenv('PSQL_DB')}"
    )
    # Main logic
    with engine.begin() as connection:
        if schema_already_initialized(connection):
            print("✅ Schema already initialized. Skipping.")
        else:
            # Load SQL file
            sql_path = Path("src/sql/initialize_schema.sql")
            sql = sql_path.read_text()
            connection.execute(text(sql))
            print("✅ Schema created successfully.")
