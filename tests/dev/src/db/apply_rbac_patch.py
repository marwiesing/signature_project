from db_utils import PostgresDatabaseConnection


def apply_patch():
    patch_path = "tests/dev/src/sql/rbac_patch.sql"
    with open(patch_path, "r") as f:
        sql = f.read()
    try:
        db = PostgresDatabaseConnection()
        with db.connection.cursor() as cursor:
            for statement in sql.strip().split(";"):
                if statement.strip():
                    print(f"🔧 Executing: {statement.strip()}")
                    cursor.execute(statement)
            db.connection.commit()
            print("✅ RBAC patch applied successfully.")
    except Exception as e:
        db.connection.rollback()
        print(f"❌ Error applying RBAC patch: {e}")

if __name__ == "__main__":
    apply_patch()
