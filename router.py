import re
from src.services.clubs_service import add_club, get_all_clubs, delete_club


def route_intent(intent, user_input):
    if intent == "add_club":
        match = re.search(r"добави клуб (.+)", user_input.lower())
        if match:
            name = match.group(1)
            return add_club(name)

    if intent == "list_clubs":
        return get_all_clubs()

    if intent == "delete_club":
        match = re.search(r"изтрий клуб (.+)", user_input.lower())
        if match:
            name = match.group(1)
            return delete_club(name)

    if intent == "help":
        return (
            "Команди:\n"
            "- Добави клуб Име\n"
            "- Покажи всички клубове\n"
            "- Изтрий клуб Име\n"
            "- помощ\n"
            "- изход"
        )

    if intent == "exit":
        return "exit"

    return "Не разбирам командата."
