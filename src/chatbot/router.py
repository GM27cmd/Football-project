import re

from src.services.clubs_service import add_club, get_all_clubs, delete_club
from src.services.players_service import (
    add_player,
    list_players_by_club,
    update_player_number,
    delete_player
)


def route_intent(intent, user_input):

    user_input = user_input.lower()

    # ===============================
    # CLUBS MODULE
    # ===============================

    if intent == "add_club":
        match = re.search(r"добави клуб (.+)", user_input)
        if match:
            return add_club(match.group(1))


    if intent == "list_clubs":
        return get_all_clubs()


    if intent == "delete_club":
        match = re.search(r"изтрий клуб (.+)", user_input)
        if match:
            return delete_club(match.group(1))


    # ===============================
    # PLAYERS MODULE
    # ===============================

    # Добави играч
    if intent == "add_player":
        match = re.search(
            r"добави играч (.+) в (.+) позиция (GK|DF|MF|FW) номер (\d+) роден (\d{4}-\d{2}-\d{2}) националност (.+)",
            user_input,
            re.IGNORECASE
        )

        if match:
            return add_player(
                match.group(1),
                match.group(5),
                match.group(6),
                match.group(3),
                int(match.group(4)),
                match.group(2)
            )


    # Покажи играчи по клуб
    if intent == "list_players":
        match = re.search(r"покажи играчи на (.+)", user_input)
        if match:
            return list_players_by_club(match.group(1))


    # Смени номер
    if intent == "update_player_number":
        match = re.search(r"смени номер на (.+) на (\d+)", user_input)
        if match:
            return update_player_number(
                match.group(1),
                int(match.group(2))
            )


    # Изтрий играч
    if intent == "delete_player":
        match = re.search(r"изтрий играч (.+)", user_input)
        if match:
            return delete_player(match.group(1))


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
