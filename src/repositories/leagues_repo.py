from database.db import execute_query

# =========================
# LEAGUES
# =========================

def create_league(name, season):
    query = "INSERT INTO Leagues (name, season) VALUES (?, ?)"
    execute_query(query, (name, season))


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

# =========================
# LEAGUE TEAMS
# =========================

def add_team_to_league(league_id, club_id):
    query = "INSERT INTO League_Teams (league_id, club_id) VALUES (?, ?)"
    execute_query(query, (league_id, club_id))


def get_teams_in_league(league_id):
    query = """
        SELECT c.club_id, c.name
        FROM League_Teams lt
        JOIN Clubs c ON lt.club_id = c.club_id
        WHERE lt.league_id = ?
    """
    return execute_query(query, (league_id,), fetch=True)


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
