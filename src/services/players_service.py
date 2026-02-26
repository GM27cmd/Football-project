from src.database.db import execute_query
from datetime import datetime


VALID_POSITIONS = {"GK", "DF", "MF", "FW"}


def validate_birth_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_club_id_by_name(club_name):
    query = "SELECT id FROM clubs WHERE name = ?;"
    result = execute_query(query, (club_name,), fetch=True)
    return result[0][0] if result else None


def add_player(full_name, birth_date, nationality, position, number, club_name):
    if position not in VALID_POSITIONS:
        return "Невалидна позиция. Използвай: GK, DF, MF, FW."

    if not (1 <= number <= 99):
        return "Номерът трябва да е между 1 и 99."

    if not validate_birth_date(birth_date):
        return "Датата трябва да е във формат YYYY-MM-DD."

    club_id = get_club_id_by_name(club_name)
    if not club_id:
        return f"Клубът {club_name} не съществува."

    query = """
        INSERT INTO players 
        (full_name, birth_date, nationality, position, number, club_id)
        VALUES (?, ?, ?, ?, ?, ?);
    """

    execute_query(query, (full_name, birth_date, nationality, position, number, club_id))

    return f"Играчът {full_name} беше добавен в {club_name}."


def list_players_by_club(club_name):
    club_id = get_club_id_by_name(club_name)
    if not club_id:
        return "Няма такъв клуб."

    query = """
        SELECT full_name, position, number, status
        FROM players
        WHERE club_id = ?;
    """

    players = execute_query(query, (club_id,), fetch=True)

    if not players:
        return "Няма играчи в този клуб."

    result = f"Играчите на {club_name}:\n"
    for p in players:
        result += f"{p[0]} | {p[1]} | №{p[2]} | {p[3]}\n"

    return result


def update_player_number(full_name, new_number):
    if not (1 <= new_number <= 99):
        return "Номерът трябва да е между 1 и 99."

    query = "UPDATE players SET number = ? WHERE full_name = ?;"
    execute_query(query, (new_number, full_name))

    return f"Номерът на {full_name} беше сменен на {new_number}."


def delete_player(full_name):
    query = "DELETE FROM players WHERE full_name = ?;"
    execute_query(query, (full_name,))
    return f"Играчът {full_name} беше изтрит."
