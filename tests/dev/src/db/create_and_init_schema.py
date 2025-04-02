from sqlalchemy import create_engine, text
import os
import sys
from pathlib import Path
from dotenv import load_dotenv; load_dotenv()
from datetime import datetime



# Define schema and required table(s)
SCHEMA_NAME = "chatbot_schema"
REQUIRED_TABLES = ["app_user", "project", "chat", "message"]

def log(message, level="INFO"):
    timestamp = datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} [{level}] {message}", file=sys.stdout if level == "INFO" else sys.stderr)


def schema_exists(connection):
    check_query = text("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name = :schema
    """)
    result = connection.execute(check_query, {"schema": SCHEMA_NAME}).fetchone()
    return result is not None

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
    log("Initializing database schema check...")
    try:
        # Setup DB connection
        engine = create_engine(
            f"postgresql://{os.getenv('PSQL_USER')}:{os.getenv('PSQL_PASSWORD')}@{os.getenv('PSQL_HOST')}:{os.getenv('PSQL_PORT')}/{os.getenv('PSQL_DB')}"
        )
        # Main logic
        with engine.begin() as connection:
            if not schema_exists(connection):
                print("Schema does not exist. Creating schema and granting privileges...")
                schema_sql = Path("tests/dev/src/sql/create_schema.sql").read_text()
                connection.execute(text(schema_sql))
                print("✅ Schema created and privileges granted.")
            else:
                print("Schema already exists. Skipping creation.")

            if schema_already_initialized(connection):
                print("Schema already initialized. Skipping.")
            else:
                # Load SQL file
                sql_path = Path("tests/dev/src/sql/initialize_schema.sql")
                sql = sql_path.read_text()
                connection.execute(text(sql))
                print("✅ Schema created successfully.")
                
        log("Schema initialization completed.")
    except Exception as e:
        log(f"Error occurred: {e}", level="ERROR")
        sys.exit(1)
