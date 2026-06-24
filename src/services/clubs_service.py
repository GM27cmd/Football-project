# src/services/clubs_service.py
from database.db import execute_query

def add_club(name, city=None, founded_year=None, league_id=None):
    if not name:
        return "❌ Името на клуба не може да е празно."

    # Стойности по подразбиране ако не са подадени
    city         = city         or "Неизвестен"
    founded_year = founded_year or 0

    # Проверка за дублиране
    existing = execute_query(
        "SELECT club_id FROM Clubs WHERE name = ?",
        (name,), fetch=True
    )
    if existing:
        return f"❌ Клуб '{name}' вече съществува."

    execute_query(
        "INSERT INTO Clubs (name, city, founded_year, league_id) VALUES (?, ?, ?, ?)",
        (name, city, founded_year, league_id)
    )
    return f"✅ Клубът '{name}' беше добавен ({city})."


def get_all_clubs():
    clubs = execute_query(
        "SELECT club_id, name, city, founded_year FROM Clubs ORDER BY name",
        fetch=True
    )
    if not clubs:
        return "⚠️ Няма добавени клубове."
    result = "📋 Списък на клубовете:\n"
    for club in clubs:
        year = f" | осн. {club[3]}" if club[3] else ""
        result += f"  - {club[1]} | {club[2]}{year}\n"
    return result


def delete_club(name):
    club = execute_query(
        "SELECT club_id FROM Clubs WHERE name = ?",
        (name,), fetch=True
    )
    if not club:
        return f"❌ Няма такъв клуб: '{name}'"
    execute_query("DELETE FROM Clubs WHERE name = ?", (name,))
    return f"✅ Клубът '{name}' беше изтрит."
