from sqlalchemy import create_engine, text
import os
from pathlib import Path
from dotenv import load_dotenv; load_dotenv()
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Define schema and required table(s)
SCHEMA_NAME = "chatbot_schema"
REQUIRED_TABLES = ["app_user", "project", "chat", "message"]

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
    logger.info("Initializing database schema check...")

    try:        
        engine = create_engine(
            f"postgresql://{os.getenv('PSQL_USER')}:{os.getenv('PSQL_PASSWORD')}@{os.getenv('PSQL_HOST')}:{os.getenv('PSQL_PORT')}/{os.getenv('PSQL_DB')}"
        )

        with engine.begin() as connection:
            if not schema_exists(connection):
                logger.info("Schema does not exist. Creating schema and granting privileges...")
                schema_sql = Path("src/sql/00_create_schema.sql").read_text()
                connection.execute(text(schema_sql))
                logger.info("✅ Schema created and privileges granted.")
            else:
                logger.info("Schema already exists. Skipping creation.")

            if schema_already_initialized(connection):
                logger.info("✅ Schema already initialized. Skipping table creation.")
            else:
                logger.info("🔧 Tables not found. Initializing schema with tables...")
                sql_path = Path("src/sql/initialize_schema.sql")
                sql = sql_path.read_text()
                connection.execute(text(sql))
                logger.info("✅ Tables created successfully.")

        logger.info("Schema initialization completed.")

    except Exception as e:
        logger.exception("❌ Exception during schema initialization")
        sys.exit(1)
