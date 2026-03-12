import sqlite3
import os

DB_FILE = "football.db"
SQL_FOLDER = "sql"


def initialize_database():
    schema_path = os.path.join(SQL_FOLDER, "schema.sql")
    test_data_path = os.path.join(SQL_FOLDER, "test_data.sql")

    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Schema
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    # Test data
    with open(test_data_path, "r", encoding="utf-8") as f:
        test_data_sql = f.read()
    cursor.executescript(test_data_sql)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


if __name__ == "__main__":
    initialize_database()
