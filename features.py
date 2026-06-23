# src/ai/features.py
#
# Отговаря САМО за извличане и изчисляване на характеристики (features)
# от базата данни. Без логика за прогнози — само данни.
#
# Структура: handler → ai_service → features (тук) → DB

from database.db import execute_query

MIN_MATCHES = 5   # Минимален брой изиграни мача за прогноза


# ──────────────────────────────────────────────────
# НАМИРАНЕ НА КЛУБОВЕ И ЛИГИ
# ──────────────────────────────────────────────────

def get_club_id_by_name(name: str):
    """
    Търси клуб по частично съвпадение на името (LIKE).
    Връща (club_id, full_name) или (None, None).
    Raises ValueError при двусмислено съвпадение.
    """
    result = execute_query(
        "SELECT club_id, name FROM Clubs WHERE LOWER(name) LIKE LOWER(?)",
        (f"%{name}%",),
        fetch=True,
    )
    if not result:
        return None, None
    if len(result) > 1:
        names = ", ".join(r[1] for r in result)
        raise ValueError(f"❌ Намерени няколко отбора: {names}. Уточни.")
    return result[0][0], result[0][1]


def get_league_for_teams(home_id: int, away_id: int):
    """
    Намира обща лига, в която участват и двата отбора.
    Връща league_id или None.
    """
    result = execute_query(
        """
        SELECT lt1.league_id
        FROM   League_Teams lt1
        JOIN   League_Teams lt2 ON lt1.league_id = lt2.league_id
        WHERE  lt1.club_id = ? AND lt2.club_id = ?
        LIMIT  1
        """,
        (home_id, away_id),
        fetch=True,
    )
    return result[0][0] if result else None


# ──────────────────────────────────────────────────
# ДАННИ ОТ МАЧОВЕ
# ──────────────────────────────────────────────────

def get_last_n_matches(club_id: int, league_id: int, n: int = MIN_MATCHES):
    """
    Връща последните N изиграни мача за даден клуб в дадена лига.
    Ред: (match_id, home_club_id, away_club_id, home_goals, away_goals)
    Наредени от най-нов към най-стар (по match_id DESC).
    """
    return execute_query(
        """
        SELECT match_id, home_club_id, away_club_id, home_goals, away_goals
        FROM   Matches
        WHERE  league_id = ?
          AND  (home_club_id = ? OR away_club_id = ?)
          AND  status       = 'played'
          AND  home_goals   IS NOT NULL
          AND  away_goals   IS NOT NULL
        ORDER  BY match_id DESC
        LIMIT  ?
        """,
        (league_id, club_id, club_id, n),
        fetch=True,
    )


# ──────────────────────────────────────────────────
# ИЗЧИСЛЯВАНЕ НА ХАРАКТЕРИСТИКИ
# ──────────────────────────────────────────────────

def calculate_form(club_id: int, matches: list) -> float:
    """
    Форма = (точки от последните N мача) / (N * 3).
    Победа = 3т., равен = 1т., загуба = 0т.
    Връща стойност в [0.0, 1.0].
    """
    if not matches:
        return 0.0
    total = 0
    for _, home_id, away_id, hg, ag in matches:
        if home_id == club_id:
            if hg > ag:    total += 3
            elif hg == ag: total += 1
        else:
            if ag > hg:    total += 3
            elif ag == hg: total += 1
    return total / (len(matches) * 3)


def get_form_sequence(club_id: int, matches: list) -> list:
    """
    Връща поредица от резултати за последните N мача (от нов към стар).
    Всеки елемент е 'W' (победа), 'D' (равен) или 'L' (загуба).
    """
    seq = []
    for _, home_id, away_id, hg, ag in matches:
        if home_id == club_id:
            if hg > ag:    seq.append("W")
            elif hg == ag: seq.append("D")
            else:          seq.append("L")
        else:
            if ag > hg:    seq.append("W")
            elif ag == hg: seq.append("D")
            else:          seq.append("L")
    return seq


def calculate_attack_defense(club_id: int, matches: list) -> tuple:
    """
    Изчислява средните голове вкарани и допуснати на мач.
    Връща (avg_scored, avg_conceded).
    """
    if not matches:
        return 0.0, 0.0
    scored = conceded = 0
    for _, home_id, away_id, hg, ag in matches:
        if home_id == club_id:
            scored   += hg
            conceded += ag
        else:
            scored   += ag
            conceded += hg
    n = len(matches)
    return scored / n, conceded / n


def get_league_position(club_id: int, league_id: int) -> tuple:
    """
    Изчислява текущата позиция на отбора в класирането.
    Използва същия алгоритъм като standings_service.
    Връща (позиция, общ_брой_отбори).
    Позиция 1 = лидер.
    """
    clubs = execute_query(
        "SELECT club_id FROM League_Teams WHERE league_id = ?",
        (league_id,),
        fetch=True,
    )
    if not clubs:
        return 1, 1

    total = len(clubs)
    stats = {c[0]: {"pts": 0, "gd": 0} for c in clubs}

    played = execute_query(
        """
        SELECT home_club_id, away_club_id, home_goals, away_goals
        FROM   Matches
        WHERE  league_id   = ?
          AND  status      = 'played'
          AND  home_goals  IS NOT NULL
          AND  away_goals  IS NOT NULL
        """,
        (league_id,),
        fetch=True,
    )
    for home_id, away_id, hg, ag in played:
        if home_id not in stats or away_id not in stats:
            continue
        stats[home_id]["gd"] += hg - ag
        stats[away_id]["gd"] += ag - hg
        if hg > ag:
            stats[home_id]["pts"] += 3
        elif ag > hg:
            stats[away_id]["pts"] += 3
        else:
            stats[home_id]["pts"] += 1
            stats[away_id]["pts"] += 1

    sorted_clubs = sorted(stats.items(), key=lambda x: (-x[1]["pts"], -x[1]["gd"]))
    for pos, (cid, _) in enumerate(sorted_clubs, 1):
        if cid == club_id:
            return pos, total

    return total, total  # fallback: последно място


# ──────────────────────────────────────────────────
# ГЛАВНА ФУНКЦИЯ – ИЗВЛИЧАНЕ НА ВСИЧКИ FEATURES
# ──────────────────────────────────────────────────

def extract_features(home_id: int, away_id: int, league_id: int,
                     n: int = MIN_MATCHES) -> dict:
    """
    Извлича всички характеристики нужни за прогнозата.
    Raises ValueError ако няма достатъчно данни.

    Върнат речник (dict) с ключове:
        form_h, form_a           – форма [0,1]
        seq_h, seq_a             – поредица W/D/L (list)
        gf_h, ga_h, gf_a, ga_a  – средни голове/мач
        pos_score_h, pos_score_a – нормализирана позиция [0,1]
        pos_h, pos_a             – реална позиция (int)
        n_h, n_a                 – брой използвани мача
    """
    home_matches = get_last_n_matches(home_id, league_id, n)
    away_matches = get_last_n_matches(away_id, league_id, n)

    if len(home_matches) < n:
        raise ValueError(
            f"❌ Недостатъчно мачове за домакина "
            f"(налични: {len(home_matches)}, нужни: минимум {n}).\n"
            f"   Запиши поне {n} изиграни мача, за да работи прогнозата."
        )
    if len(away_matches) < n:
        raise ValueError(
            f"❌ Недостатъчно мачове за госта "
            f"(налични: {len(away_matches)}, нужни: минимум {n}).\n"
            f"   Запиши поне {n} изиграни мача, за да работи прогнозата."
        )

    form_h = calculate_form(home_id, home_matches)
    form_a = calculate_form(away_id, away_matches)

    seq_h = get_form_sequence(home_id, home_matches)
    seq_a = get_form_sequence(away_id, away_matches)

    gf_h, ga_h = calculate_attack_defense(home_id, home_matches)
    gf_a, ga_a = calculate_attack_defense(away_id, away_matches)

    pos_h, total = get_league_position(home_id, league_id)
    pos_a, _     = get_league_position(away_id, league_id)

    # Нормализиране: 1-во място → 1.0, последно → ~0
    pos_score_h = (total - pos_h + 1) / total if total > 0 else 0.5
    pos_score_a = (total - pos_a + 1) / total if total > 0 else 0.5

    return {
        "form_h":       form_h,
        "form_a":       form_a,
        "seq_h":        seq_h,
        "seq_a":        seq_a,
        "gf_h":         gf_h,
        "ga_h":         ga_h,
        "gf_a":         gf_a,
        "ga_a":         ga_a,
        "pos_score_h":  pos_score_h,
        "pos_score_a":  pos_score_a,
        "pos_h":        pos_h,
        "pos_a":        pos_a,
        "n_h":          len(home_matches),
        "n_a":          len(away_matches),
    }