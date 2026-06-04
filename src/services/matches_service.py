# src/services/matches_service.py
#
# Правила:
#   handler → service → repo (без SQL тук)
#   current_match_id живее САМО тук – router/handlers не пипат глобала директно
#
# ПОПРАВКИ (Етап 7 – bug fixes):
#   • add_goal / add_card: търсим ПЪРВО клуба, после играча ВЪТРЕ в клуба.
#     Така "Петър Георгиев ЦСКА" не се обърква с "Петър Георгиев Берое".
 
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
 
    update_match_score(match_id, home_goals, away_goals)
 
    # Ако мачът е бил вече изигран → показваме промяната
    if status == "played":
        return (
            f"✏️  Резултатът е обновен: {home_team}–{away_team} "
            f"{old_home_g}:{old_away_g} → {home_goals}:{away_goals} "
            f"(мач #{match_id})\n"
            f"   📊 Класирането е обновено автоматично."
        )
 
    return f"✅ Записано: {home_team}–{away_team} {home_goals}:{away_goals} (мач #{match_id})"
 
 
# ─────────────────────────────────────────────────────────────
# ВЪТРЕШНА ПОМОЩНА ФУНКЦИЯ: намери отбор + играч в него
# ─────────────────────────────────────────────────────────────
def _resolve_club_and_player(club_name: str, player_name: str):
    """
    Търси ПЪРВО клуба (LIKE), после играча ВЪТРЕ в този клуб (LIKE).
    Така "Петър Георгиев ЦСКА" не се обърква с "Петър Георгиев Берое".
 
    Връща:
        (club_id, club_full_name, player_id, player_full_name)
        или raises ValueError с четимо съобщение при грешка.
    """
    # ── 1. Намери клуба ──────────────────────────────────────────
    clubs = execute_query(
        "SELECT club_id, name FROM Clubs WHERE LOWER(name) LIKE LOWER(?)",
        (f"%{club_name}%",),
        fetch=True,
    )
    if not clubs:
        raise ValueError(f"❌ Отбор '{club_name}' не е намерен.")
    if len(clubs) > 1:
        names = ", ".join(c[1] for c in clubs)
        raise ValueError(f"❌ Намерени няколко отбора: {names}. Уточни.")
 
    club_id, club_full_name = clubs[0]
 
    # ── 2. Намери играча ВЪТРЕ в клуба ──────────────────────────
    players = execute_query(
        """
        SELECT player_id, full_name
        FROM   Players
        WHERE  LOWER(full_name) LIKE LOWER(?)
          AND  club_id = ?
        """,
        (f"%{player_name}%", club_id),
        fetch=True,
    )
    if not players:
        raise ValueError(
            f"❌ Играч '{player_name}' не е намерен в {club_full_name}.\n"
            f"   Провери с: Покажи играчи на {club_full_name}"
        )
    if len(players) > 1:
        names = ", ".join(p[1] for p in players)
        raise ValueError(
            f"❌ Намерени няколко играча в {club_full_name}: {names}. "
            f"Уточни пълното ime."
        )
 
    player_id, player_full_name = players[0]
    return club_id, club_full_name, player_id, player_full_name
 
 
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
 
    # 3. Намери клуб + играч (новата, правилна логика)
    try:
        club_id, club_full_name, player_id, full_name = \
            _resolve_club_and_player(club_name, player_name)
    except ValueError as e:
        return str(e)
 
    # 4. Отборът участва ли в мача?
    if club_id not in (home_club_id, away_club_id):
        home_name = execute_query(
            "SELECT name FROM Clubs WHERE club_id=?", (home_club_id,), fetch=True
        )
        away_name = execute_query(
            "SELECT name FROM Clubs WHERE club_id=?", (away_club_id,), fetch=True
        )
        h = home_name[0][0] if home_name else "?"
        a = away_name[0][0] if away_name else "?"
        return (
            f"❌ {club_full_name} не участва в мач #{match_id} "
            f"({h} – {a})."
        )
 
    # 5. Запис
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
 
    # 4. Намери клуб + играч (новата, правилна логика)
    try:
        club_id, club_full_name, player_id, full_name = \
            _resolve_club_and_player(club_name, player_name)
    except ValueError as e:
        return str(e)
 
    # 5. Отборът участва ли в мача?
    if club_id not in (home_club_id, away_club_id):
        home_name = execute_query(
            "SELECT name FROM Clubs WHERE club_id=?", (home_club_id,), fetch=True
        )
        away_name = execute_query(
            "SELECT name FROM Clubs WHERE club_id=?", (away_club_id,), fetch=True
        )
        h = home_name[0][0] if home_name else "?"
        a = away_name[0][0] if away_name else "?"
        return (
            f"❌ {club_full_name} не участва в мач #{match_id} "
            f"({h} – {a})."
        )
 
    # 6. Запис
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
