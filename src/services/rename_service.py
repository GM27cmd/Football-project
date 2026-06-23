# src/services/rename_service.py
#
# Преименуване на клубове, играчи и лиги.
# Структура: handler → service → DB (execute_query)

from database.db import execute_query


# ──────────────────────────────────────────────────────────────
# КЛУБОВЕ
# ──────────────────────────────────────────────────────────────

def rename_club(old_name: str, new_name: str) -> str:
    old_name = old_name.strip()
    new_name = new_name.strip()

    if not old_name or not new_name:
        return "❌ Имената не могат да са празни."
    if old_name.lower() == new_name.lower():
        return "⚠️  Новото и старото име съвпадат."

    # Съществува ли клубът?
    existing = execute_query(
        "SELECT club_id FROM Clubs WHERE LOWER(name) = LOWER(?)",
        (old_name,),
        fetch=True,
    )
    if not existing:
        return f"❌ Клуб '{old_name}' не е намерен."

    # Заето ли е новото име?
    taken = execute_query(
        "SELECT club_id FROM Clubs WHERE LOWER(name) = LOWER(?)",
        (new_name,),
        fetch=True,
    )
    if taken:
        return f"❌ Клуб с името '{new_name}' вече съществува."

    execute_query(
        "UPDATE Clubs SET name = ? WHERE LOWER(name) = LOWER(?)",
        (new_name, old_name),
    )
    return f"✅ Клубът '{old_name}' е преименуван на '{new_name}'."


# ──────────────────────────────────────────────────────────────
# ИГРАЧИ
# ──────────────────────────────────────────────────────────────

def rename_player(old_name: str, new_name: str) -> str:
    old_name = old_name.strip()
    new_name = new_name.strip()

    if not old_name or not new_name:
        return "❌ Имената не могат да са празни."
    if old_name.lower() == new_name.lower():
        return "⚠️  Новото и старото име съвпадат."

    # Намери играча
    players = execute_query(
        "SELECT player_id, full_name FROM Players WHERE LOWER(full_name) LIKE LOWER(?)",
        (f"%{old_name}%",),
        fetch=True,
    )

    if not players:
        return f"❌ Играч '{old_name}' не е намерен."
    if len(players) > 1:
        names = ", ".join(p[1] for p in players)
        return f"❌ Намерени няколко играча: {names}. Уточни пълното ime."

    player_id, full_name = players[0]

    # Заето ли е новото ime?
    taken = execute_query(
        "SELECT player_id FROM Players WHERE LOWER(full_name) = LOWER(?)",
        (new_name,),
        fetch=True,
    )
    if taken:
        return f"❌ Играч с името '{new_name}' вече съществува."

    execute_query(
        "UPDATE Players SET full_name = ? WHERE player_id = ?",
        (new_name, player_id),
    )
    return f"✅ Играчът '{full_name}' е преименуван на '{new_name}'."


# ──────────────────────────────────────────────────────────────
# ЛИГИ
# ──────────────────────────────────────────────────────────────

def rename_league(old_name: str, season: str, new_name: str) -> str:
    old_name = old_name.strip()
    new_name = new_name.strip()
    season   = season.strip()

    if not old_name or not new_name:
        return "❌ Имената не могат да са празни."
    if old_name.lower() == new_name.lower():
        return "⚠️  Новото и старото име съвпадат."

    # Съществува ли лигата?
    existing = execute_query(
        "SELECT league_id FROM Leagues WHERE LOWER(name) = LOWER(?) AND season = ?",
        (old_name, season),
        fetch=True,
    )
    if not existing:
        return f"❌ Лига '{old_name}' ({season}) не е намерена."

    # Заето ли е новото ime за същия сезон?
    taken = execute_query(
        "SELECT league_id FROM Leagues WHERE LOWER(name) = LOWER(?) AND season = ?",
        (new_name, season),
        fetch=True,
    )
    if taken:
        return f"❌ Лига '{new_name}' ({season}) вече съществува."

    execute_query(
        "UPDATE Leagues SET name = ? WHERE LOWER(name) = LOWER(?) AND season = ?",
        (new_name, old_name, season),
    )
    return f"✅ Лигата '{old_name}' ({season}) е преименувана на '{new_name}'."
