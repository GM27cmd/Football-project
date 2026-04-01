import re
from repositories.leagues_repo import *
from database.db import execute_query

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

def create_league_service(name, season):
    if not validate_season(season):
        return "❌ Невалиден сезон (формат: YYYY/YYYY)"

    if get_league(name, season):
        return "❌ Лигата вече съществува."

    create_league(name, season)
    return f"✅ Лигата {name} ({season}) е създадена."


def add_team_service(club_name, league_name, season):
    league_id = get_league(league_name, season)
    if not league_id:
        return "❌ Няма такава лига."

    club_id = get_club_id(club_name)
    if not club_id:
        return "❌ Няма такъв клуб."

    teams = get_teams_in_league(league_id)
    if any(t[0] == club_id for t in teams):
        return "❌ Отборът вече е в лигата."

    add_team_to_league(league_id, club_id)
    return f"✅ {club_name} е добавен в {league_name}."


def list_teams_service(league_name, season):
    league_id = get_league(league_name, season)
    if not league_id:
        return "❌ Няма такава лига."

    teams = get_teams_in_league(league_id)
    if not teams:
        return "⚠️ Няма отбори."

    return "\n".join([f"- {t[1]}" for t in teams])


# =========================
# ROUND ROBIN
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

    # BYE ако е нечетно
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

        # rotation
        team_ids = [team_ids[0]] + [team_ids[-1]] + team_ids[1:-1]

    return f"✅ Генерирана програма с {rounds} кръга."
