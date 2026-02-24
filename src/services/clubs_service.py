from src.database.db import execute_query

def add_club(name):
    query = "INSERT INTO clubs (name) VALUES (?);"
    execute_query(query, (name,))
    return f"Клубът {name} беше добавен."


def get_all_clubs():
    query = "SELECT id, name FROM clubs;"
    clubs = execute_query(query, fetch=True)

    if not clubs:
        return "Няма добавени клубове."

    result = "Списък с клубове:\n"
    for club in clubs:
        result += f"{club[0]} - {club[1]}\n"

    return result


def delete_club(name):
    query = "DELETE FROM clubs WHERE name = ?;"
    execute_query(query, (name,))
    return f"Клубът {name} беше изтрит (ако съществува)."
