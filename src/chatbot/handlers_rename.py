# src/chatbot/handlers_rename.py
#
# Парсинг на командите за преименуване.
# Структура: handler → rename_service → DB

import re
from services.rename_service import rename_club, rename_player, rename_league
from utils.logger import log_command


# ──────────────────────────────────────────────────────────────
# ПОМОЩНА: извлича "X на Y" от командата
# ──────────────────────────────────────────────────────────────

def _parse_rename(user_input: str, keyword: str):
    """
    Извлича (old_name, new_name) от команда от вида:
        Преименувай <keyword> <old_name> на <new_name>
    Връща (old, new) или (None, None).
    """
    m = re.search(
        rf"преименувай\s+{keyword}\s+(.+?)\s+на\s+(.+)$",
        user_input,
        re.IGNORECASE,
    )
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()


# ──────────────────────────────────────────────────────────────
# КЛУБ
# ──────────────────────────────────────────────────────────────

def handle_rename_club(user_input: str) -> str:
    """
    Команда: Преименувай клуб <Старо> на <Ново>
    Пример:  Преименувай клуб Левски на Левски София
    """
    old, new = _parse_rename(user_input, r"клуб")
    if not old or not new:
        result = (
            "❌ Грешен формат.\n"
            "   Пример: Преименувай клуб Левски на Левски София"
        )
        log_command(user_input, "rename_club", result=result)
        return result

    result = rename_club(old, new)
    log_command(user_input, "rename_club",
                params={"old": old, "new": new}, result=result)
    return result


# ──────────────────────────────────────────────────────────────
# ИГРАЧ
# ──────────────────────────────────────────────────────────────

def handle_rename_player(user_input: str) -> str:
    """
    Команда: Преименувай играч <Старо> на <Ново>
    Пример:  Преименувай играч Иван Петров на Иван Стоянов
    """
    old, new = _parse_rename(user_input, r"играч")
    if not old or not new:
        result = (
            "❌ Грешен формат.\n"
            "   Пример: Преименувай играч Иван Петров на Иван Стоянов"
        )
        log_command(user_input, "rename_player", result=result)
        return result

    result = rename_player(old, new)
    log_command(user_input, "rename_player",
                params={"old": old, "new": new}, result=result)
    return result


# ──────────────────────────────────────────────────────────────
# ЛИГА
# ──────────────────────────────────────────────────────────────

def handle_rename_league(user_input: str) -> str:
    """
    Команда: Преименувай лига <Старо> <ГГГГ/ГГГГ> на <Ново>
    Пример:  Преименувай лига Първа лига 2025/2026 на Суперлига
    """
    m = re.search(
        r"преименувай\s+лига\s+(.+?)\s+(\d{4}/\d{4})\s+на\s+(.+)$",
        user_input,
        re.IGNORECASE,
    )
    if not m:
        result = (
            "❌ Грешен формат.\n"
            "   Пример: Преименувай лига Първа лига 2025/2026 на Суперлига"
        )
        log_command(user_input, "rename_league", result=result)
        return result

    old_name = m.group(1).strip()
    season   = m.group(2).strip()
    new_name = m.group(3).strip()

    result = rename_league(old_name, season, new_name)
    log_command(user_input, "rename_league",
                params={"old": old_name, "season": season, "new": new_name},
                result=result)
    return result
