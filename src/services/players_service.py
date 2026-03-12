# src/services/players_service.py
import re
from datetime import datetime
from database.db import execute_query
from services.clubs_service import get_all_clubs  # за валидация на клубове

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_club_id_by_name(club_name):
    """Връща club_id по име на клуба."""
    query = "SELECT club_id FROM Clubs WHERE name = ?"
    result = execute_query(query, (club_name,), fetch=True)
    if result:
        return result[0][0]
    return None

def validate_position(position):
    return position in ('GK', 'DF', 'MF', 'FW')

def validate_number(number):
    return 1 <= number <= 99

def validate_birth_date(birth_date):
    try:
        datetime.strptime(birth_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# =====================================================
# CRUD OPERATIONS
# =====================================================

def add_player(full_name, birth_date, nationality, position, number, club_name):
    if not validate_position(position):
        return f"❌ Невалидна позиция. Допустими: GK, DF, MF, FW."
    if not validate_number(number):
        return f"❌ Невалиден номер. Допустими 1-99."
    if not validate_birth_date(birth_date):
        return f"❌ Невалидна дата на раждане. Формат: YYYY-MM-DD."

    club_id = get_club_id_by_name(club_name)
    if not club_id:
        return f"❌ Няма такъв клуб: {club_name}"

    # Проверка за уникален номер в клуба
    query_check = "SELECT player_id FROM Players WHERE club_id = ? AND number = ?"
    existing = execute_query(query_check, (club_id, number), fetch=True)
    if existing:
        return f"❌ Номер {number} вече е зает в {club_name}."

    query = """
        INSERT INTO Players (full_name, birth_date, nationality, position, number, club_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    execute_query(query, (full_name, birth_date, nationality, position, number, club_id))
    return f"✅ Играчът {full_name} беше добавен в {club_name}."

def list_players_by_club(club_name):
    club_id = get_club_id_by_name(club_name)
    if not club_id:
        return f"❌ Няма такъв клуб: {club_name}"

    query = "SELECT full_name, position, number, status FROM Players WHERE club_id = ? ORDER BY number"
    players = execute_query(query, (club_id,), fetch=True)
    if not players:
        return f"⚠️ Няма добавени играчи за {club_name}."
    
    result = f"Играчите на {club_name}:\n"
    for p in players:
        result += f"- {p[0]} | {p[1]} | №{p[2]} | {p[3]}\n"
    return result

def update_player_number(full_name, new_number):
    if not validate_number(new_number):
        return f"❌ Невалиден номер. Допустими 1-99."

    # Намери играча
    query = "SELECT player_id, club_id FROM Players WHERE full_name = ?"
    player = execute_query(query, (full_name,), fetch=True)
    if not player:
        return f"❌ Няма такъв играч: {full_name}"

    player_id, club_id = player[0]

    # Проверка дали новият номер е свободен в клуба
    query_check = "SELECT player_id FROM Players WHERE club_id = ? AND number = ?"
    existing = execute_query(query_check, (club_id, new_number), fetch=True)
    if existing:
        return f"❌ Номер {new_number} вече е зает в този клуб."

    # Актуализирай
    query_update = "UPDATE Players SET number = ? WHERE player_id = ?"
    execute_query(query_update, (new_number, player_id))
    return f"✅ Играчът {full_name} има нов номер: {new_number}"

def delete_player(full_name):
    # Намери играча
    query = "SELECT player_id FROM Players WHERE full_name = ?"
    player = execute_query(query, (full_name,), fetch=True)
    if not player:
        return f"❌ Няма такъв играч: {full_name}"

    query_delete = "DELETE FROM Players WHERE full_name = ?"
    execute_query(query_delete, (full_name,))
    return f"✅ Играчът {full_name} беше изтрит."
