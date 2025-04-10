from src.utils.postgresdatabaseconnection import PostgresDatabaseConnection

# Define patch file paths
patch_files = [
    "../sql/drop_schema.sql",
    "../sql/create_schema.sql",
    "../sql/initialize_schema.sql"
]

def apply_patch(db, paths):
    for path in paths:
        print(f"\n📄 Applying patch: {path}")
        with open(path, "r") as f:
            sql = f.read()
        try:
            with db.connection.cursor() as cursor:
                for statement in sql.strip().split(";"):
                    if statement.strip():
                        print(f"🔧 Executing: {statement.strip()}")
                        cursor.execute(statement)
                db.connection.commit()
                print("✅ Patch applied successfully.")
        except Exception as e:
            db.connection.rollback()
            print(f"❌ Error applying patch: {e}")

if __name__ == "__main__":
    db = PostgresDatabaseConnection()
    apply_patch(db, patch_files)
