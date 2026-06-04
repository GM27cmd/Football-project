# src/services/standings_service.py
#
# Правила:
#   handler → service → repo (без SQL тук)
#   Тук живее цялата логика на изчислението.
 
from repositories.standings_repo import (
    get_league_id_by_name_season,
    get_clubs_in_league,
    get_played_matches,
)
 
 
# ─────────────────────────────────────────────────
# ВЪТРЕШНИ ПОМОЩНИ ФУНКЦИИ
# ─────────────────────────────────────────────────
 
def _empty_row(club_id: int, club_name: str) -> dict:
    """Начална статистика с нули за един отбор."""
    return {
        "club_id": club_id,
        "name":    club_name,
        "MP": 0,   # Изиграни
        "W":  0,   # Победи
        "D":  0,   # Равни
        "L":  0,   # Загуби
        "GF": 0,   # Вкарани голове
        "GA": 0,   # Допуснати голове
        "GD": 0,   # Голова разлика (изчислява се накрая)
        "PTS": 0,  # Точки
    }
 
 
def _apply_match(stats: dict, home_id: int, away_id: int,
                 hg: int, ag: int) -> None:
    """
    Обновява статистиката и за двата отбора след един мач.
    Победа = 3 т., равен = 1 т., загуба = 0 т.
    """
    # Изиграни мачове
    stats[home_id]["MP"] += 1
    stats[away_id]["MP"] += 1
 
    # Голове
    stats[home_id]["GF"] += hg
    stats[home_id]["GA"] += ag
    stats[away_id]["GF"] += ag
    stats[away_id]["GA"] += hg
 
    # Резултат
    if hg > ag:                          # домакинът печели
        stats[home_id]["W"]   += 1
        stats[home_id]["PTS"] += 3
        stats[away_id]["L"]   += 1
    elif ag > hg:                        # гостът печели
        stats[away_id]["W"]   += 1
        stats[away_id]["PTS"] += 3
        stats[home_id]["L"]   += 1
    else:                                # равен
        stats[home_id]["D"]   += 1
        stats[home_id]["PTS"] += 1
        stats[away_id]["D"]   += 1
        stats[away_id]["PTS"] += 1
 
 
def _sort_table(table: list) -> None:
    """
    Сортиране (низходящо за числата, възходящо за имената):
      1. Точки
      2. Голова разлика
      3. Вкарани голове
      4. Име (азбучен за стабилност)
    """
    table.sort(key=lambda r: (-r["PTS"], -r["GD"], -r["GF"], r["name"]))
 
 
def _format_table(league_name: str, season: str,
                  table: list, has_played: bool) -> str:
    """Форматира готовата таблица като четим низ."""
    SEP  = "─" * 62
    HEAD = (
        f"{'№':<4}"
        f"{'Отбор':<22}"
        f"{'ИГ':>3}"
        f"{'В':>3}"
        f"{'Р':>3}"
        f"{'З':>3}"
        f"{'ВГ':>4}"
        f"{'ДГ':>4}"
        f"{'ГР':>5}"
        f"{'Т':>4}"
    )
 
    lines = [
        f"🏆 Класиране: {league_name} ({season})",
        SEP,
        HEAD,
        SEP,
    ]
 
    if not has_played:
        lines.append("⚠️  Няма изиграни мачове — таблица с нули:")
        lines.append("")
 
    for pos, row in enumerate(table, 1):
        gd_str = f"+{row['GD']}" if row["GD"] > 0 else str(row["GD"])
        lines.append(
            f"{pos:<4}"
            f"{row['name']:<22}"
            f"{row['MP']:>3}"
            f"{row['W']:>3}"
            f"{row['D']:>3}"
            f"{row['L']:>3}"
            f"{row['GF']:>4}"
            f"{row['GA']:>4}"
            f"{gd_str:>5}"
            f"{row['PTS']:>4}"
        )
 
    lines.append(SEP)
    return "\n".join(lines)
 
 
# ─────────────────────────────────────────────────
# ПУБЛИЧЕН ИНТЕРФЕЙС
# ─────────────────────────────────────────────────
 
def get_standings(league_name: str, season: str) -> str:
    """
    Главна функция — изчислява и връща форматирана таблица
    на класирането за избрана лига и сезон.
 
    Алгоритъм (по изискване):
      1. Вземи всички отбори от League_Teams.
      2. Вземи всички изиграни мачове (status = 'played').
      3. За всеки мач обнови MP / GF / GA / W / D / L / PTS.
      4. Изчисли GD = GF − GA.
      5. Сортирай по правилата.
      6. Форматирай и върни.
    """
 
    # ── 1. Валидация: лигата съществува ли? ──────────────────────
    league_id = get_league_id_by_name_season(league_name, season)
    if not league_id:
        return f"❌ Лигата '{league_name}' ({season}) не съществува."
 
    # ── 2. Отбори в лигата ────────────────────────────────────────
    clubs = get_clubs_in_league(league_id)
    if not clubs:
        return (
            f"❌ В лига '{league_name}' ({season}) няма регистрирани отбори.\n"
            f"   Добави отбори с: Добави отбор <Отбор> в {league_name} {season}"
        )
 
    valid_ids = {club_id for club_id, _ in clubs}
 
    # ── 3. Инициализация на статистиката ──────────────────────────
    stats = {
        club_id: _empty_row(club_id, name)
        for club_id, name in clubs
    }
 
    # ── 4. Обработка на изиграните мачове ─────────────────────────
    matches = get_played_matches(league_id)
 
    for match_id, home_id, away_id, hg, ag in matches:
        # Логическа проверка: и двата отбора трябва да са в лигата
        if home_id not in valid_ids or away_id not in valid_ids:
            # Несъответствие в данните — пропускаме мача (не срива системата)
            continue
        _apply_match(stats, home_id, away_id, hg, ag)
 
    # ── 5. Изчисли голова разлика ─────────────────────────────────
    for row in stats.values():
        row["GD"] = row["GF"] - row["GA"]
 
    # ── 6. Сортиране ──────────────────────────────────────────────
    table = list(stats.values())
    _sort_table(table)
 
    # ── 7. Проверка за изиграни мачове ────────────────────────────
    has_played = any(row["MP"] > 0 for row in table)
 
    # ── 8. Форматиране и връщане ──────────────────────────────────
    return _format_table(league_name, season, table, has_played)