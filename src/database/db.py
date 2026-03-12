import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "../../football.db")


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def execute_query(query, params=(), fetch=False):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        if fetch:
            return cursor.fetchall()
    finally:
        conn.close()
