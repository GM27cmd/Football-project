# src/chatbot/handlers_rename.py
#
# Парсинг на командите за преименуване.
# Структура: handler → rename_service → DB

import re
from services.rename_service import rename_club, rename_player, rename_league
from utils.logger import log_command


# ──────────────────────────────────────────────────────────────
# КЛУБ
# ──────────────────────────────────────────────────────────────

def handle_rename_club(user_input: str) -> str:
    """
    Команда: Преименувай клуб <Старо> на <Ново>
    Пример:  Преименувай клуб Левски на Левски София
    """
    m = re.search(
        r"преименувай\s+клуб\s+(.+?)\s+на\s+(.+)$",
        user_input, re.IGNORECASE,
    )
    if not m:
        result = (
            "❌ Грешен формат.\n"
            "   Пример: Преименувай клуб Левски на Левски София"
        )
        log_command(user_input, "rename_club", result=result)
        return result

    old = m.group(1).strip()
    new = m.group(2).strip()

    result = rename_club(old, new)
    log_command(user_input, "rename_club",
                params={"old": old, "new": new}, result=result)
    return result


# ──────────────────────────────────────────────────────────────
# ИГРАЧ  — задължително с отбор
# ──────────────────────────────────────────────────────────────

def handle_rename_player(user_input: str) -> str:
    """
    Команда: Преименувай играч <Старо> от <Отбор> на <Ново>
    Пример:  Преименувай играч Иван Петров от Левски на Иван Стоянов

    Отборът е задължителен — избягва объркване при съименници
    в различни клубове (напр. двама "Петър Георгиев").
    """
    m = re.search(
        r"преименувай\s+играч\s+(.+?)\s+от\s+(.+?)\s+на\s+(.+)$",
        user_input, re.IGNORECASE,
    )
    if not m:
        result = (
            "❌ Грешен формат.\n"
            "   Пример: Преименувай играч Иван Петров от Левски на Иван Стоянов\n"
            "   ⚠️  Отборът е задължителен!"
        )
        log_command(user_input, "rename_player", result=result)
        return result

    old_name  = m.group(1).strip()
    club_name = m.group(2).strip()
    new_name  = m.group(3).strip()

    result = rename_player(old_name, club_name, new_name)
    log_command(user_input, "rename_player",
                params={"old": old_name, "club": club_name, "new": new_name},
                result=result)
    return result


# ──────────────────────────────────────────────────────────────
# ЛИГА  — може да се смени и сезонът
# ──────────────────────────────────────────────────────────────

def handle_rename_league(user_input: str) -> str:
    """
    Команда: Преименувай лига <Старо> <ГГГГ/ГГГГ> на <Ново> [ГГГГ/ГГГГ]
    Примери:
        Преименувай лига Първа лига 2025/2026 на Суперлига
        Преименувай лига Първа лига 2025/2026 на Суперлига 2026/2027
    """
    m = re.search(
        r"преименувай\s+лига\s+(.+?)\s+(\d{4}/\d{4})\s+на\s+(.+?)(?:\s+(\d{4}/\d{4}))?$",
        user_input, re.IGNORECASE,
    )
    if not m:
        result = (
            "❌ Грешен формат.\n"
            "   Само ime:          Преименувай лига Първа лига 2025/2026 на Суперлига\n"
            "   Ime + нов сезон:   Преименувай лига Първа лига 2025/2026 на Суперлига 2026/2027"
        )
        log_command(user_input, "rename_league", result=result)
        return result

    old_name   = m.group(1).strip()
    old_season = m.group(2).strip()
    new_name   = m.group(3).strip()
    new_season = m.group(4).strip() if m.group(4) else None   # None → запазва стария сезон

    result = rename_league(old_name, old_season, new_name, new_season)
    log_command(user_input, "rename_league",
                params={
                    "old": old_name, "old_season": old_season,
                    "new": new_name, "new_season": new_season or old_season,
                },
                result=result)
    return result
