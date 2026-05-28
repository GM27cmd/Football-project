# src/repositories/matches_repo.py

from database.db import execute_query


# =========================
# MATCHES
# =========================

def insert_match(league_id, round_no, home_name, away_name):
    query = """
        INSERT INTO Matches (league_id, round_no, home_club_id, away_club_id, status)
        VALUES (
            ?,
            ?,
            (SELECT club_id FROM Clubs WHERE name = ?),
            (SELECT club_id FROM Clubs WHERE name = ?),
            'scheduled'
        )
    """
    execute_query(query, (league_id, round_no, home_name, away_name))


def get_matches_by_round(league_id, round_no):
    query = """
        SELECT
            m.match_id,
            hc.name  AS home_team,
            ac.name  AS away_team,
            m.home_goals,
            m.away_goals,
            m.status
        FROM Matches m
        JOIN Clubs hc ON m.home_club_id = hc.club_id
        JOIN Clubs ac ON m.away_club_id = ac.club_id
        WHERE m.league_id = ? AND m.round_no = ?
        ORDER BY m.match_id
    """
    return execute_query(query, (league_id, round_no), fetch=True)


def get_match_by_id(match_id):
    """
    Връща:
        (match_id, home_name, away_name, home_goals, away_goals,
         status, home_club_id, away_club_id)
    Индекси: 0          1          2         3           4
             5       6              7
    """
    query = """
        SELECT
            m.match_id,
            hc.name          AS home_name,
            ac.name          AS away_name,
            m.home_goals,
            m.away_goals,
            m.status,
            m.home_club_id,
            m.away_club_id
        FROM Matches m
        JOIN Clubs hc ON m.home_club_id = hc.club_id
        JOIN Clubs ac ON m.away_club_id = ac.club_id
        WHERE m.match_id = ?
    """
    result = execute_query(query, (match_id,), fetch=True)
    return result[0] if result else None


def update_match_score(match_id, home_goals, away_goals):
    """Записва резултат и слага статус 'played'."""
    query = """
        UPDATE Matches
        SET home_goals = ?, away_goals = ?, status = 'played'
        WHERE match_id = ?
    """
    execute_query(query, (home_goals, away_goals, match_id))


# =========================
# GOALS
# =========================

def insert_goal(match_id, player_id, club_id, minute):
    query = """
        INSERT INTO Goals (match_id, player_id, club_id, minute)
        VALUES (?, ?, ?, ?)
    """
    execute_query(query, (match_id, player_id, club_id, minute))


def get_goals(match_id):
    """Връща: (minute, full_name, club_name)"""
    query = """
        SELECT g.minute, p.full_name, c.name AS club_name
        FROM Goals g
        JOIN Players p ON g.player_id = p.player_id
        JOIN Clubs  c ON g.club_id    = c.club_id
        WHERE g.match_id = ?
        ORDER BY g.minute
    """
    return execute_query(query, (match_id,), fetch=True)


# =========================
# CARDS
# =========================

def insert_card(match_id, player_id, club_id, minute, card_type):
    query = """
        INSERT INTO Cards (match_id, player_id, club_id, minute, card_type)
        VALUES (?, ?, ?, ?, ?)
    """
    execute_query(query, (match_id, player_id, club_id, minute, card_type))


def get_cards(match_id):
    """Връща: (minute, full_name, card_type, club_name)"""
    query = """
        SELECT c.minute, p.full_name, c.card_type, cl.name AS club_name
        FROM Cards c
        JOIN Players p ON c.player_id = p.player_id
        JOIN Clubs  cl ON c.club_id   = cl.club_id
        WHERE c.match_id = ?
        ORDER BY c.minute
    """
    return execute_query(query, (match_id,), fetch=True)
