# src/services/matches_service.py

from database.db import execute_query
from repositories.matches_repo import (
    get_matches_by_round,
    get_match_by_id,
    update_match_score,
    insert_goal,
    insert_card,
    get_goals,
    get_cards
)

# =========================
# GLOBAL CONTEXT (избран мач)
# =========================
current_match_id = None


# =========================
# MATCH SELECTION
# =========================
def select_match(match_id: int):
    global current_match_id

    match = get_match_by_id(match_id)
    if not match:
        return "❌ Няма мач с такъв ID."

    current_match_id = match_id
    return f"✅ Избран мач #{match_id}"


def get_current_match():
    if not current_match_id:
        return None
    return get_match_by_id(current_match_id)


# =========================
# ROUND MATCHES
# =========================
from repositories.matches_repo import get_matches_by_round
from repositories.leagues_repo import get_league_by_name_and_season


def show_round(league_name: str, season: str, round_no: int):
    league = get_league_by_name_and_season(league_name, season)

    if not league:
        return "❌ Лигата не съществува."

    league_id = league[0]

    matches = get_matches_by_round(league_id, round_no)

    if not matches:
        return f"❌ Няма мачове за кръг {round_no}."

    result = f"📅 Кръг {round_no} - {league_name} ({season})\n\n"

    for m in matches:
        match_id = m[0]
        home = m[1]
        away = m[2]
        home_goals = m[3]
        away_goals = m[4]
        status = m[5]

        if home_goals is None or away_goals is None:
            score = "⏳ неигран"
        else:
            score = f"{home_goals}:{away_goals}"

        result += f"🆔 {match_id} | {home} vs {away} с| {score} | {status}\n"

    return result


# =========================
# RESULT LOGIC
# =========================
def set_result(home, away, home_goals, away_goals):
    match = get_current_match()

    if not match:
        return "❌ Няма избран мач."

    match_id = match[0]

    # проверка дали вече има резултат
    if match[3] is not None or match[4] is not None:
        return "❌ Този мач вече има въведен резултат."

    update_match_score(match_id, home_goals, away_goals)

    return f"✅ Записано: {home}-{away} {home_goals}:{away_goals} (мач #{match_id})"


# =========================
# VALIDATION HELPERS
# =========================
def _validate_minute(minute: int):
    return 1 <= minute <= 120


def _get_player(player_id: int):
    query = "SELECT player_id, full_name, club_id FROM Players WHERE player_id = ?"
    res = execute_query(query, (player_id,), fetch=True)
    return res[0] if res else None


# =========================
# GOALS
# =========================
def add_goal(player_id: int, minute: int):
    match = get_current_match()

    if not match:
        return "❌ Няма избран мач."

    if not _validate_minute(minute):
        return "❌ Невалидна минута (1–120)."

    player = _get_player(player_id)
    if not player:
        return "❌ Играчът не съществува."

    home_team = match[1]
    away_team = match[2]

    if player[2] not in (home_team, away_team):
        return "❌ Играчът не е от участващите отбори."

    insert_goal(match[0], player_id, minute)

    return f"⚽ Гол записан (играч #{player_id}, {minute} мин.)"


# =========================
# CARDS
# =========================
def add_card(player_id: int, card_type: str, minute: int):
    match = get_current_match()

    if not match:
        return "❌ Няма избран мач."

    if not _validate_minute(minute):
        return "❌ Невалидна минута (1–120)."

    if card_type not in ["Y", "R"]:
        return "❌ Карта трябва да е Y или R."

    player = _get_player(player_id)
    if not player:
        return "❌ Играчът не съществува."

    home_team = match[1]
    away_team = match[2]

    if player[2] not in (home_team, away_team):
        return "❌ Играчът не е от участващите отбори."

    insert_card(match[0], player_id, minute, card_type)

    return f"🟨🟥 Картон записан (играч #{player_id}, {card_type})"


# =========================
# EVENTS
# =========================
def show_events(match_id=None):
    if not match_id:
        match = get_current_match()
        if not match:
            return "❌ Няма избран мач."
        match_id = match[0]

    goals = get_goals(match_id)
    cards = get_cards(match_id)

    result = f"📊 Събития за мач #{match_id}\n\n"

    result += "⚽ Голове:\n"
    for g in goals:
        result += f"{g[0]} мин - {g[1]} ({g[2]})\n"

    result += "\n🟨🟥 Картони:\n"
    for c in cards:
        result += f"{c[0]} мин - {c[1]} ({c[2]})\n"

    return result
