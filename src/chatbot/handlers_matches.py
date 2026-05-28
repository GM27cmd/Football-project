# src/chatbot/handlers_matches.py
#
# Отговаря за парсинга на чат командите за мачове.
# Структура: handler → service → repo (без SQL тук)

import re
from services.matches_service import (
    show_round,
    select_match,
    set_result,
    add_goal,
    add_card,
    show_events,
)
from utils.logger import log_command


# -------------------------------------------------------
# A) Покажи кръг <N> <лига> <сезон>
# -------------------------------------------------------
def handle_show_round(user_input: str) -> str:
    m = re.search(
        r"покажи кръг\s+(\d+)\s+(.+?)\s+(\d{4}/\d{4})",
        user_input,
        re.IGNORECASE,
    )
    if not m:
        result = "❌ Грешен формат. Пример: Покажи кръг 3 Първа лига 2025/2026"
        log_command(user_input, "show_round", result=result)
        return result

    round_no    = int(m.group(1))
    league_name = m.group(2).strip()
    season      = m.group(3).strip()

    result = show_round(league_name, season, round_no)
    log_command(
        user_input, "show_round",
        params={"round": round_no, "league": league_name, "season": season},
        result=result,
    )
    return result


# -------------------------------------------------------
# D) Избери мач <match_id>
# -------------------------------------------------------
def handle_select_match(user_input: str) -> str:
    m = re.search(r"избери мач\s+(\d+)", user_input, re.IGNORECASE)
    if not m:
        result = "❌ Грешен формат. Пример: Избери мач 12"
        log_command(user_input, "select_match", result=result)
        return result

    match_id = int(m.group(1))
    result   = select_match(match_id)
    log_command(user_input, "select_match", params={"match_id": match_id}, result=result)
    return result


# -------------------------------------------------------
# B) Резултат <Домакин>-<Гост> <X>:<Y> запиши
# -------------------------------------------------------
def handle_set_result(user_input: str) -> str:
    m = re.search(
        r"резултат\s+(.+?)\s*-\s*(.+?)\s+(\d+):(\d+)\s*запиши",
        user_input,
        re.IGNORECASE,
    )
    if not m:
        result = "❌ Грешен формат. Пример: Резултат Левски-Ботев 3:0 запиши"
        log_command(user_input, "set_result", result=result)
        return result

    home       = m.group(1).strip()
    away       = m.group(2).strip()
    home_goals = int(m.group(3))
    away_goals = int(m.group(4))

    result = set_result(home, away, home_goals, away_goals)
    log_command(
        user_input, "set_result",
        params={"home": home, "away": away, "score": f"{home_goals}:{away_goals}"},
        result=result,
    )
    return result


# -------------------------------------------------------
# C) Гол <Играч> <Отбор> <минута> [минута]
#
# Минутата е последното число в командата.
# Всичко между "гол" и числото → разбиваме на "всички думи
# без последната" = играч, "последна дума" = отбор.
# Работи за единично-именни отбори (Левски, ЦСКА, Берое).
# За двусловни (Черно море) ползвай частично съвпадение:
#   Гол Роберт Джеймс Черно 45   → LIKE %Черно% → "Черно море"
# -------------------------------------------------------
def handle_add_goal(user_input: str) -> str:
    # Извлечи всичко след "гол " и преди евентуалното " минута" накрая
    m = re.search(r"гол\s+(.+?)\s+(\d+)(?:\s+минута)?$", user_input, re.IGNORECASE)
    if not m:
        result = "❌ Грешен формат. Пример: Гол Иван Георгиев Левски 23"
        log_command(user_input, "add_goal", result=result)
        return result

    body   = m.group(1).strip()   # "Иван Георгиев Левски"
    minute = int(m.group(2))

    words = body.split()
    if len(words) < 2:
        result = "❌ Грешен формат. Нужни са поне две думи (играч + отбор)."
        log_command(user_input, "add_goal", result=result)
        return result

    # Последна дума = отбор, останалото = играч
    club_name   = words[-1]
    player_name = " ".join(words[:-1])

    result = add_goal(player_name, club_name, minute)
    log_command(
        user_input, "add_goal",
        params={"player": player_name, "club": club_name, "minute": minute},
        result=result,
    )
    return result


# -------------------------------------------------------
# E) Картон <Играч> <Отбор> <Y/R> <минута>
# -------------------------------------------------------
def handle_add_card(user_input: str) -> str:
    # Картонът (Y/R) и минутата са фиксирани в края
    m = re.search(
        r"картон\s+(.+?)\s+(Y|R)\s+(\d+)$",
        user_input,
        re.IGNORECASE,
    )
    if not m:
        result = "❌ Грешен формат. Пример: Картон Иван Петров Левски Y 55"
        log_command(user_input, "add_card", result=result)
        return result

    body      = m.group(1).strip()   # "Иван Петров Левски"
    card_type = m.group(2).upper()
    minute    = int(m.group(3))

    words = body.split()
    if len(words) < 2:
        result = "❌ Грешен формат. Нужни са поне две думи (играч + отбор)."
        log_command(user_input, "add_card", result=result)
        return result

    club_name   = words[-1]
    player_name = " ".join(words[:-1])

    result = add_card(player_name, club_name, card_type, minute)
    log_command(
        user_input, "add_card",
        params={
            "player": player_name, "club": club_name,
            "card": card_type, "minute": minute,
        },
        result=result,
    )
    return result


# -------------------------------------------------------
# F) Покажи събития [match_id]
# -------------------------------------------------------
def handle_show_events(user_input: str) -> str:
    m = re.search(r"покажи събития\s*(\d+)?", user_input, re.IGNORECASE)

    match_id = int(m.group(1)) if m and m.group(1) else None
    result   = show_events(match_id)
    log_command(user_input, "show_events", params={"match_id": match_id}, result=result)
    return result
