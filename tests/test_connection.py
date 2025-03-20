import psycopg2
import pandas as pd
import sqlparse as sp
import os


class PostgresDatabaseConnection():
    def __init__(self):
        self.database_host = os.getenv("PSQL_HOST") 
        self.database_name = os.getenv("PSQL_DB") 
        self.database_user = os.getenv("PSQL_USER")
        self.database_password = os.getenv("PSQL_PASSWORD")
        self.database_port = os.getenv("PSQL_PORT")
        self.connection = self.connect_to_database()

    def connect_to_database(self):
        try:
            connection = psycopg2.connect(
                host=self.database_host,
                dbname=self.database_name,
                user=self.database_user,
                password=self.database_password,
                port=self.database_port
            )
            print(f'Connection established to PostgreSQL: {self.database_name}')
            return connection
        except Exception as e:
            print("Error while connecting to PostgreSQL", e)
            return None  # Return None in case of error

    def read_sql_query(self, query):
        if self.connection:
            try:
                return pd.read_sql_query(query, self.connection)
            except Exception as e:
                print("Error while executing query", e)
                return None
        else:
            print("No database connection available.")
            return None

    def execute_query(self, query):
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(query)
                    self.connection.commit()
            except Exception as e:
                print("Error while executing query", e)
                self.connection.rollback()
        else:
            print("No database connection available.")
            return None

    def disconnect(self):
        if self.connection:
            try:
                self.connection.close()
                print("Database connection closed.")
            except Exception as e:
                print("Error while closing the connection", e)

# Example usage
if __name__ == "__main__":
    db = PostgresDatabaseConnection()

    with db.connection.cursor() as cursor:
        print("\n🔹 PostgreSQL Current User:")
        cursor.execute("SELECT current_user;")
        print("Connected as:", cursor.fetchone())

    print("\n🔹 PostgreSQL Roles:")
    query_roles = "SELECT rolname, rolsuper, rolcreatedb, rolcanlogin FROM pg_roles;"
    print(db.read_sql_query(query_roles))

    print("\n🔹 Available Databases:")
    query_databases = "SELECT datname FROM pg_database WHERE datistemplate = false;"
    print(db.read_sql_query(query_databases))

    print("\n🔹 Verify the Privileges of chatbot_db:")
    query_tables = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
    print(db.read_sql_query(query_tables))

    db.disconnect()
