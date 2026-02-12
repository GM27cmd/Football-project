import sqlite3

def initialize_database():
    conn = sqlite3.connect("football.db")
    cursor = conn.cursor()

    with open("schema.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    with open("test_data.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print("Базата данни е създадена успешно!")

if __name__ == "__main__":
    initialize_database()
