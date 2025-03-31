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


def execute_sql_file(connection, filepath):
    """Reads a SQL file, splits it into statements, and executes them sequentially."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(base_dir, filepath)
    try:
        with open(sql_path, "r") as file:
            sql_content = file.read()
            sql_statements = sp.split(sql_content)

        with connection.cursor() as cursor:
            for statement in sql_statements:
                clean_statement = statement.strip()
                if clean_statement:
                    print(f"\n📄 Executing:\n{clean_statement}")
                    cursor.execute(clean_statement)
                    try:
                        result = cursor.fetchall()
                        for row in result:
                            print(row)
                    except psycopg2.ProgrammingError:
                        # No results to fetch (e.g., for GRANT/ALTER)
                        pass
        connection.commit()
    except Exception as e:
        print("❌ Error while executing SQL file:", e)


# Example usage
if __name__ == "__main__":
    db = PostgresDatabaseConnection()

    # Old:
    with db.connection.cursor() as cursor:
        print("\n🔹 PostgreSQL Current User:")
        cursor.execute("SELECT current_user;")
        print("Connected as:", cursor.fetchone())

    print("\n🔹 PostgreSQL Roles:")
    query_roles = "SELECT rolname, rolsuper, rolcreatedb, rolcanlogin FROM pg_roles;"
    print(db.read_sql_query(query_roles))

    # New:
    if db.connection:
        # Run the SQL file with checks
        execute_sql_file(db.connection, "database_test.sql")

        db.disconnect()
    else:
        print("❌ Could not establish a connection to the database.") 

