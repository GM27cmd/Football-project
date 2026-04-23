from database.db import execute_query

# =========================
# LEAGUES
# =========================

def create_league(name, season):
    query = "INSERT INTO Leagues (name, season) VALUES (?, ?)"
    execute_query(query, (name, season))

def get_all_leagues():
    query = """
        SELECT league_id, name, season
        FROM Leagues
    """
    return execute_query(query, fetch=True)

def get_league(name, season):
    query = "SELECT league_id FROM Leagues WHERE name = ? AND season = ?"
    result = execute_query(query, (name, season), fetch=True)
    return result[0][0] if result else None

def get_matches_by_league(cursor, league_id):
    cursor.execute("""
        SELECT round_no, home_club_id, away_club_id
        FROM matches
        WHERE league_id = ?
        ORDER BY round_no, home_club_id
    """, (league_id,))
    return cursor.fetchall()

def league_exists_by_name(league_name):
    query = "SELECT * FROM Leagues WHERE name=?"
    result = execute_query(query, (league_name,), fetch=True)
    return bool(result)


def get_league_by_name_and_season(name, season):
    query = """
        SELECT league_id, name, season
        FROM Leagues
        WHERE name = ? AND season = ?
    """
    result = execute_query(query, (name, season), fetch=True)
    return result[0] if result else None
# =========================
# LEAGUE TEAMS
# =========================

def add_team_to_league(club_name, league_name, season):
    # намираме лига
    league = execute_query(
        "SELECT league_id FROM Leagues WHERE name=? AND season=?",
        (league_name, season),
        fetch=True
    )

    if not league:
        return "❌ Лигата не съществува. Провери име и сезон (напр. 2025/2026)."

    league_id = league[0][0]

    # намираме клуб
    club = execute_query(
        "SELECT club_id FROM Clubs WHERE name=?",
        (club_name,),
        fetch=True
    )

    if not club:
        return "❌ Клубът не съществува."

    club_id = club[0][0]

    # 🔥 ПРОВЕРКА дали вече е добавен
    exists = execute_query(
        "SELECT * FROM League_Teams WHERE league_id=? AND club_id=?",
        (league_id, club_id),
        fetch=True
    )

    if exists:
        return f"⚠️ {club_name} вече е в {league_name} ({season})."

    # добавяне
    execute_query(
        "INSERT INTO League_Teams (league_id, club_id) VALUES (?, ?)",
        (league_id, club_id)
    )

    return f"✅ {club_name} добавен в {league_name} ({season})."


def get_teams_in_league(league_name, season):
    query = """
        SELECT c.name
        FROM League_Teams lt
        JOIN Leagues l ON lt.league_id = l.league_id
        JOIN Clubs c ON lt.club_id = c.club_id
        WHERE l.name = ? AND l.season = ?
    """
    return execute_query(query, (league_name, season), fetch=True)


def remove_team_from_league(league_id, club_id):
    query = "DELETE FROM League_Teams WHERE league_id = ? AND club_id = ?"
    execute_query(query, (league_id, club_id))


# =========================
# MATCHES
# =========================

def insert_match(league_id, round_no, home_id, away_id):
    query = """
        INSERT INTO Matches (league_id, round_no, home_club_id, away_club_id)
        VALUES (?, ?, ?, ?)
    """
    execute_query(query, (league_id, round_no, home_id, away_id))


def league_has_matches(league_id):
    query = "SELECT match_id FROM Matches WHERE league_id = ? LIMIT 1"
    return execute_query(query, (league_id,), fetch=True)


def delete_matches_by_league(league_id):
    query = "DELETE FROM Matches WHERE league_id = ?"
    execute_query(query, (league_id,))
