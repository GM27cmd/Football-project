# src/services/stats_service.py
#
# Модул G — Статистика
# Три функции:
#   1. get_top_scorers()    – голмайстори
#   2. get_discipline()     – дисциплина (картони)
#   3. get_team_scoring()   – отборна резултатност
#
# Структура: handler → service → DB (execute_query)

from database.db import execute_query


# ──────────────────────────────────────────────────────────────
# ПОМОЩНА: проверка дали лигата съществува
# ──────────────────────────────────────────────────────────────

def _get_league_id(league_name: str, season: str):
    """Връща league_id или None."""
    result = execute_query(
        "SELECT league_id FROM Leagues WHERE name = ? AND season = ?",
        (league_name, season),
        fetch=True,
    )
    return result[0][0] if result else None


# ──────────────────────────────────────────────────────────────
# 1. ГОЛМАЙСТОРИ
# ──────────────────────────────────────────────────────────────

def get_top_scorers(league_name: str, season: str, limit: int = 10) -> str:
    """
    Показва топ голмайстори за дадена лига и сезон.
    Командa: Покажи голмайстори <лига> <сезон>
    """
    league_id = _get_league_id(league_name, season)
    if not league_id:
        return f"❌ Лига '{league_name}' ({season}) не е намерена."

    rows = execute_query(
        """
        SELECT
            p.full_name,
            c.name        AS club_name,
            COUNT(g.goal_id) AS goals
        FROM   Goals g
        JOIN   Players p  ON g.player_id = p.player_id
        JOIN   Clubs   c  ON g.club_id   = c.club_id
        JOIN   Matches m  ON g.match_id  = m.match_id
        WHERE  m.league_id    = ?
          AND  g.is_own_goal  = 0
        GROUP  BY g.player_id
        ORDER  BY goals DESC, p.full_name
        LIMIT  ?
        """,
        (league_id, limit),
        fetch=True,
    )

    if not rows:
        return (
            f"⚠️  Няма записани голове за {league_name} ({season}).\n"
            f"   Запиши голове с: Гол <Играч> <Отбор> <минута>"
        )

    SEP  = "─" * 46
    HEAD = f"{'№':<4}{'Играч':<24}{'Отбор':<18}{'Голове':>6}"
    lines = [
        f"⚽ ГОЛМАЙСТОРИ: {league_name} ({season})",
        SEP, HEAD, SEP,
    ]
    for pos, (name, club, goals) in enumerate(rows, 1):
        medal = ("🥇" if pos == 1 else "🥈" if pos == 2 else "🥉" if pos == 3 else f"{pos}. ")
        lines.append(f"{medal:<4}{name:<24}{club:<18}{goals:>6}")
    lines.append(SEP)

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# 2. ДИСЦИПЛИНА
# ──────────────────────────────────────────────────────────────

def get_discipline(league_name: str, season: str, limit: int = 10) -> str:
    """
    Показва играчите с най-много картони.
    Командa: Покажи дисциплина <лига> <сезон>
    Точки дисциплина: жълт = 1, червен = 3
    """
    league_id = _get_league_id(league_name, season)
    if not league_id:
        return f"❌ Лига '{league_name}' ({season}) не е намерена."

    rows = execute_query(
        """
        SELECT
            p.full_name,
            c.name                                           AS club_name,
            SUM(CASE WHEN ca.card_type = 'Y' THEN 1 ELSE 0 END) AS yellow,
            SUM(CASE WHEN ca.card_type = 'R' THEN 1 ELSE 0 END) AS red,
            SUM(CASE WHEN ca.card_type = 'Y' THEN 1
                     WHEN ca.card_type = 'R' THEN 3 ELSE 0 END) AS pts
        FROM   Cards   ca
        JOIN   Players p  ON ca.player_id = p.player_id
        JOIN   Clubs   c  ON ca.club_id   = c.club_id
        JOIN   Matches m  ON ca.match_id  = m.match_id
        WHERE  m.league_id = ?
        GROUP  BY ca.player_id
        ORDER  BY pts DESC, yellow DESC, p.full_name
        LIMIT  ?
        """,
        (league_id, limit),
        fetch=True,
    )

    if not rows:
        return (
            f"⚠️  Няма записани картони за {league_name} ({season}).\n"
            f"   Запиши картон с: Картон <Играч> <Отбор> Y/R <минута>"
        )

    SEP  = "─" * 52
    HEAD = f"{'№':<4}{'Играч':<22}{'Отбор':<16}{'🟨':>4}{'🟥':>4}{'Т':>4}"
    lines = [
        f"🟨 ДИСЦИПЛИНА: {league_name} ({season})",
        f"   (Точки: жълт=1, червен=3)",
        SEP, HEAD, SEP,
    ]
    for pos, (name, club, yellow, red, pts) in enumerate(rows, 1):
        lines.append(
            f"{pos:<4}{name:<22}{club:<16}{yellow:>4}{red:>4}{pts:>4}"
        )
    lines.append(SEP)

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# 3. ОТБОРНА РЕЗУЛТАТНОСТ
# ──────────────────────────────────────────────────────────────

def get_team_scoring(league_name: str, season: str) -> str:
    """
    Показва отборна статистика: голове вкарани, допуснати,
    разлика и средно на мач.
    Командa: Покажи резултатност <лига> <сезон>
    """
    league_id = _get_league_id(league_name, season)
    if not league_id:
        return f"❌ Лига '{league_name}' ({season}) не е намерена."

    # Всички изиграни мачове в лигата
    matches = execute_query(
        """
        SELECT home_club_id, away_club_id, home_goals, away_goals
        FROM   Matches
        WHERE  league_id  = ?
          AND  status     = 'played'
          AND  home_goals IS NOT NULL
        """,
        (league_id,),
        fetch=True,
    )

    # Отбори в лигата
    clubs = execute_query(
        """
        SELECT c.club_id, c.name
        FROM   League_Teams lt
        JOIN   Clubs c ON lt.club_id = c.club_id
        WHERE  lt.league_id = ?
        ORDER  BY c.name
        """,
        (league_id,),
        fetch=True,
    )

    if not clubs:
        return f"❌ Няма отбори в лига '{league_name}' ({season})."
    if not matches:
        return (
            f"⚠️  Няма изиграни мачове за {league_name} ({season}).\n"
            f"   Запиши резултат с: Резултат <Домакин>-<Гост> X:Y запиши"
        )

    # Изчисляване по отбор
    stats = {club_id: {"name": name, "mp": 0, "gf": 0, "ga": 0}
             for club_id, name in clubs}

    for home_id, away_id, hg, ag in matches:
        if home_id in stats:
            stats[home_id]["mp"] += 1
            stats[home_id]["gf"] += hg
            stats[home_id]["ga"] += ag
        if away_id in stats:
            stats[away_id]["mp"] += 1
            stats[away_id]["gf"] += ag
            stats[away_id]["ga"] += hg

    # Сортиране по вкарани голове
    table = sorted(stats.values(), key=lambda r: (-r["gf"], r["ga"], r["name"]))

    SEP  = "─" * 58
    HEAD = (f"{'Отбор':<22}{'ИГ':>4}{'ВГ':>5}"
            f"{'ДГ':>5}{'ГР':>5}{'СР/м':>7}")
    lines = [
        f"📊 ОТБОРНА РЕЗУЛТАТНОСТ: {league_name} ({season})",
        SEP, HEAD, SEP,
    ]
    for r in table:
        mp   = r["mp"]
        gf   = r["gf"]
        ga   = r["ga"]
        gd   = gf - ga
        avg  = gf / mp if mp else 0.0
        gd_s = f"+{gd}" if gd > 0 else str(gd)
        lines.append(
            f"{r['name']:<22}{mp:>4}{gf:>5}{ga:>5}{gd_s:>5}{avg:>7.2f}"
        )
    lines.append(SEP)
    lines.append("   ИГ=изиграни  ВГ=вкарани  ДГ=допуснати  ГР=разлика  СР/м=средно/мач")

    return "\n".join(lines)
