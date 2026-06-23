# seed_matches.py
#
# УНИВЕРСАЛЕН скрипт — работи за ВСИЧКИ лиги и отбори в БД.
#
# Пускаш го от папката Football-project:
#   python seed_matches.py
#
# Какво прави:
#   1. Открива автоматично всички лиги в БД
#   2. За всяка лига взима всички отбори
#   3. Попълва резултати на насрочените мачове (първи кръг)
#   4. Ако отборите имат < 5 изиграни мача → добавя втори кръг (реванш)
#   5. Записва голмайстори за всеки мач
#   → Безопасен при многократно пускане (идемпотентен)

import sqlite3
import os
import random

DB_FILE = os.path.join(os.path.dirname(__file__), "football.db")
MIN_MATCHES = 5   # минимум за AI прогнозата


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ──────────────────────────────────────────────────────────────
# ГЕНЕРАТОР НА РЕАЛИСТИЧЕН РЕЗУЛТАТ
# ──────────────────────────────────────────────────────────────

# Тегла за брой голове: 0 гола=30%, 1=35%, 2=20%, 3=10%, 4=5%
GOAL_WEIGHTS = [30, 35, 20, 10, 5]

def random_goals(seed_val):
    """Генерира брой голове с реалистично разпределение."""
    rng = random.Random(seed_val)
    population = []
    for goals, weight in enumerate(GOAL_WEIGHTS):
        population.extend([goals] * weight)
    return rng.choice(population)


def generate_score(home_id, away_id, match_index):
    """
    Генерира (home_goals, away_goals) детерминирано по
    комбинация от club_id-та и индекс на мача.
    Резултатът е винаги същият при същите входни данни.
    """
    seed_h = home_id * 1000 + away_id + match_index
    seed_a = away_id * 1000 + home_id + match_index + 7
    return random_goals(seed_h), random_goals(seed_a)


# ──────────────────────────────────────────────────────────────
# ГОЛМАЙСТОРИ
# ──────────────────────────────────────────────────────────────

def get_scorers(cursor, club_id, count):
    """Взима нападатели/полузащитници от клуба."""
    if count == 0:
        return []
    cursor.execute(
        """
        SELECT player_id FROM Players
        WHERE club_id = ?
        ORDER BY CASE position WHEN 'FW' THEN 1 WHEN 'MF' THEN 2 ELSE 3 END,
                 player_id
        LIMIT ?
        """,
        (club_id, count + 3),
    )
    rows = cursor.fetchall()
    players = [r[0] for r in rows]
    if not players:
        return []
    rng = random.Random(club_id * 999)
    rng.shuffle(players)
    return players[:count]


def insert_goals(cursor, match_id, club_id, num_goals):
    """Записва голове за клуба в мача."""
    if num_goals == 0:
        return
    scorers = get_scorers(cursor, club_id, num_goals)
    if not scorers:
        return
    rng = random.Random(match_id * club_id)
    minutes = sorted(rng.sample(range(5, 90), min(num_goals, 85)))
    for i, player_id in enumerate(scorers):
        minute = minutes[i] if i < len(minutes) else 89
        cursor.execute(
            """
            INSERT OR IGNORE INTO Goals
                (match_id, player_id, club_id, minute)
            VALUES (?, ?, ?, ?)
            """,
            (match_id, player_id, club_id, minute),
        )


# ──────────────────────────────────────────────────────────────
# ОСНОВНА ЛОГИКА
# ──────────────────────────────────────────────────────────────

def count_played(cursor, league_id, club_id):
    """Брой изиграни мача за отбора в лигата."""
    cursor.execute(
        """
        SELECT COUNT(*) FROM Matches
        WHERE league_id = ?
          AND (home_club_id = ? OR away_club_id = ?)
          AND status = 'played'
        """,
        (league_id, club_id, club_id),
    )
    return cursor.fetchone()[0]


def set_match_result(cursor, match_id, home_id, away_id, hg, ag):
    """Записва резултат и голове за мач."""
    cursor.execute(
        """
        UPDATE Matches
        SET home_goals = ?, away_goals = ?, status = 'played'
        WHERE match_id = ?
        """,
        (hg, ag, match_id),
    )
    insert_goals(cursor, match_id, home_id, hg)
    insert_goals(cursor, match_id, away_id, ag)


def add_new_match(cursor, league_id, home_id, away_id, hg, ag, round_no):
    """Добавя нов мач (втори кръг) и му записва резултат."""
    cursor.execute(
        """
        INSERT INTO Matches
            (league_id, round_no, home_club_id, away_club_id,
             home_goals, away_goals, status)
        VALUES (?, ?, ?, ?, ?, ?, 'played')
        """,
        (league_id, round_no, home_id, away_id, hg, ag),
    )
    match_id = cursor.lastrowid
    insert_goals(cursor, match_id, home_id, hg)
    insert_goals(cursor, match_id, away_id, ag)
    return match_id


def match_exists(cursor, league_id, home_id, away_id):
    """Проверява дали вече има изигран мач (в двете посоки)."""
    cursor.execute(
        """
        SELECT COUNT(*) FROM Matches
        WHERE league_id = ?
          AND home_club_id = ? AND away_club_id = ?
          AND status = 'played'
        """,
        (league_id, home_id, away_id),
    )
    return cursor.fetchone()[0] > 0


def process_league(cursor, league_id, league_name, season):
    """Обработва една лига — попълва и/или добавя мачове."""
    print(f"\n🏆 {league_name} ({season})  [ID={league_id}]")
    print("─" * 50)

    # Отбори в лигата
    cursor.execute(
        """
        SELECT c.club_id, c.name
        FROM League_Teams lt
        JOIN Clubs c ON lt.club_id = c.club_id
        WHERE lt.league_id = ?
        ORDER BY c.club_id
        """,
        (league_id,),
    )
    teams = cursor.fetchall()

    if len(teams) < 2:
        print("  ⚠️  По-малко от 2 отбора — пропускам.")
        return 0, 0

    updated = 0
    added   = 0

    # ── Стъпка 1: Попълни насрочените мачове ────────────────
    cursor.execute(
        """
        SELECT match_id, home_club_id, away_club_id
        FROM Matches
        WHERE league_id = ? AND status = 'scheduled'
        ORDER BY round_no, match_id
        """,
        (league_id,),
    )
    scheduled = cursor.fetchall()

    for idx, (match_id, home_id, away_id) in enumerate(scheduled):
        hg, ag = generate_score(home_id, away_id, idx)
        set_match_result(cursor, match_id, home_id, away_id, hg, ag)

        home_name = next(t[1] for t in teams if t[0] == home_id)
        away_name = next(t[1] for t in teams if t[0] == away_id)
        print(f"  ✅ обновен   {home_name} {hg}:{ag} {away_name}")
        updated += 1

    # ── Стъпка 2: Добави реванши ако < MIN_MATCHES ──────────
    # Намираме max round_no
    cursor.execute(
        "SELECT COALESCE(MAX(round_no), 0) FROM Matches WHERE league_id = ?",
        (league_id,),
    )
    max_round = cursor.fetchone()[0]

    # Проверяваме дали някой отбор има < MIN_MATCHES изиграни
    needs_more = any(
        count_played(cursor, league_id, club_id) < MIN_MATCHES
        for club_id, _ in teams
    )

    if needs_more:
        print(f"\n  📋 Добавям реванши (нужни са мин. {MIN_MATCHES} мача/отбор)...")

        # Генерираме всички двойки (реванш = разменени домакин/гост)
        pairs = [
            (teams[i][0], teams[j][0])
            for i in range(len(teams))
            for j in range(len(teams))
            if i != j
        ]

        round_counter = max_round
        pair_idx      = 0

        for home_id, away_id in pairs:
            if count_played(cursor, league_id, home_id) >= MIN_MATCHES \
               and count_played(cursor, league_id, away_id) >= MIN_MATCHES:
                continue

            if match_exists(cursor, league_id, home_id, away_id):
                continue

            # Нова програма: всяка двойка в отделен кръг
            if pair_idx % (len(teams) // 2) == 0:
                round_counter += 1
            pair_idx += 1

            hg, ag = generate_score(away_id, home_id, pair_idx + 100)
            match_id = add_new_match(
                cursor, league_id, home_id, away_id, hg, ag, round_counter
            )

            home_name = next(t[1] for t in teams if t[0] == home_id)
            away_name = next(t[1] for t in teams if t[0] == away_id)
            print(f"  ➕ добавен   {home_name} {hg}:{ag} {away_name}")
            added += 1

    # Обобщение за лигата
    print(f"\n  Резултат: {updated} обновени, {added} добавени")
    for club_id, name in teams:
        played = count_played(cursor, league_id, club_id)
        status = "✅" if played >= MIN_MATCHES else "⚠️ "
        print(f"    {status}  {name}: {played} изиграни мача")

    return updated, added


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(DB_FILE):
        print(f"❌ Не намирам БД: {DB_FILE}")
        print("   Увери се, че стартираш скрипта от папката Football-project")
        return

    conn   = get_conn()
    cursor = conn.cursor()

    # Всички лиги
    cursor.execute("SELECT league_id, name, season FROM Leagues ORDER BY league_id")
    leagues = cursor.fetchall()

    if not leagues:
        print("❌ Няма лиги в базата данни.")
        print("   Създай лига първо с: Създай лига Първа лига 2025/2026")
        conn.close()
        return

    print(f"🔍 Намерени {len(leagues)} лига/и в БД\n")

    total_upd = total_add = 0
    for league_id, name, season in leagues:
        upd, add = process_league(cursor, league_id, name, season)
        total_upd += upd
        total_add += add

    conn.commit()
    conn.close()

    print(f"""
══════════════════════════════════════════
✅  ГОТОВО!
   Обновени мачове : {total_upd}
   Добавени мачове : {total_add}
══════════════════════════════════════════
Сега можеш да тестваш (за всяка лига):

  Покажи класиране Първа лига 2025/2026
  Прогноза Левски срещу Лудогорец
  Прогноза ЦСКА срещу Ботев Пловдив
══════════════════════════════════════════
""")


if __name__ == "__main__":
    main()