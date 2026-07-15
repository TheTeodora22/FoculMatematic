"""
Generează întrebări pentru lecția „Scrierea și citirea numerelor naturale”.
Rulează: python data/quizzes/generators/gen_scrierea_naturale.py
"""

import json
from pathlib import Path


def q(text, correct, wrong, points=10):
    opts = [{"text": correct, "is_correct": True}]
    opts += [{"text": w, "is_correct": False} for w in wrong]
    return {"text": text, "points": points, "options": opts}


def digits_for_pages(pages: int) -> int:
    if pages < 1:
        return 0
    if pages <= 9:
        return pages
    if pages <= 99:
        return 9 + (pages - 9) * 2
    return 9 + 90 * 2 + (pages - 99) * 3


def pages_from_digits(total: int) -> int:
    if total <= 9:
        return total
    if total <= 189:
        return 9 + (total - 9) // 2
    return 99 + (total - 189) // 3


def count_ab_solutions(target: int, coeff_b=2) -> list[int]:
    """Numere ab (2 cifre) cu a + coeff_b*b = target, a>=1."""
    results = []
    for b in range(10):
        a = target - coeff_b * b
        if 1 <= a <= 9:
            results.append(10 * a + b)
    return results


def build_questions():
    questions = []

    # --- Forma desfășurată / cifre (din ex. 1) ---
    expanded = [
        (456, 4, 5, 6),
        (789, 7, 8, 9),
        (305, 3, 0, 5),
        (620, 6, 2, 0),
        (518, 5, 1, 8),
    ]
    for num, a, b, c in expanded:
        questions.append(
            q(
                f"Determinați cifrele a, b și c, știind că {num} = a·100 + b·10 + c.",
                f"a = {a}, b = {b}, c = {c}",
                [
                    f"a = {a+1}, b = {b}, c = {c}",
                    f"a = {a}, b = {b+1}, c = {c}",
                    f"a = {c}, b = {b}, c = {a}",
                ],
            )
        )

    # --- Numerotare pagini: câte cifre (ex. 2a) ---
    for pages in [35, 50, 80, 99, 120]:
        d = digits_for_pages(pages)
        questions.append(
            q(
                f"Câte cifre s-au folosit pentru numerotarea unei cărți cu {pages} de pagini?",
                str(d),
                [str(d - 10), str(d + 1), str(d + 11)],
            )
        )

    # --- Numerotare pagini: câte pagini (ex. 2b) ---
    for digits, pages in [(151, 80), (189, 99), (192, 100), (468, 192)]:
        questions.append(
            q(
                f"Pentru numerotarea paginilor unui manual s-au folosit {digits} de cifre. Câte pagini are manualul?",
                str(pages),
                [str(pages - 5), str(pages + 3), str(pages + 10)],
            )
        )

    # --- a + 2b = n, forma ab (ex. 3) ---
    for target in [9, 11, 13, 15]:
        sols = count_ab_solutions(target, 2)
        count = len(sols)
        questions.append(
            q(
                f"Câte numere naturale de forma ab verifică relația a + 2b = {target}?",
                str(count),
                [str(max(0, count - 1)), str(count + 1), str(count + 2)],
            )
        )
        if sols:
            pick = sols[len(sols) // 2]
            wrong = [s for s in sols if s != pick]
            w = [
                str(wrong[0]) if wrong else str(pick + 11),
                str(pick + 10),
                str(pick - 10 if pick > 10 else pick + 20),
            ]
            questions.append(
                q(
                    f"Care dintre numerele următoare are forma ab și verifică a + 2b = {target}?",
                    str(pick),
                    w[:3],
                )
            )

    # --- Scriere cu cifre (MC, din test) ---
    word_to_digit = [
        ("treizeci și opt de mii nouă", "38 009", ["389", "3 809", "380 009"]),
        ("cinci mii opt", "5 008", ["58", "508", "50 008"]),
        ("două sute treizeci și patru", "234", ["2 034", "23 400", "2 340"]),
        ("un milion două sute", "1 200 000", ["1 200", "120 000", "12 000"]),
        ("nouă sute cinci", "905", ["9 500", "95", "9 050"]),
    ]
    for words, correct, wrong in word_to_digit:
        questions.append(
            q(f"Scrierea cu cifre a numărului „{words}” este:", correct, wrong)
        )

    # --- Scriere cu litere (MC) ---
    digit_to_word = [
        ("1 078", "o mie șaptezeci și opt", [
            "o sută șaptezeci și opt",
            "zece mii șaptezeci și opt",
            "un milion șaptezeci și opt",
        ]),
        ("2 405", "două mii patru sute cinci", [
            "două sute patru mii cinci",
            "douăzeci și patru mii cinci",
            "două mii patruzeci și cinci",
        ]),
        ("50 003", "cincizeci de mii trei", [
            "cinci mii trei",
            "cinci sute trei",
            "cinci milioane trei",
        ]),
        ("100 010", "o sută de mii zece", [
            "o mie zece",
            "un milion zece",
            "zece mii zece",
        ]),
    ]
    for num, correct, wrong in digit_to_word:
        questions.append(
            q(f"Scrierea cu litere a numărului {num} este:", correct, wrong)
        )

    # --- Ordin și clasă ---
    place_value = [
        (
            "1 234 567",
            "3",
            "zecilor de mii",
            "miilor",
            ["unităților", "sutelor", "milioanelor"],
        ),
        (
            "23 456 981",
            "9",
            "sutelor",
            "unităților",
            ["zecilor", "miilor", "milioanelor"],
        ),
        (
            "50 423 678",
            "0",
            "unităților de milioane",
            "milioanelor",
            ["zecilor de milioane", "miilor", "sutelor de mii"],
        ),
        (
            "54 678",
            "4",
            "miilor",
            "miilor",
            ["zecilor de mii", "sutelor", "unităților"],
        ),
    ]
    for number, digit, order, cls, wrong_orders in place_value:
        questions.append(
            q(
                f"În numărul {number}, cifra {digit} este la ordinul:",
                order,
                wrong_orders,
            )
        )
        questions.append(
            q(
                f"În numărul {number}, cifra {digit} aparține clasei:",
                cls,
                ["unităților", "milioanelor", "zecilor"],
            )
        )

    # --- Numere în interval cu cifra dată ---
    def count_digit_in_range(low, high, digit):
        return sum(1 for n in range(low, high + 1) if str(digit) in str(n))

    for low, high, digit in [(30, 60, 4), (100, 150, 5), (20, 40, 2)]:
        cnt = count_digit_in_range(low, high, digit)
        questions.append(
            q(
                f"Câte numere naturale între {low} și {high} conțin cifra {digit}?",
                str(cnt),
                [str(cnt - 2), str(cnt + 1), str(cnt + 3)],
            )
        )

    # --- Răsturnatul (ex. 13) ---
    reverse_cases = [
        ("73a", "437", 4, ["5", "3", "7"]),
        ("95a", "459", 4, ["5", "9", "6"]),
        ("13a", "831", 8, ["1", "3", "6"]),
    ]
    for form, reversed_num, a_val, wrong in reverse_cases:
        questions.append(
            q(
                f"Răsturnatul numărului {form} este {reversed_num}. Care este valoarea cifrei a?",
                str(a_val),
                wrong,
            )
        )

    # --- Șablon a14b: impare / a > b ---
    # a14b impar: b impar, a 1-9 → 9*5 = 45
    questions.append(
        q(
            "Câte numere naturale de forma a14b (a și b cifre, a ≠ 0) sunt impare?",
            "45",
            ["40", "50", "36"],
        )
    )
    # a > b: a 1-9, b 0-9, a>b → sum for each a
    a_gt_b = sum(1 for a in range(1, 10) for b in range(10) if a > b)
    questions.append(
        q(
            "Câte numere naturale de forma a14b verifică relația a > b?",
            str(a_gt_b),
            [str(a_gt_b - 5), str(a_gt_b + 5), "90"],
        )
    )

    # --- Secvențe ---
    sequences = [
        ([10, 16, 22], "+6", "28", ["26", "30", "34"]),
        ([2, 6, 18], "×3", "54", ["36", "48", "72"]),
        ([5, 11, 23], "+6 apoi ×2-1", "47", ["45", "49", "51"]),
    ]
    for seq, rule, correct, wrong in sequences:
        questions.append(
            q(
                f"Care este următorul termen al șirului: {', '.join(map(str, seq))}, ...?",
                correct,
                wrong,
            )
        )

    assert len(questions) >= 30, f"Doar {len(questions)} întrebări generate"
    return questions


def main():
    out = Path(__file__).resolve().parent.parent / "clasa_5_operatii_scrierea_si_citirea_numerelor_naturale.json"
    questions = build_questions()
    payload = {
        "title": "Scrierea și citirea numerelor naturale",
        "description": "Clasa a 5-a · Operații cu numere naturale",
        "difficulty": "easy",
        "questions": questions,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    answers = out.with_suffix(".answers.txt")
    lines = [f"Quiz: {payload['title']} ({len(questions)} întrebări)\n"]
    for i, question in enumerate(questions, 1):
        correct = next(o["text"] for o in question["options"] if o["is_correct"])
        lines.append(f"{i}. {question['text']}")
        lines.append(f"   → {correct}\n")
    answers.write_text("\n".join(lines), encoding="utf-8")

    print(f"Scrie {len(questions)} intrebari in {out.name}")
    print(f"Raspunsuri: {answers.name}")


if __name__ == "__main__":
    main()
