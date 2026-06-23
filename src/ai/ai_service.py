# src/ai/ai_service.py
#
# Rule-based модел за прогноза на мач (Вариант A).
#
# Алгоритъм:
#   1. Изчисли "сила" за всеки отбор от 4 показателя:
#        – Форма (последни 5 мача)          тежест 40%
#        – Атакуваща сила (средно вкарани)   тежест 25%
#        – Защитна сила  (средно допуснати)  тежест 25%
#        – Позиция в класирането             тежест 10%
#   2. Добави домакинско предимство (+8%) към домакина.
#   3. Изчисли вероятност за равен (по-балансирани отбори → по-вероятен равен).
#   4. Раздели останалото пропорционално между победите.
#   5. Закръгли до цели проценти, сумата = 100%.

from ai.features import (
    get_club_id_by_name,
    get_league_for_teams,
    extract_features,
)

# ──────────────────────────────────────────────────
# КОНСТАНТИ
# ──────────────────────────────────────────────────

HOME_BONUS = 0.08    # Домакинско предимство (8%)
MAX_GOALS  = 3.0     # Нормализационен таван за голове

_EMOJI = {"W": "🟩", "D": "🟨", "L": "🟥"}


# ──────────────────────────────────────────────────
# ВЪТРЕШНИ ПОМОЩНИ ФУНКЦИИ
# ──────────────────────────────────────────────────

def _strength(form: float, avg_gf: float, avg_ga: float,
              pos_score: float, bonus: float = 0.0) -> float:
    """
    Композитен индекс на сила за един отбор.
    Всички компоненти са нормализирани в [0, 1].
    """
    attack  = min(avg_gf / MAX_GOALS, 1.0)
    defence = max(0.0, 1.0 - avg_ga / MAX_GOALS)
    score = (
        form      * 0.40
        + attack  * 0.25
        + defence * 0.25
        + pos_score * 0.10
        + bonus
    )
    return max(0.01, score)   # предотвратяване на делене на нула


def _calc_probs(str_h: float, str_a: float) -> tuple:
    """
    Изчислява (home%, draw%, away%) като цели числа суммирани до 100.

    Логика:
      – По-балансирани сили → по-вероятен равен.
      – draw = max(10%, 32% - strength_diff * 80%)
      – Останалото се разделя пропорционално.
    """
    diff = abs(str_h - str_a)
    draw = max(0.10, 0.32 - diff * 0.80)

    remaining = 1.0 - draw
    total     = str_h + str_a
    home      = (str_h / total) * remaining
    away      = (str_a / total) * remaining

    h = round(home * 100)
    d = round(draw * 100)
    a = round(away * 100)

    # Корекция при закръгляне (сумата може да е 99 или 101)
    delta = 100 - (h + d + a)
    if delta:
        # Добавяме разликата към най-голямата стойност
        if h >= d and h >= a:
            h += delta
        elif d >= h and d >= a:
            d += delta
        else:
            a += delta

    return h, d, a


def _bar(pct: int, width: int = 20) -> str:
    """ASCII лента за визуализация на процент."""
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def _form_str(seq: list) -> str:
    """Преобразува W/D/L поредица в emoji низ."""
    return " ".join(_EMOJI.get(r, "?") for r in seq)


# ──────────────────────────────────────────────────
# MATPLOTLIB ГРАФИКА (БОНУС – за "Отличен")
# ──────────────────────────────────────────────────

def show_probability_chart(home_name: str, away_name: str,
                           h_pct: int, d_pct: int, a_pct: int) -> bool:
    """
    Показва bar chart на вероятностите.
    Връща True ако matplotlib е наличен, иначе False.
    """
    try:
        import matplotlib.pyplot as plt

        labels = [f"Победа\n{home_name}", "Равен", f"Победа\n{away_name}"]
        values = [h_pct, d_pct, a_pct]
        colors = ["#1565C0", "#757575", "#B71C1C"]

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(labels, values, color=colors,
                      edgecolor="white", linewidth=1.5, width=0.5)

        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1.2,
                f"{val}%",
                ha="center", va="bottom",
                fontsize=15, fontweight="bold", color="black",
            )

        ax.set_ylim(0, max(values) + 15)
        ax.set_ylabel("Вероятност (%)", fontsize=12)
        ax.set_title(
            f"⚽  AI Прогноза: {home_name}  🆚  {away_name}",
            fontsize=13, fontweight="bold", pad=15,
        )
        ax.set_yticks(range(0, 101, 10))
        ax.yaxis.grid(True, alpha=0.3, linestyle="--")
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.tight_layout()
        plt.show()
        return True

    except ImportError:
        return False
    except Exception:
        return False


# ──────────────────────────────────────────────────
# ПУБЛИЧЕН ИНТЕРФЕЙС
# ──────────────────────────────────────────────────

def predict(home_name: str, away_name: str, show_chart: bool = False) -> str:
    """
    Главна функция — прогнозира резултат на мач.

    Параметри:
        home_name  – частично или пълно име на домакина
        away_name  – частично или пълно име на госта
        show_chart – показва matplotlib графика (ако е инсталиран)

    Връща форматиран низ с:
        – 3 вероятности (домакин / равен / гост)
        – форма (последни 5 мача)
        – голова статистика
        – позиция в класирането
    """

    # ── 1. Намери отборите ───────────────────────────────────
    try:
        home_id, home_full = get_club_id_by_name(home_name)
        away_id, away_full = get_club_id_by_name(away_name)
    except ValueError as e:
        return str(e)

    if not home_id:
        return f"❌ Отбор '{home_name}' не е намерен в базата данни."
    if not away_id:
        return f"❌ Отбор '{away_name}' не е намерен в базата данни."
    if home_id == away_id:
        return "❌ Домакинът и гостът не могат да са един и същ отбор."

    # ── 2. Намери обща лига ──────────────────────────────────
    league_id = get_league_for_teams(home_id, away_id)
    if not league_id:
        return (
            f"❌ {home_full} и {away_full} не участват в обща лига.\n"
            f"   Прогнозата е достъпна само за отбори от една и съща лига."
        )

    # ── 3. Извлечи характеристики ────────────────────────────
    try:
        f = extract_features(home_id, away_id, league_id)
    except ValueError as e:
        return str(e)

    # ── 4. Изчисли сили ──────────────────────────────────────
    str_h = _strength(f["form_h"], f["gf_h"], f["ga_h"], f["pos_score_h"], HOME_BONUS)
    str_a = _strength(f["form_a"], f["gf_a"], f["ga_a"], f["pos_score_a"])

    # ── 5. Изчисли вероятности ───────────────────────────────
    h_pct, d_pct, a_pct = _calc_probs(str_h, str_a)

    # ── 6. (По избор) Matplotlib графика ─────────────────────
    chart_note = ""
    if show_chart:
        ok = show_probability_chart(home_full, away_full, h_pct, d_pct, a_pct)
        if not ok:
            chart_note = "\n   ⚠️  matplotlib не е инсталиран. Инсталирай с: pip install matplotlib"

    # ── 7. Форматирай и върни ─────────────────────────────────
    SEP = "─" * 48
    return (
        f"\n🤖 AI ПРОГНОЗА\n"
        f"{SEP}\n"
        f"  {home_full}  🆚  {away_full}\n"
        f"{SEP}\n"
        f"🏠 Победа {home_full}:\n"
        f"   {h_pct}%  {_bar(h_pct)}\n"
        f"\n"
        f"🤝 Равен:\n"
        f"   {d_pct}%  {_bar(d_pct)}\n"
        f"\n"
        f"✈️  Победа {away_full}:\n"
        f"   {a_pct}%  {_bar(a_pct)}\n"
        f"{SEP}\n"
        f"📊 Форма (последни 5 мача, от нов към стар):\n"
        f"   {home_full}: {_form_str(f['seq_h'])}\n"
        f"   {away_full}: {_form_str(f['seq_a'])}\n"
        f"\n"
        f"⚽ Средно голове на мач:\n"
        f"   {home_full}: {f['gf_h']:.1f} вкарани  /  {f['ga_h']:.1f} допуснати\n"
        f"   {away_full}: {f['gf_a']:.1f} вкарани  /  {f['ga_a']:.1f} допуснати\n"
        f"\n"
        f"🏆 Позиция в лигата:\n"
        f"   #{f['pos_h']} {home_full}  |  #{f['pos_a']} {away_full}\n"
        f"{SEP}"
        f"{chart_note}\n"
    )
