import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "../../football.db")


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def execute_query(query, params=(), fetch=False):
    import sqlite3

    conn = sqlite3.connect("football.db")
    cursor = conn.cursor()

    cursor.execute(query, params)

    if fetch:
        result = cursor.fetchall()
        conn.close()
        return result

    conn.commit()
    conn.close()
