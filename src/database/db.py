import sqlite3

DB_NAME = "football.db"


def execute_query(query, params=(), fetch=False):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(query, params)

    if fetch:
        result = cursor.fetchall()
    else:
        result = None

    connection.commit()
    connection.close()

    return result
