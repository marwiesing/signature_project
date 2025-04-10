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
        
        if self.connection is None:
            raise ConnectionError("Error: Could not connect to PostgreSQL database.")

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
            return None 

    def disconnect(self):
        try:
            self.connection.close()
            print("Database connection closed.")
        except Exception as e:
            print("Error while closing the connection", e)

    def reconnect(self):
        self.connection = self.connect_to_database()
        if self.connection is None:
            raise ConnectionError("Failed to reconnect to the database.")
        
    def is_connected(self):
        return self.connection is not None          

    def read_sql_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                    return cursor.fetchall()
                else:
                    return pd.read_sql_query(query, self.connection)
        except Exception as e:
            print("Error while executing query:", e)
            return None

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                self.connection.commit()
        except Exception as e:
            print("Error while executing query", e)
            self.connection.rollback()

    def execute_sql_file(self, filepath):
        """Reads a SQL file and executes all statements sequentially."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sql_path = os.path.join(base_dir, filepath)

        try:
            with open(sql_path, "r") as file:
                sql_content = file.read()
                sql_statements = sp.split(sql_content)

            with self.connection.cursor() as cursor:
                for statement in sql_statements:
                    clean = statement.strip()
                    if clean:
                        print(f"\nExecuting:\n{clean}")
                        cursor.execute(clean)
                        try:
                            result = cursor.fetchall()
                            for row in result:
                                print("📄", row)
                        except psycopg2.ProgrammingError:
                            pass  # No result to fetch
            self.connection.commit()
            print("SQL file executed successfully.")
        except Exception as e:
            print("Error while executing SQL file:", e)
            self.connection.rollback()

    def __del__(self):
        self.disconnect()
