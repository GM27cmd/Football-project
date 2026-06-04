# src/repositories/standings_repo.py
#
# Отговаря САМО за заявки към БД, свързани с класирането.
# Без логика, без форматиране — само SELECT.
 
from database.db import execute_query
 
 
def get_league_id_by_name_season(league_name: str, season: str):
    """Връща league_id по име и сезон, или None ако не съществува."""
    result = execute_query(
        "SELECT league_id FROM Leagues WHERE name = ? AND season = ?",
        (league_name, season),
        fetch=True,
    )
    return result[0][0] if result else None
 
 
def get_clubs_in_league(league_id: int):
    """
    Връща списък с (club_id, club_name) за всички отбори в лигата.
    Сортирано по име за стабилност при равни показатели.
    """
    return execute_query(
        """
        SELECT c.club_id, c.name
        FROM   League_Teams lt
        JOIN   Clubs c ON lt.club_id = c.club_id
        WHERE  lt.league_id = ?
        ORDER  BY c.name
        """,
        (league_id,),
        fetch=True,
    )
 
 
def get_played_matches(league_id: int):
    """
    Връща всички изиграни мачове (status = 'played') за лигата
    с ненулеви резултати. Редовете: (match_id, home_id, away_id, home_goals, away_goals).
    """
    return execute_query(
        """
        SELECT match_id,
               home_club_id,
               away_club_id,
               home_goals,
               away_goals
        FROM   Matches
        WHERE  league_id  = ?
          AND  status     = 'played'
          AND  home_goals IS NOT NULL
          AND  away_goals IS NOT NULL
        """,
        (league_id,),
        fetch=True,
    )
 