import re
from repositories.leagues_repo import *
from repositories.leagues_repo import get_all_leagues
from repositories.leagues_repo import add_team_to_league
from repositories.leagues_repo import get_teams_in_league
from repositories.leagues_repo import add_team_to_league, league_exists_by_name
from database.db import execute_query, get_connection

# =========================
# HELPERS
# =========================

def get_club_id(name):
    result = execute_query("SELECT club_id FROM Clubs WHERE name = ?", (name,), fetch=True)
    return result[0][0] if result else None

def validate_season(season):
    return re.match(r"\d{4}/\d{4}", season)

# =========================
# LEAGUE CRUD
# =========================
def show_leagues():
    leagues = get_all_leagues()

    if not leagues:
        return "❌ Няма създадени лиги."

    result = "🏆 ЛИГИ:\n"
    for lg in leagues:
        result += f"- {lg[1]} ({lg[2]})\n"

    return result

def create_league_service(name, season):
    if not validate_season(season):
        return "❌ Невалиден сезон (формат: YYYY/YYYY)"

    if get_league(name, season):
        return "❌ Лигата вече съществува."

    create_league(name, season)
    return f"✅ Лигата {name} ({season}) е създадена."

def add_team_service(club_name, league_name, season):
    # 🔥 проверка дали има такава лига въобще
    if not league_exists_by_name(league_name):
        return f"❌ Няма лига с име '{league_name}'. Провери правописа."

    return add_team_to_league(club_name, league_name, season)

def list_teams_service(league_name, season):
    teams = get_teams_in_league(league_name, season)

    if not teams:
        return "❌ Няма отбори в тази лига."

    result = f"🏆 Отбори в {league_name} ({season}):\n"
    for t in teams:
        result += f"- {t[0]}\n"

    return result

# =========================
# SHOW SCHEDULEС
# =========================

def show_league_schedule(league_name, season):
    conn = get_connection()
    cursor = conn.cursor()

    # Взимаме ID на лигата
    cursor.execute("SELECT league_id FROM Leagues WHERE name=? AND season=?", (league_name, season))
    row = cursor.fetchone()
    if not row:
        return f"❌ Лига '{league_name}' сезон {season} не съществува."
    league_id = row[0]

    # Взимаме мачовете
    cursor.execute("""
        SELECT round_no, home_club_id, away_club_id 
        FROM Matches 
        WHERE league_id=? 
        ORDER BY round_no
    """, (league_id,))
    matches = cursor.fetchall()

    if not matches:
        return "❌ Все още няма генерирана програма за тази лига."

    schedule_text = f"Програма за {league_name} {season}:\n"
    current_round = None

    for match in matches:
        round_no, home_id, away_id = match

        if round_no != current_round:
            schedule_text += f"\nКръг {round_no}:\n"
            current_round = round_no

        # взимаме имената правилно
        cursor.execute("SELECT name FROM Clubs WHERE club_id=?", (home_id,))
        home_name = cursor.fetchone()[0]

        cursor.execute("SELECT name FROM Clubs WHERE club_id=?", (away_id,))
        away_name = cursor.fetchone()[0]

        schedule_text += f"- {home_name} vs {away_name}\n"

    return schedule_text

# =========================
# ROUND ROBIN SCHEDULE
# =========================

def generate_schedule_service(league_name, season):
    league_id = get_league(league_name, season)
    if not league_id:
        return "❌ Няма такава лига."

    if league_has_matches(league_id):
        return "❌ Вече има генерирана програма."

    teams = get_teams_in_league(league_id)
    team_ids = [t[0] for t in teams]

    if len(team_ids) < 4:
        return "❌ Минимум 4 отбора."

    # Добавяме BYE ако е нечетно
    if len(team_ids) % 2 != 0:
        team_ids.append(None)

    n = len(team_ids)
    rounds = n - 1

    for r in range(rounds):
        for i in range(n // 2):
            home = team_ids[i]
            away = team_ids[n - 1 - i]

            if home is None or away is None:
                continue

            insert_match(league_id, r + 1, home, away)

        # ротация на отборите
        team_ids = [team_ids[0]] + [team_ids[-1]] + team_ids[1:-1]

    return f"✅ Генерирана програма с {rounds} кръга."
