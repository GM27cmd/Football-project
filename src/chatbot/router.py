# src/chatbot/router.py

import re
from services.clubs_service   import add_club, get_all_clubs, delete_club
from services.players_service import (
    add_player, list_players_by_club,
    update_player_number, delete_player,
)
from services.transfers_service import (
    transfer_player,
    list_transfers_by_player,
    list_transfers_by_club,
)
from services.leagues_service import (
    create_league_service,
    add_team_service,
    list_teams_service,
    show_league_schedule,
    generate_schedule_service,
    show_leagues,
)

# ✅ Мач-команди
from chatbot.handlers_matches import (
    handle_show_round,
    handle_select_match,
    handle_set_result,
    handle_add_goal,
    handle_add_card,
    handle_show_events,
)

from chatbot.handlers_rename import (
    handle_rename_club,
    handle_rename_player,
    handle_rename_league,
)

# ✅ Класиране 
from chatbot.handlers_standings import handle_show_standings

# ✅ AI Прогноза
from chatbot.handlers_ai import handle_predict

from chatbot.help import show_help
from utils.logger import log_command


def route_intent(intent, user_input):
    user_input = user_input.strip()

    # ─── CLUBS ───────────────────────────────────────────
    if intent == "add_club":
        m = re.search(r"добави клуб\s+(.+)", user_input, re.IGNORECASE)
        if m:
            result = add_club(m.group(1).strip())
            log_command(user_input, intent, params={"club": m.group(1).strip()}, result=result)
            return result

    if intent == "list_clubs":
        result = get_all_clubs()
        log_command(user_input, intent, result=result)
        return result

    if intent == "delete_club":
        m = re.search(r"изтрий клуб\s+(.+)", user_input, re.IGNORECASE)
        if m:
            result = delete_club(m.group(1).strip())
            log_command(user_input, intent, params={"club": m.group(1).strip()}, result=result)
            return result

    # ─── PLAYERS ─────────────────────────────────────────
    if intent == "add_player":
        m = re.search(
            r"добави играч\s+(.+?)\s+в\s+(.+?)\s+позиция\s+(GK|DF|MF|FW)"
            r"\s+номер\s+(\d+)\s+роден\s+(\d{4}-\d{2}-\d{2})\s+националност\s+(.+)",
            user_input, re.IGNORECASE,
        )
        if m:
            full_name   = m.group(1).strip()
            club_name   = m.group(2).strip()
            position    = m.group(3).upper()
            number      = int(m.group(4))
            birth_date  = m.group(5).strip()
            nationality = m.group(6).strip()
            result = add_player(full_name, birth_date, nationality, position, number, club_name)
            log_command(user_input, intent, params={"player": full_name, "club": club_name}, result=result)
            return result

    if intent == "list_players":
        m = re.search(r"покажи играчи на\s+(.+)", user_input, re.IGNORECASE)
        if m:
            club_name = m.group(1).strip()
            result = list_players_by_club(club_name)
            log_command(user_input, intent, params={"club": club_name}, result=result)
            return result

    if intent == "update_player_number":
        m = re.search(r"смени номер на\s+(.+?)\s+на\s+(\d+)", user_input, re.IGNORECASE)
        if m:
            player_name = m.group(1).strip()
            new_number  = int(m.group(2))
            result = update_player_number(player_name, new_number)
            log_command(user_input, intent, params={"player": player_name, "number": new_number}, result=result)
            return result

    if intent == "delete_player":
        m = re.search(r"изтрий играч\s+(.+)", user_input, re.IGNORECASE)
        if m:
            player_name = m.group(1).strip()
            result = delete_player(player_name)
            log_command(user_input, intent, params={"player": player_name}, result=result)
            return result

    # ─── TRANSFERS ───────────────────────────────────────
    if user_input.lower().startswith("покажи трансфери на"):
        m = re.search(r"покажи трансфери на\s+(.+)", user_input, re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            result = list_transfers_by_player(name)
            if "❌ Играчът не съществува." not in result:
                log_command(user_input, "show_transfers_player", params={"player": name}, result=result)
                return result
            result = list_transfers_by_club(name)
            if "❌ Клубът не съществува." not in result:
                log_command(user_input, "show_transfers_club", params={"club": name}, result=result)
                return result
            return "❌ Няма трансфери за този играч или клуб."

    if user_input.lower().startswith("трансфер"):
        m = re.search(
            r"трансфер\s+(.+?)\s+от\s+(.+?)\s+в\s+(.+?)\s+(\d{4}-\d{2}-\d{2})"
            r"(\s+сума\s+(\d+))?(\s+забележка\s+(.+))?",
            user_input, re.IGNORECASE,
        )
        if m:
            player_name = m.group(1).strip()
            from_club   = m.group(2).strip()
            to_club     = m.group(3).strip()
            date        = m.group(4)
            fee         = float(m.group(6)) if m.group(6) else None
            note        = m.group(8).strip() if m.group(8) else None
            result = transfer_player(player_name, from_club, to_club, date, fee, note)
            log_command(
                user_input, "transfer_player",
                params={"player": player_name, "from": from_club, "to": to_club, "date": date},
                result=result,
            )
            return result
        return "❌ Грешен формат. Пример: Трансфер Иван Петров от Левски в Лудогорец 2026-03-10"

    # ─── LEAGUES ─────────────────────────────────────────
    if intent == "create_league":
        m = re.search(r"създай лига\s+(.+?)\s+(\d{4}/\d{4})", user_input, re.IGNORECASE)
        if m:
            result = create_league_service(m.group(1).strip(), m.group(2).strip())
            log_command(user_input, intent, result=result)
            return result

    if intent == "add_team_league":
        m = re.search(
            r"добави отбор\s+(.+?)\s+в\s+(.+?)\s*(\d{4}/\d{4})?$",
            user_input, re.IGNORECASE,
        )
        if m:
            club   = m.group(1).strip()
            league = m.group(2).strip()
            season = m.group(3)
            if not season:
                return "❌ Моля добави сезон. Пример: 2025/2026"
            result = add_team_service(club, league, season)
            log_command(user_input, intent, params={"club": club, "league": league}, result=result)
            return result

    if intent == "list_teams_league":
        m = re.search(r"покажи отбори в лига\s+(.+?)\s+(\d{4}/\d{4})", user_input, re.IGNORECASE)
        if m:
            result = list_teams_service(m.group(1).strip(), m.group(2).strip())
            log_command(user_input, intent, result=result)
            return result

    if intent == "generate_schedule":
        m = re.search(r"генерирай програма\s+(.+?)\s*\(?\s*(\d{4}/\d{4})\s*\)?", user_input, re.IGNORECASE)
        if m:
            result = generate_schedule_service(m.group(1).strip(), m.group(2).strip())
            log_command(user_input, intent, result=result)
            return result

    if intent == "show_schedule":
        m = re.search(r"покажи програма\s+(.+?)\s*\(?\s*(\d{4}/\d{4})\s*\)?", user_input, re.IGNORECASE)
        if m:
            result = show_league_schedule(m.group(1).strip(), m.group(2).strip())
            log_command(user_input, intent, result=result)
            return result

    if intent == "show_leagues":
        result = show_leagues()
        log_command(user_input, intent, result=result)
        return result

    # ─── MATCHES (делегиране към handlers_matches) ────────
    if intent == "show_round":
        return handle_show_round(user_input)

    if intent == "select_match":
        return handle_select_match(user_input)

    if intent == "set_result":
        return handle_set_result(user_input)

    if intent == "add_goal":
        return handle_add_goal(user_input)

    if intent == "add_card":
        return handle_add_card(user_input)

    if intent == "show_events":
        return handle_show_events(user_input)

    # ─── КЛАСИРАНЕ  ──────────────────────────────
    if intent == "show_standings":
        return handle_show_standings(user_input)

    # ─── AI ПРОГНОЗА  ────────────────────────────
    if intent == "predict_match":
        return handle_predict(user_input)
    
    # ─── ПРЕИМЕНУВАНЕ  ────────────────────────────
    if intent == "rename_club":
        return handle_rename_club(user_input)
    if intent == "rename_player":
        return handle_rename_player(user_input)
    if intent == "rename_league":
        return handle_rename_league(user_input)
    
    # ─── SYSTEM ──────────────────────────────────────────
    if intent == "help":
        return show_help()

    if intent == "exit":
        return "exit"

    return "❌ Не разбирам командата."
