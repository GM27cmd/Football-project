# src/chatbot/handlers_stats.py
#
# Парсинг на чат командите за статистика (Модул G).
# Структура: handler → stats_service → DB

import re
from services.stats_service import get_top_scorers, get_discipline, get_team_scoring
from utils.logger import log_command


# ──────────────────────────────────────────────────────────────
# ПОМОЩНА: извлича <лига> <сезон> от края на командата
# ──────────────────────────────────────────────────────────────

def _parse_league_season(user_input: str, keyword: str):
    """
    Извлича (league_name, season) от команда:
        <keyword> <league_name> <ГГГГ/ГГГГ>
    Връща (None, None) при грешен формат.
    """
    m = re.search(
        rf"{keyword}\s+(.+?)\s+(\d{{4}}/\d{{4}})",
        user_input,
        re.IGNORECASE,
    )
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()


# ──────────────────────────────────────────────────────────────
# 1. ГОЛМАЙСТОРИ
# ──────────────────────────────────────────────────────────────

def handle_top_scorers(user_input: str) -> str:
    """
    Команда: Покажи голмайстори <лига> <сезон>
    Пример:  Покажи голмайстори Първа лига 2025/2026
    """
    league, season = _parse_league_season(user_input, "покажи голмайстори")
    if not league:
        result = (
            "❌ Грешен формат.\n"
            "   Пример: Покажи голмайстори Първа лига 2025/2026"
        )
        log_command(user_input, "top_scorers", result=result)
        return result

    result = get_top_scorers(league, season)
    log_command(user_input, "top_scorers",
                params={"league": league, "season": season}, result=result)
    return result


# ──────────────────────────────────────────────────────────────
# 2. ДИСЦИПЛИНА
# ──────────────────────────────────────────────────────────────

def handle_discipline(user_input: str) -> str:
    """
    Команда: Покажи дисциплина <лига> <сезон>
    Пример:  Покажи дисциплина Първа лига 2025/2026
    """
    league, season = _parse_league_season(user_input, "покажи дисциплина")
    if not league:
        result = (
            "❌ Грешен формат.\n"
            "   Пример: Покажи дисциплина Първа лига 2025/2026"
        )
        log_command(user_input, "discipline", result=result)
        return result

    result = get_discipline(league, season)
    log_command(user_input, "discipline",
                params={"league": league, "season": season}, result=result)
    return result


# ──────────────────────────────────────────────────────────────
# 3. ОТБОРНА РЕЗУЛТАТНОСТ
# ──────────────────────────────────────────────────────────────

def handle_team_scoring(user_input: str) -> str:
    """
    Команда: Покажи резултатност <лига> <сезон>
    Пример:  Покажи резултатност Първа лига 2025/2026
    """
    league, season = _parse_league_season(user_input, "покажи резултатност")
    if not league:
        result = (
            "❌ Грешен формат.\n"
            "   Пример: Покажи резултатност Първа лига 2025/2026"
        )
        log_command(user_input, "team_scoring", result=result)
        return result

    result = get_team_scoring(league, season)
    log_command(user_input, "team_scoring",
                params={"league": league, "season": season}, result=result)
    return result
