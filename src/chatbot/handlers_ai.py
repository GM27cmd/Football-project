# src/chatbot/handlers_ai.py
#
# Парсинг на чат командата за AI прогноза.
# Структура: handler → ai_service → features → DB

import re
from ai.ai_service import predict
from utils.logger import log_command


def handle_predict(user_input: str) -> str:
    """
    Команда: Прогноза <Отбор1> срещу <Отбор2>
    Команда: Прогноза <Отбор1> срещу <Отбор2> графика   ← показва matplotlib chart

    Примери:
        Прогноза Левски срещу Лудогорец
        Прогноза Левски срещу Лудогорец графика
    """
    m = re.search(
        r"прогноза\s+(.+?)\s+срещу\s+(.+?)(?:\s+графика)?\s*$",
        user_input,
        re.IGNORECASE,
    )
    if not m:
        result = (
            "❌ Грешен формат.\n"
            "   Пример: Прогноза Левски срещу Лудогорец\n"
            "   С графика: Прогноза Левски срещу Лудогорец графика"
        )
        log_command(user_input, "predict_match", result=result)
        return result

    home_name  = m.group(1).strip()
    away_name  = m.group(2).strip()
    show_chart = bool(re.search(r"графика", user_input, re.IGNORECASE))

    result = predict(home_name, away_name, show_chart=show_chart)

    log_command(
        user_input,
        "predict_match",
        params={"home": home_name, "away": away_name, "chart": show_chart},
        result=result,
    )
    return result
