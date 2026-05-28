# src/services/matches_service.py
#
# Правила:
#   handler → service → repo (без SQL тук)
#   current_match_id живее САМО тук – router/handlers не пипат глобала директно

from database.db import execute_query
from repositories.matches_repo import (
    get_matches_by_round,
    get_match_by_id,
    update_match_score,
    insert_goal,
    insert_card,
    get_goals,
    get_cards,
)
from repositories.leagues_repo import get_league_by_name_and_season

# =========================
# RUNTIME КОНТЕКСТ
# =========================
current_match_id = None          # избран мач за текущата сесия


# =========================
# ИЗБОР НА МАЧ
# =========================
def select_match(match_id: int) -> str:
    global current_match_id
    match = get_match_by_id(match_id)
    if not match:
        return f"❌ Няма мач с ID {match_id}."
    current_match_id = match_id
    return f"✅ Избран мач #{match_id}: {match[1]} vs {match[2]}"


def get_current_match():
    """Връща row за текущия мач или None."""
    if current_match_id is None:
        return None
    return get_match_by_id(current_match_id)


# =========================
# ПРЕГЛЕД НА КРЪГ
# =========================
def show_round(league_name: str, season: str, round_no: int) -> str:
    league = get_league_by_name_and_season(league_name, season)
    if not league:
        return f"❌ Лигата '{league_name}' ({season}) не съществува."

    league_id = league[0]
    matches = get_matches_by_round(league_id, round_no)
    if not matches:
        return f"❌ Няма мачове за кръг {round_no} в {league_name} ({season})."

    result = f"📅 Кръг {round_no} – {league_name} ({season})\n\n"
    for m in matches:
        match_id, home, away, home_goals, away_goals, status = m
        score = f"{home_goals}:{away_goals}" if home_goals is not None else "⏳ неигран"
        result += f"🆔 {match_id} | {home} – {away} | {score} | {status}\n"
    return result


# =========================
# ЗАПИС НА РЕЗУЛТАТ
# =========================
def set_result(home: str, away: str, home_goals: int, away_goals: int) -> str:
    match = get_current_match()
    if not match:
        return "❌ Не е избран мач. Използвай: Избери мач <ID>"

    match_id   = match[0]
    home_team  = match[1]
    away_team  = match[2]
    old_home_g = match[3]
    old_away_g = match[4]
    status     = match[5]

    # Проверка дали подадените отбори съвпадат с мача
    if home.lower() != home_team.lower() or away.lower() != away_team.lower():
        return (
            f"❌ Отборите не съвпадат с избрания мач #{match_id} "
            f"({home_team} – {away_team}).\n"
            f"   Провери с: Покажи кръг или смени мача с: Избери мач <ID>"
        )

    # Вече записан резултат
    if status == "played":
        return (
            f"❌ Мач #{match_id} вече има резултат "
            f"{old_home_g}:{old_away_g}. "
            f"Редакция не е позволена."
        )

    update_match_score(match_id, home_goals, away_goals)
    return f"✅ Записано: {home_team}–{away_team} {home_goals}:{away_goals} (мач #{match_id})"


# =========================
# ГОЛОВЕ
# =========================
def add_goal(player_name: str, club_name: str, minute: int) -> str:
    # 1. Валидна минута
    if not (1 <= minute <= 120):
        return f"❌ Невалидна минута {minute}. Трябва да е между 1 и 120."

    # 2. Текущ мач
    match = get_current_match()
    if not match:
        return "❌ Не е избран мач. Използвай: Избери мач <ID>"

    match_id     = match[0]
    home_club_id = match[6]
    away_club_id = match[7]

    # 3. Намери играча (LIKE за частично съвпадение на имена)
    players = execute_query(
        "SELECT player_id, club_id, full_name FROM Players "
        "WHERE LOWER(full_name) LIKE LOWER(?)",
        (f"%{player_name}%",),
        fetch=True,
    )
    if not players:
        return f"❌ Играч '{player_name}' не е намерен."
    if len(players) > 1:
        names = ", ".join(p[2] for p in players)
        return f"❌ Намерени няколко играча: {names}. Уточни пълното име."

    player_id, player_club_id, full_name = players[0]

    # 4. Намери клуба
    clubs = execute_query(
        "SELECT club_id, name FROM Clubs WHERE LOWER(name) LIKE LOWER(?)",
        (f"%{club_name}%",),
        fetch=True,
    )
    if not clubs:
        return f"❌ Отбор '{club_name}' не е намерен."
    if len(clubs) > 1:
        names = ", ".join(c[1] for c in clubs)
        return f"❌ Намерени няколко отбора: {names}. Уточни."

    club_id, club_full_name = clubs[0]

    # 5. Играчът принадлежи ли на посочения отбор?
    if player_club_id != club_id:
        return f"❌ {full_name} не е играч на {club_full_name}."

    # 6. Отборът участва ли в мача?
    if club_id not in (home_club_id, away_club_id):
        return f"❌ {club_full_name} не участва в мач #{match_id}."

    # 7. Запис
    insert_goal(match_id, player_id, club_id, minute)
    return f"⚽ Гол записан: {full_name} ({club_full_name}) {minute}'"


# =========================
# КАРТОНИ
# =========================
def add_card(player_name: str, club_name: str, card_type: str, minute: int) -> str:
    # 1. Тип картон
    card_type = card_type.upper()
    if card_type not in ("Y", "R"):
        return "❌ Картонът трябва да е Y (жълт) или R (червен)."

    # 2. Валидна минута
    if not (1 <= minute <= 120):
        return f"❌ Невалидна минута {minute}. Трябва да е между 1 и 120."

    # 3. Текущ мач
    match = get_current_match()
    if not match:
        return "❌ Не е избран мач. Използвай: Избери мач <ID>"

    match_id     = match[0]
    home_club_id = match[6]
    away_club_id = match[7]

    # 4. Намери играча
    players = execute_query(
        "SELECT player_id, club_id, full_name FROM Players "
        "WHERE LOWER(full_name) LIKE LOWER(?)",
        (f"%{player_name}%",),
        fetch=True,
    )
    if not players:
        return f"❌ Играч '{player_name}' не е намерен."
    if len(players) > 1:
        names = ", ".join(p[2] for p in players)
        return f"❌ Намерени няколко играча: {names}. Уточни пълното ime."

    player_id, player_club_id, full_name = players[0]

    # 5. Намери клуба
    clubs = execute_query(
        "SELECT club_id, name FROM Clubs WHERE LOWER(name) LIKE LOWER(?)",
        (f"%{club_name}%",),
        fetch=True,
    )
    if not clubs:
        return f"❌ Отбор '{club_name}' не е намерен."
    if len(clubs) > 1:
        names = ", ".join(c[1] for c in clubs)
        return f"❌ Намерени няколко отбора: {names}. Уточни."

    club_id, club_full_name = clubs[0]

    # 6. Играчът принадлежи ли на посочения отбор?
    if player_club_id != club_id:
        return f"❌ {full_name} не е играч на {club_full_name}."

    # 7. Отборът участва ли в мача?
    if club_id not in (home_club_id, away_club_id):
        return f"❌ {club_full_name} не участва в мач #{match_id}."

    # 8. Запис
    insert_card(match_id, player_id, club_id, minute, card_type)
    emoji = "🟨" if card_type == "Y" else "🟥"
    return f"{emoji} Картон записан: {full_name} ({club_full_name}) {card_type} {minute}'"


# =========================
# ПРЕГЛЕД НА СЪБИТИЯ
# =========================
def show_events(match_id: int = None) -> str:
    # Ако не е подаден ID → ползваме текущия
    if match_id is None:
        match = get_current_match()
        if not match:
            return (
                "❌ Не е избран мач. Използвай: Избери мач <ID> "
                "или: Покажи събития <match_id>"
            )
        match_id = match[0]
    else:
        match = get_match_by_id(match_id)
        if not match:
            return f"❌ Няма мач с ID {match_id}."

    home       = match[1]
    away       = match[2]
    home_goals = match[3]
    away_goals = match[4]
    score_str  = f"{home_goals}:{away_goals}" if home_goals is not None else "– : –"

    output  = f"📊 Мач #{match_id}: {home} – {away} | {score_str}\n"
    output += "─" * 42 + "\n"

    goals = get_goals(match_id)    # (minute, full_name, club_name)
    cards = get_cards(match_id)    # (minute, full_name, card_type, club_name)

    # Обединяваме и сортираме по минута
    events = []
    for g in goals:
        events.append((g[0], "⚽", g[1], g[2]))
    for c in cards:
        emoji = "🟨" if c[2] == "Y" else "🟥"
        events.append((c[0], emoji, c[1], c[3]))

    events.sort(key=lambda x: x[0])

    if not events:
        output += "Няма записани събития.\n"
    else:
        for minute, icon, name, club in events:
            output += f"{minute:>3}' {icon}  {name} ({club})\n"

    return output
