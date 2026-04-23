import re
from database.db import execute_query, get_connection

from repositories.leagues_repo import (
    get_all_leagues,
    get_league_by_name,
    add_team_to_league,
    create_league,
    get_teams_in_league
)

# =========================
# HELPERS
# =========================

def validate_season(season):
    return re.match(r"\d{4}/\d{4}", season)


def normalize_text(text):
    return text.strip()


# =========================
# LEAGUES
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
    name = normalize_text(name)
    season = normalize_text(season)

    if not validate_season(season):
        return "❌ Невалиден сезон (формат: YYYY/YYYY)"

    if get_league_by_name(name, season):
        return "❌ Лигата вече съществува."

    create_league(name, season)
    return f"✅ Лигата {name} ({season}) е създадена."


# =========================
# TEAMS
# =========================

def add_team_service(club_name, league_name, season):
    club_name = normalize_text(club_name)
    league_name = normalize_text(league_name)
    season = normalize_text(season)

    league = get_league_by_name(league_name, season)
    if not league:
        return "❌ Лигата не съществува."

    league_id = league[0]

    # провери дали вече е добавен
    teams = get_teams_in_league(league_id, season)
    if teams:
        for t in teams:
            if t[0].lower() == club_name.lower():
                return f"❌ {club_name} вече е в лигата."

    result = add_team_to_league(club_name, league_id)

    return result


def list_teams_service(league_name, season):
    league = get_league_by_name(league_name, season)

    if not league:
        return "❌ Лигата не съществува."

    league_id = league[0]

    teams = get_teams_in_league(league_id, season)

    if not teams:
        return "❌ Няма отбори в тази лига."

    result = f"🏆 Отбори в {league_name} ({season}):\n"
    for t in teams:
        result += f"- {t[0]}\n"

    return result


# =========================
# SCHEDULE
# =========================

def show_league_schedule(league_name, season):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT league_id FROM Leagues WHERE name=? AND season=?",
        (league_name, season)
    )
    row = cursor.fetchone()

    if not row:
        return f"❌ Лига '{league_name}' ({season}) не съществува."

    league_id = row[0]

    cursor.execute("""
        SELECT round_no, home_club_id, away_club_id
        FROM Matches
        WHERE league_id=?
        ORDER BY round_no
    """, (league_id,))

    matches = cursor.fetchall()

    if not matches:
        return "❌ Няма генерирана програма."

    output = f"📅 Програма {league_name} ({season}):\n"

    current_round = None

    for round_no, home_id, away_id in matches:
        if round_no != current_round:
            output += f"\n🔹 Кръг {round_no}:\n"
            current_round = round_no

        cursor.execute("SELECT name FROM Clubs WHERE club_id=?", (home_id,))
        home = cursor.fetchone()[0]

        cursor.execute("SELECT name FROM Clubs WHERE club_id=?", (away_id,))
        away = cursor.fetchone()[0]

        output += f"- {home} vs {away}\n"

    return output


# =========================
# SCHEDULE GENERATION (FIXED)
# =========================

def generate_schedule_service(league_name, season):
    league = get_league_by_name(league_name, season)

    if not league:
        return "❌ Лигата не съществува."

    league_id = league[0]

    teams_raw = get_teams_in_league(league_id, season)
    teams = [t[0] for t in teams_raw]

    if len(teams) < 4:
        return "❌ Минимум 4 отбора."

    n = len(teams)
    rounds = n - 1

    schedule = []

    for r in range(rounds):
        for i in range(n // 2):
            home = teams[i]
            away = teams[n - 1 - i]

            if home != away:
                schedule.append((r + 1, home, away))

        teams.insert(1, teams.pop())

    from repositories.matches_repo import insert_match

    for round_no, home, away in schedule:
        insert_match(league_id, round_no, home, away)

    return f"✅ Генерирани {rounds} кръга с по {len(schedule)//rounds} мача."
