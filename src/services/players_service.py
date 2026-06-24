# src/services/players_service.py
import re
from datetime import datetime
from database.db import execute_query

# ──────────────────────────────────────────────────────────────
# КАРТА НА ПОЗИЦИИ
# Приема разширени позиции и ги преобразува към 4-те стандартни:
# GK (вратар), DF (защитник), MF (полузащитник), FW (нападател)
# ──────────────────────────────────────────────────────────────
POSITION_MAP = {
    # Вратари
    'GK': 'GK', 'POR': 'GK', 'PORT': 'GK',
    # Защитници
    'DF': 'DF', 'CB': 'DF', 'LB': 'DF', 'RB': 'DF',
    'LWB': 'DF', 'RWB': 'DF', 'SW': 'DF', 'DEF': 'DF',
    'BEK': 'DF', 'WB': 'DF',
    # Полузащитници
    'MF': 'MF', 'CM': 'MF', 'CAM': 'MF', 'CDM': 'MF',
    'LM': 'MF', 'RM': 'MF', 'DM': 'MF', 'AM': 'MF',
    'MID': 'MF', 'DMF': 'MF', 'AMF': 'MF', 'OM': 'MF',
    'BOX': 'MF', 'B2B': 'MF',
    # Нападатели
    'FW': 'FW', 'ST': 'FW', 'CF': 'FW', 'LW': 'FW',
    'RW': 'FW', 'SS': 'FW', 'IF': 'FW', 'ATT': 'FW',
    'NAP': 'FW', 'FOR': 'FW', 'CTR': 'FW',
}

VALID_POSITIONS = {'GK', 'DF', 'MF', 'FW'}


# ──────────────────────────────────────────────────────────────
# ПОМОЩНИ ФУНКЦИИ
# ──────────────────────────────────────────────────────────────

def normalize_position(pos: str):
    """
    Приема всяка позиция (LW, ST, CB, CAM...) и връща
    стандартната (FW, FW, DF, MF...) или None ако е непозната.
    """
    return POSITION_MAP.get(pos.upper())


def get_club_id_by_name(club_name):
    result = execute_query(
        "SELECT club_id FROM Clubs WHERE name = ?",
        (club_name,), fetch=True
    )
    return result[0][0] if result else None


def validate_number(number):
    return 1 <= number <= 99


def validate_birth_date(birth_date):
    try:
        datetime.strptime(birth_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# ──────────────────────────────────────────────────────────────
# CRUD ОПЕРАЦИИ
# ──────────────────────────────────────────────────────────────

def add_player(full_name, birth_date, nationality, position, number, club_name):
    # Нормализиране на позицията
    std_position = normalize_position(position)
    if not std_position:
        known = ", ".join(sorted(POSITION_MAP.keys()))
        return (
            f"❌ Непозната позиция '{position}'.\n"
            f"   Поддържани: {known}"
        )

    if not validate_number(number):
        return "❌ Невалиден номер. Допустими: 1–99."
    if not validate_birth_date(birth_date):
        return "❌ Невалидна дата на раждане. Формат: ГГГГ-ММ-ДД."

    club_id = get_club_id_by_name(club_name)
    if not club_id:
        return f"❌ Няма такъв клуб: '{club_name}'"

    # Уникален номер в клуба
    existing = execute_query(
        "SELECT player_id FROM Players WHERE club_id = ? AND number = ?",
        (club_id, number), fetch=True
    )
    if existing:
        return f"❌ Номер {number} вече е зает в {club_name}."

    execute_query(
        """
        INSERT INTO Players
            (full_name, birth_date, nationality, position, number, club_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (full_name, birth_date, nationality, std_position, number, club_id)   # ← вече са 6
    )

    # Показваме оригиналната позиция + стандартната ако се различават
    pos_note = f" ({position} → {std_position})" if position.upper() != std_position else ""
    return f"✅ Играчът {full_name} беше добавен в {club_name} като {std_position}{pos_note}."


def list_players_by_club(club_name):
    club_id = get_club_id_by_name(club_name)
    if not club_id:
        return f"❌ Няма такъв клуб: '{club_name}'"

    players = execute_query(
        """
        SELECT full_name, position, number, nationality, status
        FROM   Players
        WHERE  club_id = ?
        ORDER  BY number
        """,
        (club_id,), fetch=True
    )
    if not players:
        return f"⚠️ Няма добавени играчи за {club_name}."

    result = f"👕 Играчите на {club_name}:\n"
    for p in players:
        result += f"  №{p[2]:<4} {p[0]:<25} {p[1]:<4} {p[3]}\n"
    return result


def update_player_number(full_name, new_number):
    if not validate_number(new_number):
        return "❌ Невалиден номер. Допустими: 1–99."

    player = execute_query(
        "SELECT player_id, club_id FROM Players WHERE full_name = ?",
        (full_name,), fetch=True
    )
    if not player:
        return f"❌ Няма такъв играч: '{full_name}'"

    player_id, club_id = player[0]

    existing = execute_query(
        "SELECT player_id FROM Players WHERE club_id = ? AND number = ?",
        (club_id, new_number), fetch=True
    )
    if existing:
        return f"❌ Номер {new_number} вече е зает в този клуб."

    execute_query(
        "UPDATE Players SET number = ? WHERE player_id = ?",
        (new_number, player_id)
    )
    return f"✅ Играчът {full_name} вече носи номер {new_number}."


def delete_player(full_name):
    player = execute_query(
        "SELECT player_id FROM Players WHERE full_name = ?",
        (full_name,), fetch=True
    )
    if not player:
        return f"❌ Няма такъв играч: '{full_name}'"

    execute_query("DELETE FROM Players WHERE full_name = ?", (full_name,))
    return f"✅ Играчът {full_name} беше изтрит."
