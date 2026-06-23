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
        return "⚠️  Новото и старото ime съвпадат."

    existing = execute_query(
        "SELECT club_id FROM Clubs WHERE LOWER(name) = LOWER(?)",
        (old_name,), fetch=True,
    )
    if not existing:
        return f"❌ Клуб '{old_name}' не е намерен."

    taken = execute_query(
        "SELECT club_id FROM Clubs WHERE LOWER(name) = LOWER(?)",
        (new_name,), fetch=True,
    )
    if taken:
        return f"❌ Клуб с името '{new_name}' вече съществува."

    execute_query(
        "UPDATE Clubs SET name = ? WHERE LOWER(name) = LOWER(?)",
        (new_name, old_name),
    )
    return f"✅ Клубът '{old_name}' е преименуван на '{new_name}'."


# ──────────────────────────────────────────────────────────────
# ИГРАЧИ  (изисква се отбор за да се избегнат двусмислия)
# ──────────────────────────────────────────────────────────────

def rename_player(old_name: str, club_name: str, new_name: str) -> str:
    """
    Преименува играч като задължително се подава и отборът.
    Така "Петър Георгиев от ЦСКА" и "Петър Георгиев от Берое"
    се третират като различни хора.
    """
    old_name  = old_name.strip()
    club_name = club_name.strip()
    new_name  = new_name.strip()

    if not old_name or not new_name:
        return "❌ Имената не могат да са празни."
    if old_name.lower() == new_name.lower():
        return "⚠️  Новото и старото ime съвпадат."

    # Намери клуба
    club = execute_query(
        "SELECT club_id, name FROM Clubs WHERE LOWER(name) LIKE LOWER(?)",
        (f"%{club_name}%",), fetch=True,
    )
    if not club:
        return f"❌ Клуб '{club_name}' не е намерен."
    if len(club) > 1:
        names = ", ".join(c[1] for c in club)
        return f"❌ Намерени няколко клуба: {names}. Уточни."
    club_id, club_full = club[0]

    # Намери играча В този клуб
    players = execute_query(
        """
        SELECT player_id, full_name
        FROM   Players
        WHERE  LOWER(full_name) LIKE LOWER(?)
          AND  club_id = ?
        """,
        (f"%{old_name}%", club_id), fetch=True,
    )
    if not players:
        return (
            f"❌ Играч '{old_name}' не е намерен в {club_full}.\n"
            f"   Провери с: Покажи играчи на {club_full}"
        )
    if len(players) > 1:
        names = ", ".join(p[1] for p in players)
        return f"❌ Намерени няколко играча в {club_full}: {names}. Уточни пълното ime."

    player_id, full_name = players[0]

    # Ново ime уникално ли е?
    taken = execute_query(
        "SELECT player_id FROM Players WHERE LOWER(full_name) = LOWER(?)",
        (new_name,), fetch=True,
    )
    if taken:
        return f"❌ Играч с името '{new_name}' вече съществува."

    execute_query(
        "UPDATE Players SET full_name = ? WHERE player_id = ?",
        (new_name, player_id),
    )
    return f"✅ Играчът '{full_name}' ({club_full}) е преименуван на '{new_name}'."


# ──────────────────────────────────────────────────────────────
# ЛИГИ  (може да се сменят и ime, и сезон)
# ──────────────────────────────────────────────────────────────

def rename_league(old_name: str, old_season: str,
                  new_name: str, new_season: str = None) -> str:
    """
    Преименува лига. Ако е подаден нов сезон, обновява и него.
    Безопасно: всички FK таблици ползват league_id, не (name, season).
    """
    old_name   = old_name.strip()
    new_name   = new_name.strip()
    old_season = old_season.strip()
    new_season = new_season.strip() if new_season else old_season

    if not old_name or not new_name:
        return "❌ Имената не могат да са празни."

    name_same   = old_name.lower() == new_name.lower()
    season_same = old_season == new_season
    if name_same and season_same:
        return "⚠️  Новото ime и сезонът съвпадат със старите."

    # Съществува ли лигата?
    existing = execute_query(
        "SELECT league_id FROM Leagues WHERE LOWER(name) = LOWER(?) AND season = ?",
        (old_name, old_season), fetch=True,
    )
    if not existing:
        return f"❌ Лига '{old_name}' ({old_season}) не е намерена."

    league_id = existing[0][0]

    # Ще се получи ли конфликт след промяната?
    conflict = execute_query(
        """
        SELECT league_id FROM Leagues
        WHERE  LOWER(name) = LOWER(?) AND season = ?
          AND  league_id  != ?
        """,
        (new_name, new_season, league_id), fetch=True,
    )
    if conflict:
        return f"❌ Лига '{new_name}' ({new_season}) вече съществува."

    execute_query(
        "UPDATE Leagues SET name = ?, season = ? WHERE league_id = ?",
        (new_name, new_season, league_id),
    )

    changes = []
    if not name_same:
        changes.append(f"ime: '{old_name}' → '{new_name}'")
    if not season_same:
        changes.append(f"сезон: {old_season} → {new_season}")

    return f"✅ Лигата е обновена — {', '.join(changes)}."
