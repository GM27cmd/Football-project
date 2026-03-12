import re
from src.services.clubs_service import add_club, get_all_clubs, delete_club
from src.services.players_service import (
    add_player,
    list_players_by_club,
    update_player_number,
    delete_player
)

def route_intent(intent, user_input):
    user_input = user_input.strip()

    # ===============================
    # CLUBS MODULE
    # ===============================
    if intent == "add_club":
        match = re.search(r"добави клуб\s+(.+)", user_input, re.IGNORECASE)
        if match:
            return add_club(match.group(1).strip())

    if intent == "list_clubs":
        return get_all_clubs()

    if intent == "delete_club":
        match = re.search(r"изтрий клуб\s+(.+)", user_input, re.IGNORECASE)
        if match:
            return delete_club(match.group(1).strip())

    # ===============================
    # PLAYERS MODULE
    # ===============================
    # Добави играч
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
            return add_player(full_name, birth_date, nationality, position, number, club_name)

    # Покажи играчи по клуб
    if intent == "list_players":
        match = re.search(r"покажи играчи на\s+(.+)", user_input, re.IGNORECASE)
        if match:
            return list_players_by_club(match.group(1).strip())

    # Смени номер
    if intent == "update_player_number":
        match = re.search(r"смени номер на\s+(.+?)\s+на\s+(\d+)", user_input, re.IGNORECASE)
        if match:
            return update_player_number(match.group(1).strip(), int(match.group(2)))

    # Изтрий играч
    if intent == "delete_player":
        match = re.search(r"изтрий играч\s+(.+)", user_input, re.IGNORECASE)
        if match:
            return delete_player(match.group(1).strip())

    # ===============================
    # HELP / SYSTEM
    # ===============================
    if intent == "help":
        return """
Команди:

Клубове:
- Добави клуб Левски
- Покажи всички клубове
- Изтрий клуб Левски

Играчите:
- Добави играч Иван Петров в Левски позиция FW номер 9 роден 2000-01-01 националност България
- Покажи играчи на Левски
- Смени номер на Иван Петров на 10
- Изтрий играч Иван Петров

Система:
- помощ
- изход
"""

    if intent == "exit":
        return "exit"

    return "❌ Не разбирам командата."
