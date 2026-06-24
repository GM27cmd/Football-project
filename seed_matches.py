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
#   3. Попълва резултати на насрочените мачове
#   4. Ако отборите имат < 5 изиграни мача → добавя втори кръг
#   5. Записва голмайстори за всеки мач
#   6. Записва картони (жълти и червени) за всеки мач
#   → Безопасен при многократно пускане (идемпотентен)

import sqlite3
import os
import random

DB_FILE = os.path.join(os.path.dirname(__file__), "football.db")
MIN_MATCHES = 5


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ──────────────────────────────────────────────────────────────
# ГЕНЕРАТОР НА РЕЗУЛТАТ
# ──────────────────────────────────────────────────────────────

GOAL_WEIGHTS = [30, 35, 20, 10, 5]

def random_goals(seed_val):
    rng = random.Random(seed_val)
    population = []
    for goals, weight in enumerate(GOAL_WEIGHTS):
        population.extend([goals] * weight)
    return rng.choice(population)

def generate_score(home_id, away_id, match_index):
    seed_h = home_id * 1000 + away_id + match_index
    seed_a = away_id * 1000 + home_id + match_index + 7
    return random_goals(seed_h), random_goals(seed_a)


# ──────────────────────────────────────────────────────────────
# ГОЛМАЙСТОРИ
# ──────────────────────────────────────────────────────────────

def get_players_by_position(cursor, club_id, positions, limit):
    """Взима играчи от клуба по позиция."""
    placeholders = ",".join("?" * len(positions))
    cursor.execute(
        f"""
        SELECT player_id FROM Players
        WHERE  club_id  = ?
          AND  position IN ({placeholders})
        ORDER  BY player_id
        LIMIT  ?
        """,
        (club_id, *positions, limit),
    )
    return [r[0] for r in cursor.fetchall()]

def insert_goals(cursor, match_id, club_id, num_goals):
    if num_goals == 0:
        return
    # Предпочитаме FW и MF за голмайстори
    scorers = get_players_by_position(cursor, club_id, ("FW", "MF"), num_goals + 3)
    if not scorers:
        return
    rng = random.Random(match_id * club_id + 1)
    rng.shuffle(scorers)
    scorers = scorers[:num_goals]
    minutes = sorted(rng.sample(range(5, 90), min(num_goals, 85)))
    for i, player_id in enumerate(scorers):
        minute = minutes[i] if i < len(minutes) else 88
        cursor.execute(
            "INSERT OR IGNORE INTO Goals (match_id, player_id, club_id, minute) VALUES (?, ?, ?, ?)",
            (match_id, player_id, club_id, minute),
        )


# ──────────────────────────────────────────────────────────────
# КАРТОНИ  (ново!)
# ──────────────────────────────────────────────────────────────

def insert_cards(cursor, match_id, home_id, away_id):
    """
    Генерира реалистични картони за мача:
    - 1-3 жълти картона на отбор (рандомно)
    - ~20% шанс за червен картон (само 1 на мач)
    - Картоните се дават на DF и MF играчи (по-реалистично)
    - Идемпотентно: ако вече има картони за мача, пропуска
    """
    # Проверка дали вече има картони
    cursor.execute(
        "SELECT COUNT(*) FROM Cards WHERE match_id = ?", (match_id,)
    )
    if cursor.fetchone()[0] > 0:
        return

    rng = random.Random(match_id * 777)

    for club_id in (home_id, away_id):
        # Взимаме DF и MF за картони
        candidates = get_players_by_position(cursor, club_id, ("DF", "MF"), 8)
        if not candidates:
            continue
        rng.shuffle(candidates)

        # Брой жълти: 1-3
        num_yellow = rng.randint(1, 3)
        yellow_players = candidates[:num_yellow]

        # Минути за жълти (равномерно разпределени)
        yellow_minutes = sorted(rng.sample(range(10, 88), min(num_yellow, 78)))

        for i, player_id in enumerate(yellow_players):
            minute = yellow_minutes[i] if i < len(yellow_minutes) else 85
            cursor.execute(
                """
                INSERT OR IGNORE INTO Cards
                    (match_id, player_id, club_id, minute, card_type)
                VALUES (?, ?, ?, ?, 'Y')
                """,
                (match_id, player_id, club_id, minute),
            )

    # Червен картон (~20% шанс, само за един отбор)
    if rng.random() < 0.20:
        red_club = rng.choice([home_id, away_id])
        red_candidates = get_players_by_position(cursor, red_club, ("DF", "MF"), 6)
        if red_candidates:
            rng.shuffle(red_candidates)
            red_player = red_candidates[0]
            red_minute = rng.randint(50, 90)
            cursor.execute(
                """
                INSERT OR IGNORE INTO Cards
                    (match_id, player_id, club_id, minute, card_type)
                VALUES (?, ?, ?, ?, 'R')
                """,
                (match_id, red_player, red_club, red_minute),
            )


# ──────────────────────────────────────────────────────────────
# ОСНОВНА ЛОГИКА
# ──────────────────────────────────────────────────────────────

def count_played(cursor, league_id, club_id):
    cursor.execute(
        """
        SELECT COUNT(*) FROM Matches
        WHERE  league_id = ?
          AND  (home_club_id = ? OR away_club_id = ?)
          AND  status = 'played'
        """,
        (league_id, club_id, club_id),
    )
    return cursor.fetchone()[0]


def set_match_result(cursor, match_id, home_id, away_id, hg, ag):
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
    insert_cards(cursor, match_id, home_id, away_id)   # ← ново


def add_new_match(cursor, league_id, home_id, away_id, hg, ag, round_no):
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
    insert_cards(cursor, match_id, home_id, away_id)   # ← ново
    return match_id


def match_exists(cursor, league_id, home_id, away_id):
    cursor.execute(
        """
        SELECT COUNT(*) FROM Matches
        WHERE  league_id    = ?
          AND  home_club_id = ? AND away_club_id = ?
          AND  status = 'played'
        """,
        (league_id, home_id, away_id),
    )
    return cursor.fetchone()[0] > 0


def add_cards_to_existing(cursor, league_id):
    """
    Добавя картони на вече изиграни мачове, които нямат такива.
    Така скриптът работи и при повторно пускане върху стара БД.
    """
    cursor.execute(
        """
        SELECT match_id, home_club_id, away_club_id
        FROM   Matches
        WHERE  league_id = ? AND status = 'played'
        """,
        (league_id,),
    )
    matches = cursor.fetchall()
    added = 0
    for match_id, home_id, away_id in matches:
        cursor.execute(
            "SELECT COUNT(*) FROM Cards WHERE match_id = ?", (match_id,)
        )
        if cursor.fetchone()[0] == 0:
            insert_cards(cursor, match_id, home_id, away_id)
            added += 1
    return added


def process_league(cursor, league_id, league_name, season):
    print(f"\n🏆 {league_name} ({season})  [ID={league_id}]")
    print("─" * 50)

    cursor.execute(
        """
        SELECT c.club_id, c.name
        FROM   League_Teams lt
        JOIN   Clubs c ON lt.club_id = c.club_id
        WHERE  lt.league_id = ?
        ORDER  BY c.club_id
        """,
        (league_id,),
    )
    teams = cursor.fetchall()

    if len(teams) < 2:
        print("  ⚠️  По-малко от 2 отбора — пропускам.")
        return 0, 0, 0

    updated = added = cards_added = 0

    # ── Стъпка 1: Попълни насрочените мачове ────────────────
    cursor.execute(
        """
        SELECT match_id, home_club_id, away_club_id
        FROM   Matches
        WHERE  league_id = ? AND status = 'scheduled'
        ORDER  BY round_no, match_id
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

    # ── Стъпка 2: Добави картони на стари мачове без такива ─
    cards_added = add_cards_to_existing(cursor, league_id)
    if cards_added:
        print(f"  🟨 добавени картони за {cards_added} стари мача")

    # ── Стъпка 3: Добави реванши ако < MIN_MATCHES ──────────
    cursor.execute(
        "SELECT COALESCE(MAX(round_no), 0) FROM Matches WHERE league_id = ?",
        (league_id,),
    )
    max_round = cursor.fetchone()[0]

    needs_more = any(
        count_played(cursor, league_id, club_id) < MIN_MATCHES
        for club_id, _ in teams
    )

    if needs_more:
        print(f"\n  📋 Добавям реванши (нужни са мин. {MIN_MATCHES} мача/отбор)...")
        pairs = [
            (teams[i][0], teams[j][0])
            for i in range(len(teams))
            for j in range(len(teams))
            if i != j
        ]
        round_counter = max_round
        pair_idx = 0

        for home_id, away_id in pairs:
            if (count_played(cursor, league_id, home_id) >= MIN_MATCHES
                    and count_played(cursor, league_id, away_id) >= MIN_MATCHES):
                continue
            if match_exists(cursor, league_id, home_id, away_id):
                continue

            if pair_idx % max(len(teams) // 2, 1) == 0:
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

    # ── Резюме ───────────────────────────────────────────────
    print(f"\n  Резултат: {updated} обновени, {added} добавени, {cards_added} картонирани мача")
    for club_id, name in teams:
        played = count_played(cursor, league_id, club_id)
        status = "✅" if played >= MIN_MATCHES else "⚠️ "
        print(f"    {status}  {name}: {played} изиграни мача")

    return updated, added, cards_added


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

    cursor.execute("SELECT league_id, name, season FROM Leagues ORDER BY league_id")
    leagues = cursor.fetchall()

    if not leagues:
        print("❌ Няма лиги в базата данни.")
        conn.close()
        return

    print(f"🔍 Намерени {len(leagues)} лига/и в БД\n")

    total_upd = total_add = total_cards = 0
    for league_id, name, season in leagues:
        upd, add, cards = process_league(cursor, league_id, name, season)
        total_upd   += upd
        total_add   += add
        total_cards += cards

    conn.commit()
    conn.close()

    print(f"""
══════════════════════════════════════════
✅  ГОТОВО!
   Обновени мачове  : {total_upd}
   Добавени мачове  : {total_add}
   Мача с картони   : {total_cards}
══════════════════════════════════════════
""")


if __name__ == "__main__":
    main()
