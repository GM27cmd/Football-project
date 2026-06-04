# src/chatbot/handlers_standings.py
#
# Парсинг на чат командите за класиране.
# Структура: handler → service → repo (без SQL тук)
 
import re
from services.standings_service import get_standings
from utils.logger import log_command
 
 
# -------------------------------------------------------
# Покажи класиране <лига> <сезон>
# -------------------------------------------------------
def handle_show_standings(user_input: str) -> str:
    """
    Команда: Покажи класиране <лига> <сезон>
    Пример:  Покажи класиране Първа лига 2025/2026
    """
    m = re.search(
        r"покажи класиране\s+(.+?)\s+(\d{4}/\d{4})",
        user_input,
        re.IGNORECASE,
    )
    if not m:
        result = (
            "❌ Грешен формат.\n"
            "   Пример: Покажи класиране Първа лига 2025/2026"
        )
        log_command(user_input, "show_standings", result=result)
        return result
 
    league_name = m.group(1).strip()
    season      = m.group(2).strip()
 
    result = get_standings(league_name, season)
 
    log_command(
        user_input,
        "show_standings",
        params={"league": league_name, "season": season},
        result=result,
    )
    return result
 
