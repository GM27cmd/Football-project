# src/services/transfers_service.py
from database.db import execute_query
from datetime import datetime

def get_player_id(name):
    result = execute_query(
        "SELECT player_id, club_id FROM players WHERE full_name = ?",
        (name,),
        fetch=True
    )
    return result[0] if result else None

def get_club_id(name):
    result = execute_query(
        "SELECT club_id FROM clubs WHERE name = ?",
        (name,),
        fetch=True
    )
    return result[0][0] if result else None

def transfer_player(player_name, from_club_name, to_club_name, date, fee=None, note=None):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "❌ Невалидна дата, използвай YYYY-MM-DD."

    player = get_player_id(player_name)
    if not player:
        return "❌ Играчът не съществува."

    player_id, current_club_id = player
    from_club_id = get_club_id(from_club_name) if from_club_name else None
    to_club_id = get_club_id(to_club_name)

    if not to_club_id:
        return f"❌ Клубът {to_club_name} не съществува."

    if current_club_id != from_club_id:
        if current_club_id is None and from_club_name in [None, "", "няма"]:
            pass
        else:
            return "❌ Играчът не принадлежи на отбора 'от'."

    if from_club_id == to_club_id:
        return "❌ From и To клубовете не могат да съвпадат."

    try:
        execute_query(
            """INSERT INTO transfers 
               (player_id, from_club_id, to_club_id, transfer_date, fee, note)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (player_id, from_club_id, to_club_id, date, fee, note)
        )
        execute_query(
            "UPDATE players SET club_id = ? WHERE player_id = ?",
            (to_club_id, player_id)
        )
        msg = f"✅ {player_name} трансфериран от {from_club_name or 'свободен'} в {to_club_name} на {date}."
        if fee:
            msg += f" Сума: {fee}"
        if note:
            msg += f" Забележка: {note}"
        return msg
    except Exception as e:
        return f"❌ Грешка при трансфер: {str(e)}"

def list_transfers_by_player(player_name):
    player = get_player_id(player_name)
    if not player:
        return "❌ Играчът не съществува."
    player_id, _ = player

    transfers = execute_query(
        """SELECT t.transfer_date, c_from.name, c_to.name, t.fee, t.note 
           FROM transfers t
           LEFT JOIN clubs c_from ON t.from_club_id = c_from.club_id
           JOIN clubs c_to ON t.to_club_id = c_to.club_id
           WHERE t.player_id = ?
           ORDER BY t.transfer_date""",
        (player_id,),
        fetch=True
    )

    if not transfers:
        return "Няма трансфери за този играч."

    return "\n".join([f"{row[0]}: {row[1] or 'свободен'} → {row[2]} (сума: {row[3] or 'N/A'}, забележка: {row[4] or 'N/A'})" for row in transfers])

def list_transfers_by_club(club_name):
    club_id = get_club_id(club_name)
    if not club_id:
        return "❌ Клубът не съществува."

    transfers = execute_query(
        """SELECT t.transfer_date, p.full_name, c_from.name, c_to.name, t.fee, t.note
           FROM transfers t
           JOIN players p ON t.player_id = p.player_id
           LEFT JOIN clubs c_from ON t.from_club_id = c_from.club_id
           JOIN clubs c_to ON t.to_club_id = c_to.club_id
           WHERE c_from.club_id = ? OR c_to.club_id = ?
           ORDER BY t.transfer_date""",
        (club_id, club_id),
        fetch=True
    )

    if not transfers:
        return "Няма трансфери за този клуб."

    return "\n".join([f"{row[0]}: {row[1]} {row[2] or 'свободен'} → {row[3]} (сума: {row[4] or 'N/A'}, забележка: {row[5] or 'N/A'})" for row in transfers])
