# src/services/clubs_service.py
from database.db import execute_query

def add_club(name, city=None, founded_year=None, league_id=None):
    if not name:
        return "❌ Името на клуба не може да е празно."

    # Проверка за дублиране
    query_check = "SELECT club_id FROM Clubs WHERE name = ?"
    existing = execute_query(query_check, (name,), fetch=True)
    if existing:
        return f"❌ Клуб {name} вече съществува."

    query = "INSERT INTO Clubs (name, city, founded_year, league_id) VALUES (?, ?, ?, ?)"
    execute_query(query, (name, city, founded_year, league_id))
    return f"✅ Клубът {name} беше добавен."

def get_all_clubs():
    query = "SELECT club_id, name, city FROM Clubs ORDER BY name"
    clubs = execute_query(query, fetch=True)
    if not clubs:
        return "⚠️ Няма добавени клубове."
    result = "Списък на клубовете:\n"
    for club in clubs:
        result += f"- {club[1]} | {club[2]}\n"
    return result

def delete_club(name):
    query_check = "SELECT club_id FROM Clubs WHERE name = ?"
    club = execute_query(query_check, (name,), fetch=True)
    if not club:
        return f"❌ Няма такъв клуб: {name}"
    query_delete = "DELETE FROM Clubs WHERE name = ?"
    execute_query(query_delete, (name,))
    return f"✅ Клубът {name} беше изтрит."
