# src/chatbot/router.py
import re
from services.clubs_service import add_club, get_all_clubs, delete_club
from services.players_service import add_player, list_players_by_club, update_player_number, delete_player
from services.transfers_service import transfer_player, list_transfers_by_player, list_transfers_by_club
from utils.logger import log_command
from services.leagues_service import *
from services.leagues_service import show_league_schedule
from services.leagues_service import show_leagues
from services.matches_service import (
    show_round,
    select_match,
    set_result,
    add_goal,
    add_card,
    show_events
)
from chatbot.help import show_help
from services.leagues_service import list_teams_service

def route_intent(intent, user_input):
    user_input = user_input.strip()

    # --- CLUBS ---
    if intent == "add_club":
        match = re.search(r"добави клуб\s+(.+)", user_input, re.IGNORECASE)
        if match:
            result = add_club(match.group(1).strip())
            log_command(user_input, intent, params={"club": match.group(1).strip()}, result=result)
            return result

    if intent == "list_clubs":
        result = get_all_clubs()
        log_command(user_input, intent, result=result)
        return result

    if intent == "delete_club":
        match = re.search(r"изтрий клуб\s+(.+)", user_input, re.IGNORECASE)
        if match:
            result = delete_club(match.group(1).strip())
            log_command(user_input, intent, params={"club": match.group(1).strip()}, result=result)
            return result

    # --- PLAYERS ---
    if intent == "add_player":
        match = re.search(
            r"добави играч\s+(.+?)\s+в\s+(.+?)\s+позиция\s+(GK|DF|MF|FW)\s+номер\s+(\d+)\s+роден\s+(\d{4}-\d{2}-\d{2})\s+националност\s+(.+)",
            user_input,
            re.IGNORECASE
        )
        if match:
            full_name = match.group(1).strip()
            club_name = match.group(2).strip()
            position = match.group(3).upper()
            number = int(match.group(4))
            birth_date = match.group(5).strip()
            nationality = match.group(6).strip()
            result = add_player(full_name, birth_date, nationality, position, number, club_name)
            log_command(user_input, intent, params={"player": full_name, "club": club_name}, result=result)
            return result

    if intent == "list_players":
        match = re.search(r"покажи играчи на\s+(.+)", user_input, re.IGNORECASE)
        if match:
            club_name = match.group(1).strip()
            result = list_players_by_club(club_name)
            log_command(user_input, intent, params={"club": club_name}, result=result)
            return result

    if intent == "update_player_number":
        match = re.search(r"смени номер на\s+(.+?)\s+на\s+(\d+)", user_input, re.IGNORECASE)
        if match:
            player_name = match.group(1).strip()
            new_number = int(match.group(2))
            result = update_player_number(player_name, new_number)
            log_command(user_input, intent, params={"player": player_name, "number": new_number}, result=result)
            return result

    if intent == "delete_player":
        match = re.search(r"изтрий играч\s+(.+)", user_input, re.IGNORECASE)
        if match:
            player_name = match.group(1).strip()
            result = delete_player(player_name)
            log_command(user_input, intent, params={"player": player_name}, result=result)
            return result

    # --- TRANSFERS ---
    if user_input.lower().startswith("покажи трансфери на"):
        match = re.search(r"Покажи трансфери на\s+(.+)", user_input, re.IGNORECASE)
        if match:
            name = match.group(1).strip()

            # първо като играч
            result = list_transfers_by_player(name)
            if "❌ Играчът не съществува." not in result:
                log_command(user_input, "show_transfers_player", params={"player": name}, result=result)
                return result

            # ако не е играч → пробвай като клуб
            result = list_transfers_by_club(name)
            if "❌ Клубът не съществува." not in result:
                log_command(user_input, "show_transfers_club", params={"club": name}, result=result)
                return result

            # няма такъв играч или клуб
            return "❌ Няма трансфери за този играч или клуб."


    # ✅ REAL transfer (само ако започва с "Трансфер")
    if user_input.lower().startswith("трансфер"):
        match = re.search(
            r"Трансфер\s+(.+?)\s+от\s+(.+?)\s+в\s+(.+?)\s+(\d{4}-\d{2}-\d{2})(\s+сума\s+(\d+))?(\s+забележка\s+(.+))?",
            user_input,
            re.IGNORECASE
        )
        if match:
            player_name = match.group(1).strip()
            from_club = match.group(2).strip()
            to_club = match.group(3).strip()
            date = match.group(4)
            fee = float(match.group(6)) if match.group(6) else None
            note = match.group(8).strip() if match.group(8) else None

            result = transfer_player(player_name, from_club, to_club, date, fee, note)

            log_command(
                user_input,
                "transfer_player",
                params={
                    "player": player_name,
                    "from": from_club,
                    "to": to_club,
                    "date": date,
                    "fee": fee,
                    "note": note
                },
                result=result
            )
            return result
        else:
            return "❌ Грешен формат на трансфер. Пример: Трансфер Иван Петров от Левски в Лудогорец 2026-03-10"
        
    if intent == "create_league":
        match = re.search(r"създай лига\s+(.+?)\s+(\d{4}/\d{4})", user_input, re.IGNORECASE)
        if match:
            name = match.group(1)
            season = match.group(2)
            result = create_league_service(name, season)
            return result
        
    if intent == "add_team_league":
        match = re.search(
            r"добави отбор\s+(.+?)\s+в\s+(.+?)\s*(\d{4}/\d{4})?$",
            user_input,
            re.IGNORECASE
        )

        if match:
            club = match.group(1).strip()
            league = match.group(2).strip()
            season = match.group(3)

            if not season:
                return "❌ Моля добави сезон. Пример: 2025/2026"

            return add_team_service(club, league, season)
        
    if intent == "list_teams_league":
        match = re.search(r"покажи отбори в лига\s+(.+?)\s+(\d{4}/\d{4})", user_input, re.IGNORECASE)
        if match:
            return list_teams_service(match.group(1), match.group(2))
        
    if intent == "generate_schedule":
        match = re.search(
            r"генерирай програма\s+(.+?)\s*\(?(\d{4}/\d{4})\)?",
            user_input,
            re.IGNORECASE
        )
        if match:
            return generate_schedule_service(match.group(1), match.group(2))
    
    if intent == "show_schedule":
        match = re.search(
            r"покажи програма\s+(.+?)\s*\(?(\d{4}/\d{4})\)?",
            user_input,
            re.IGNORECASE
        )
        if match:
            league_name = match.group(1).strip()
            season = match.group(2).strip()
            result = show_league_schedule(league_name, season)
            log_command(user_input, intent, params={"league": league_name, "season": season}, result=result)
            return result

    if intent == "show_round":
        match = re.search(
            r"покажи кръг\s+(\d+)\s+(.+?)\s*\(?(\d{4}/\d{4})\)?",
            user_input,
            re.IGNORECASE
        )
        if match:
            return show_round(match.group(2), match.group(3), int(match.group(1)))

    # SELECT MATCH
    if intent == "select_match":
        match = re.search(r"избери мач\s+(\d+)", user_input, re.IGNORECASE)
        if match:
            return select_match(int(match.group(1)))

    # RESULT
    if user_input.lower().startswith("резултат"):
        match = re.search(r"резултат\s+(.+?)-(.+?)\s+(\d+):(\d+)", user_input, re.IGNORECASE)
        if match:
            return set_result(
                match.group(1).strip(),
                match.group(2).strip(),
                int(match.group(3)),
                int(match.group(4))
            )

    # GOAL
    if intent == "add_goal":
        match = re.search(r"гол\s+(.+?)\s+(.+?)\s+(\d+)", user_input, re.IGNORECASE)
        if match:
            return add_goal(match.group(1), match.group(2), int(match.group(3)))

    # CARD
    if intent == "add_card":
        match = re.search(r"картон\s+(.+?)\s+(.+?)\s+(Y|R)\s+(\d+)", user_input, re.IGNORECASE)
        if match:
            return add_card(match.group(1), match.group(2), match.group(3), int(match.group(4)))

    # LEAGUES
    if intent == "show_leagues":
        match = re.search(r"покажи\s+лиги", user_input, re.IGNORECASE)
        if match:
            return show_leagues()

    # EVENTS
    if intent == "show_events":
        return show_events()    
    
    # --- HELP / SYSTEM ---
    if intent == "help":
        return show_help()
    
    if intent == "exit":
        return "exit"

    return "❌ Не разбирам командата."
