"""
Progresie XP: praguri cumulative. Fiecare nivel începe la un total XP mai mare;
cantitatea necesară pentru următorul nivel crește (trepte diferite).
"""

import bisect
from typing import Any

# XP total minim pentru a fi în nivelul N (N = 1 .. len(LEVEL_START_XP)).
LEVEL_START_XP = [
    0,
    45,
    110,
    210,
    360,
    580,
    890,
    1320,
    1900,
    2680,
    3720,
    5080,
    6850,
    9150,
    12100,
    15900,
    20800,
    27000,
    35000,
]

LEVEL_TITLES = [
    "Începător",
    "Ucenic",
    "Exersant",
    "Rezolvitor",
    "Practician",
    "Riguros",
    "Perspicace",
    "Strateg",
    "Analist",
    "Expert",
    "Maestru al exercițiului",
    "Virtuoz",
    "Elitist",
    "Oracol",
    "Arhitect",
    "Legendă locală",
    "Geniu discret",
    "Foc viu",
    "Focul Matematic",
]


def compute_level_number(total_xp: int) -> int:
    """Returnează numărul nivelului (1-based), derivat din XP total."""
    if total_xp < 0:
        total_xp = 0
    idx = bisect.bisect_right(LEVEL_START_XP, total_xp) - 1
    idx = max(0, min(idx, len(LEVEL_START_XP) - 1))
    return idx + 1


def get_level_progress(total_xp: int) -> dict[str, Any]:
    """
    Date pentru UI: bară progres, titluri, XP în segmentul curent vs necesar pentru nivelul următor.
    """
    if total_xp < 0:
        total_xp = 0

    level_idx = bisect.bisect_right(LEVEL_START_XP, total_xp) - 1
    level_idx = max(0, min(level_idx, len(LEVEL_START_XP) - 1))
    level_num = level_idx + 1

    xp_floor = LEVEL_START_XP[level_idx]
    is_max = level_idx >= len(LEVEL_START_XP) - 1

    if is_max:
        xp_ceiling = None
        xp_in_segment = total_xp - xp_floor
        segment_size = None
        pct = 100
        xp_to_next = 0
    else:
        xp_ceiling = LEVEL_START_XP[level_idx + 1]
        segment_size = xp_ceiling - xp_floor
        xp_in_segment = total_xp - xp_floor
        xp_to_next = max(0, xp_ceiling - total_xp)
        pct = int(round(100 * xp_in_segment / segment_size)) if segment_size else 100
        pct = max(0, min(100, pct))

    title = LEVEL_TITLES[level_idx] if level_idx < len(LEVEL_TITLES) else LEVEL_TITLES[-1]
    next_title = (
        None
        if is_max
        else (
            LEVEL_TITLES[level_idx + 1]
            if level_idx + 1 < len(LEVEL_TITLES)
            else f"Nivel {level_num + 1}"
        )
    )

    return {
        "level": level_num,
        "level_title": title,
        "next_level_title": next_title,
        "xp_total": total_xp,
        "xp_floor": xp_floor,
        "xp_ceiling": xp_ceiling,
        "xp_in_level": xp_in_segment,
        "xp_needed_this_level": (xp_ceiling - xp_floor) if xp_ceiling is not None else None,
        "xp_to_next_level": xp_to_next,
        "progress_pct": pct,
        "is_max_level": is_max,
        "max_level": len(LEVEL_START_XP),
    }
