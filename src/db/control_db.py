from src.utils.postgresdatabaseconnection import PostgresDatabaseConnection


def run_control_sql():
    patch_path = "../sql/control.sql"
    with open(patch_path, "r") as f:
        sql = f.read()

    try:
        db = PostgresDatabaseConnection()
        with db.connection.cursor() as cursor:
            for statement in sql.strip().split(";"):
                clean = statement.strip()
                if clean:
                    print(f"\n🔎 Executing:\n{clean}")
                    cursor.execute(clean)

                    try:
                        rows = cursor.fetchall()
                        for row in rows:
                            print("📄", row)
                    except Exception:
                        print("⚠️  No results to fetch.")

        print("\n✅ Control SQL script executed.")
    except Exception as e:
        print(f"\n❌ Error running control SQL: {e}")


if __name__ == "__main__":
    run_control_sql()
