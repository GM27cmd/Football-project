import sqlite3

def initialize_database():
    # Свързваме се или създаваме базата football.db
    conn = sqlite3.connect("football.db")
    cursor = conn.cursor()

    # Включваме foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Прочитаме schema.sql и създаваме таблиците
    with open("sql/schema.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)

    # Прочитаме test_data.sql и добавяме тестовите данни
    with open("sql/test_data.sql", "r", encoding="utf-8") as f:
        test_data_sql = f.read()
        cursor.executescript(test_data_sql)

    # Запазваме промените
    conn.commit()
    conn.close()

    print("Базата данни 'football.db' е създадена успешно с тестови данни!")

if __name__ == "__main__":
    initialize_database()