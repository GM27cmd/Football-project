import sqlite3
import os

DB_NAME = "football.db"

def initialize_database():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ===== LOAD SCHEMA =====
    with open("sql/schema.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)

    # ===== LOAD TEST DATA =====
    with open("sql/test_data.sql", "r", encoding="utf-8") as f:
        test_data_sql = f.read()

    cursor.executescript(test_data_sql)

    conn.commit()
    conn.close()

    print("Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()
