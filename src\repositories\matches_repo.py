# src/repositories/matches_repo.py

from database.db import execute_query

# =========================
# MATCHES
# =========================

def get_matches_by_round(league_id, round_no):
    query = """
        SELECT match_id, home_club_id, away_club_id, home_goals, away_goals
        FROM Matches
        WHERE league_id = ? AND round_no = ?
    """
    return execute_query(query, (league_id, round_no), fetch=True)


def get_match_by_id(match_id):
    query = """
        SELECT match_id, home_club_id, away_club_id, home_goals, away_goals
        FROM Matches
        WHERE match_id = ?
    """
    result = execute_query(query, (match_id,), fetch=True)
    return result[0] if result else None


def update_match_score(match_id, home_goals, away_goals):
    query = """
        UPDATE Matches
        SET home_goals = ?, away_goals = ?
        WHERE match_id = ?
    """
    execute_query(query, (home_goals, away_goals, match_id))


# =========================
# GOALS
# =========================

def insert_goal(match_id, player_id, club_id, minute):
    query = """
        INSERT INTO Goals (match_id, player_id, minute)
        VALUES (?, ?, ?)
    """
    execute_query(query, (match_id, player_id, minute))


# =========================
# CARDS
# =========================

def insert_card(match_id, player_id, club_id, minute, card_type):
    query = """
        INSERT INTO Cards (match_id, player_id, type, minute)
        VALUES (?, ?, ?, ?)
    """
    execute_query(query, (match_id, player_id, card_type, minute))


# =========================
# EVENTS
# =========================

def get_goals(match_id):
    query = """
        SELECT g.minute, p.full_name, c.name
        FROM Goals g
        JOIN Players p ON g.player_id = p.player_id
        JOIN Clubs c ON p.club_id = c.club_id
        WHERE g.match_id = ?
    """
    return execute_query(query, (match_id,), fetch=True)


def get_cards(match_id):
    query = """
        SELECT c.minute, p.full_name, c.type
        FROM Cards c
        JOIN Players p ON c.player_id = p.player_id
        WHERE c.match_id = ?
    """
    return execute_query(query, (match_id,), fetch=True)
