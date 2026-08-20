"""Generează lecția despre înmulțirea fracțiilor ordinare."""

import json
from fractions import Fraction
from pathlib import Path


def grid(text, correct, wrong, explanation):
    values = [str(correct), *[str(value) for value in wrong]]
    order = [2, 0, 3, 1]
    return {
        "text": text,
        "type": "multiple_choice",
        "format": "grid",
        "points": 10,
        "explanation": explanation,
        "options": [{"text": values[index], "is_correct": index == 0} for index in order],
    }


def true_false(text, answer, explanation):
    return {
        "text": text,
        "type": "multiple_choice",
        "format": "true_false",
        "points": 10,
        "explanation": explanation,
        "options": [{"text": value, "is_correct": value == answer} for value in ("Adevărat", "Fals")],
    }


def interactive(text, mode, data, explanation):
    return {
        "text": text,
        "type": "fraction_product",
        "format": "interactive",
        "points": 10,
        "explanation": explanation,
        "interactive": {"mode": mode, **data},
    }


def build(left, right):
    raw_numerator = left[0] * right[0]
    raw_denominator = left[1] * right[1]
    result = Fraction(raw_numerator, raw_denominator)
    return interactive(
        f"Calculează {left[0]}/{left[1]} · {right[0]}/{right[1]} și simplifică.",
        "build",
        {
            "left": list(left), "right": list(right),
            "answers": {
                "raw_numerator": raw_numerator,
                "raw_denominator": raw_denominator,
                "result_numerator": result.numerator,
                "result_denominator": result.denominator,
            },
        },
        f"Produsul este {raw_numerator}/{raw_denominator}, care se simplifică la {result.numerator}/{result.denominator}.",
    )


def cross_cancel(left, right, cancellations):
    result = Fraction(*left) * Fraction(*right)
    answers = {"result_numerator": result.numerator, "result_denominator": result.denominator}
    items = []
    for index, (first, second, factor) in enumerate(cancellations):
        items.append({
            "first": first, "second": second, "factor": factor,
            "first_result": first // factor, "second_result": second // factor,
        })
        answers.update({
            f"{index}:factor": factor,
            f"{index}:first_result": first // factor,
            f"{index}:second_result": second // factor,
        })
    return interactive(
        f"Simplifică în cruce și calculează {left[0]}/{left[1]} · {right[0]}/{right[1]}.",
        "cross_cancel",
        {"left": list(left), "right": list(right), "cancellations": items, "answers": answers},
        f"După simplificările în cruce, produsul ireductibil este {result.numerator}/{result.denominator}.",
    )


def visual(left, right):
    columns, rows = left[1], right[1]
    selected = [row * columns + column for row in range(right[0]) for column in range(left[0])]
    result = Fraction(*left) * Fraction(*right)
    return interactive(
        f"Reprezintă pe grilă produsul {left[0]}/{left[1]} · {right[0]}/{right[1]}.",
        "visual",
        {
            "left": list(left), "right": list(right),
            "columns": columns, "rows": rows,
            "first_columns": left[0], "second_rows": right[0],
            "answers": {"selected": ",".join(map(str, selected))},
        },
        f"Suprapunerea conține {len(selected)} din {rows * columns} căsuțe, adică {result.numerator}/{result.denominator}.",
    )


def missing(left, right, result, missing_side="right", editable="fraction", mode="missing"):
    value = right if missing_side == "right" else left
    if editable == "numerator":
        blank = f"□/{value[1]}"
        answers = {"missing_numerator": value[0]}
    elif editable == "denominator":
        blank = f"{value[0]}/□"
        answers = {"missing_denominator": value[1]}
    else:
        blank = "□/□"
        answers = {"missing_numerator": value[0], "missing_denominator": value[1]}
    left_label = blank if missing_side == "left" else f"{left[0]}/{left[1]}"
    right_label = blank if missing_side == "right" else f"{right[0]}/{right[1]}"
    return interactive(
        f"Completează egalitatea {left_label} · {right_label} = {result[0]}/{result[1]}.",
        mode,
        {
            "left": list(left), "right": list(right), "result": list(result),
            "missing": list(value), "missing_side": missing_side, "editable": editable,
            "answers": answers,
        },
        f"Factorul lipsă este {value[0]}/{value[1]}.",
    )


def cancel_select(left, right, candidates, correct):
    return interactive(
        f"Alege simplificările în cruce permise pentru {left[0]}/{left[1]} · {right[0]}/{right[1]}.",
        "cancel_select",
        {
            "left": list(left), "right": list(right),
            "candidates": [{"id": item_id, "label": label} for item_id, label in candidates],
            "answers": {"selected": ",".join(sorted(correct))},
        },
        "Se pot simplifica numai un numărător cu un numitor, folosind un divizor comun mai mare decât 1.",
    )


def error_case(text, left, right, steps, error_index, explanation):
    return interactive(
        text,
        "error",
        {"left": list(left), "right": list(right), "steps": steps, "answers": {"error_index": error_index}},
        explanation,
    )


def order_steps(text, left, right, steps, display_order, explanation):
    return interactive(
        text,
        "order_steps",
        {
            "left": list(left), "right": list(right), "steps": steps,
            "display_order": display_order,
            "answers": {"order": ",".join(str(index) for index in range(len(steps)))},
        },
        explanation,
    )


def match_results(text, pairs):
    return interactive(
        text,
        "match",
        {
            "left": [1, 2], "right": [1, 3],
            "pairs": [{"operation": operation, "result": result} for operation, result in pairs],
            "result_order": [2, 0, 1],
            "answers": {f"match_{index}": index for index in range(len(pairs))},
        },
        "Înmulțim numărătorii și numitorii, apoi simplificăm fiecare produs.",
    )


def problem(text, left, right):
    result = Fraction(*left) * Fraction(*right)
    return interactive(
        text,
        "problem",
        {
            "left": list(left), "right": list(right),
            "answers": {"result_numerator": result.numerator, "result_denominator": result.denominator},
        },
        f"Calculăm {left[0]}/{left[1]} · {right[0]}/{right[1]} = {result.numerator}/{result.denominator}.",
    )


def mixed(left_label, right_label, left, right):
    result = Fraction(*left) * Fraction(*right)
    whole, remainder = divmod(result.numerator, result.denominator)
    return interactive(
        f"Calculează {left_label} · {right_label} și scrie rezultatul ca număr mixt.",
        "mixed",
        {
            "left": list(left), "right": list(right),
            "left_label": left_label, "right_label": right_label,
            "answers": {"whole": whole, "mixed_numerator": remainder, "mixed_denominator": result.denominator},
        },
        f"Produsul este {result.numerator}/{result.denominator}, adică {whole} {remainder}/{result.denominator}.",
    )


def build_questions():
    questions = [
        grid("Calculează 3 · 2/7.", "6/7", ["6/21", "5/7", "3/14"], "Scriem 3 ca 3/1 și înmulțim numărătorii."),
        grid("Rezultatul lui 4/9 · 7/10 este:", "14/45", ["28/19", "11/19", "28/90"], "4/9 · 7/10 = 28/90 = 14/45."),
        grid("Calculează și simplifică 5/6 · 9/20.", "3/8", ["45/120", "14/26", "3/4"], "Simplificăm 5 cu 20 și 9 cu 6 înainte de înmulțire."),
        grid("Produsul 2 1/7 · 3/5 este:", "1 2/7", ["6/35", "9/35", "2 4/7"], "2 1/7 = 15/7, iar 15/7 · 3/5 = 9/7 = 1 2/7."),
        grid("Radu mănâncă 2/3 dintr-o bucată care reprezintă 3/8 din plăcintă. Ce fracție din plăcintă mănâncă?", "1/4", ["5/11", "2/8", "6/11"], "Calculăm 2/3 · 3/8 = 6/24 = 1/4."),
        true_false("Produsul a două fracții se obține înmulțind numărătorii între ei și numitorii între ei.", "Adevărat", "Aceasta este regula înmulțirii fracțiilor."),
        true_false("La simplificarea în cruce putem simplifica doi numărători între ei.", "Fals", "Simplificăm un numărător cu un numitor."),
        true_false("Un număr mixt trebuie transformat în fracție înainte de înmulțire.", "Adevărat", "Introducem întregii în fracție, apoi efectuăm produsul."),
        build((3, 1), (2, 7)),
        build((4, 9), (7, 10)),
        build((5, 6), (9, 20)),
        build((11, 12), (6, 55)),
        cross_cancel((4, 15), (25, 14), [(4, 14, 2), (25, 15, 5)]),
        cross_cancel((9, 28), (14, 15), [(9, 15, 3), (14, 28, 14)]),
        cross_cancel((12, 35), (21, 16), [(12, 16, 4), (21, 35, 7)]),
        cross_cancel((18, 49), (21, 30), [(18, 30, 6), (21, 49, 7)]),
        visual((2, 3), (4, 5)),
        visual((3, 4), (2, 3)),
        visual((1, 2), (3, 4)),
        missing((3, 5), (3, 4), (9, 20), editable="fraction"),
        missing((4, 7), (3, 2), (6, 7), editable="denominator"),
        missing((5, 8), (4, 15), (1, 6), editable="numerator"),
        cancel_select((4, 15), (25, 14), [("a", "4 cu 14"), ("b", "25 cu 15"), ("c", "4 cu 15"), ("d", "25 cu 14")], ["a", "b"]),
        cancel_select((9, 28), (14, 15), [("a", "9 cu 15"), ("b", "14 cu 28"), ("c", "9 cu 28"), ("d", "14 cu 15")], ["a", "b"]),
        cancel_select((12, 35), (21, 16), [("a", "12 cu 16"), ("b", "21 cu 35"), ("c", "12 cu 35"), ("d", "21 cu 16")], ["a", "b"]),
        error_case("Identifică primul pas greșit în calculul 2/3 · 5/7.", (2, 3), (5, 7), ["Înmulțim numărătorii: 2 · 5 = 10.", "Înmulțim numitorii: 3 · 7 = 21.", "Produsul este 21/10."], 2, "Produsul corect este 10/21, nu 21/10."),
        error_case("Apasă prima simplificare greșită din calculul 4/9 · 3/8.", (4, 9), (3, 8), ["Simplificăm 4 cu 8 și obținem 1 și 4.", "Simplificăm 3 cu 9 și obținem 1 și 3.", "Înmulțim 1/3 · 1/4."], 0, "4 și 8 simplificate prin 4 devin 1 și 2."),
        error_case("Alege prima transformare incorectă pentru 1 1/2 · 2/3.", (3, 2), (2, 3), ["1 1/2 = 2/2.", "Înmulțim fracțiile obținute.", "Simplificăm produsul."], 0, "1 1/2 = 3/2, deoarece 1 · 2 + 1 = 3."),
        order_steps("Așază pașii pentru calculul 3/5 · 10/21.", (3, 5), (10, 21), ["Simplificăm 3 cu 21 prin 3.", "Simplificăm 10 cu 5 prin 5.", "Înmulțim 1/1 · 2/7.", "Obținem 2/7."], [2, 0, 3, 1], "Simplificăm în cruce, apoi înmulțim valorile rămase."),
        order_steps("Construiește rezolvarea produsului 2 1/4 · 8/15.", (9, 4), (8, 15), ["Transformăm 2 1/4 în 9/4.", "Simplificăm 8 cu 4 și 9 cu 15.", "Înmulțim 3/1 · 2/5 = 6/5.", "Scriem 6/5 = 1 1/5."], [3, 1, 0, 2], "Mai întâi introducem întregii, apoi simplificăm și înmulțim."),
        order_steps("Ordonează pașii calculului 6 · 5/18.", (6, 1), (5, 18), ["Scriem 6 ca fracția 6/1.", "Simplificăm 6 cu 18 prin 6.", "Calculăm 1/1 · 5/3 = 5/3.", "Scoatem întregii: 5/3 = 1 2/3."], [1, 3, 0, 2], "Numărul natural se scrie cu numitorul 1 înainte de calcul."),
        match_results("Potrivește fiecare produs cu rezultatul lui.", [("2/3 · 3/5", "2/5"), ("4/7 · 7/8", "1/2"), ("5/9 · 3/10", "1/6")]),
        match_results("Leagă fiecare înmulțire de valoarea corectă.", [("3 · 2/11", "6/11"), ("7/12 · 6/7", "1/2"), ("5/8 · 4/9", "5/18")]),
        match_results("Alege rezultatul potrivit pentru fiecare produs.", [("2 1/4 · 2/3", "3/2"), ("1 2/5 · 5/7", "1"), ("3 1/3 · 3/8", "5/4")]),
        problem("Fiecare sesiune consumă 2/9 din baterie. Ce fracție din baterie consumă 4 sesiuni?", (4, 1), (2, 9)),
        problem("O tavă este plină în proporție de 2/3, iar Horia folosește 4/5 din cuburile existente. Ce fracție din tavă folosește?", (2, 3), (4, 5)),
        problem("Pentru o perdea sunt necesari 4 3/5 metri de material. Cât material este necesar pentru 4 perdele?", (4, 1), (23, 5)),
        problem("Pentru o porție sunt necesare 1/2 kg de zahăr. Ce cantitate este necesară pentru 3 porții?", (3, 1), (1, 2)),
        mixed("14", "5/21", (14, 1), (5, 21)),
        mixed("4 2/7", "5/11", (30, 7), (5, 11)),
        mixed("3 3/5", "2 1/4", (18, 5), (9, 4)),
        missing((6, 5), (3, 4), (9, 10), missing_side="left", editable="fraction", mode="inverse"),
        missing((5, 7), (3, 4), (15, 28), editable="fraction", mode="inverse"),
        missing((15, 4), (2, 9), (5, 6), missing_side="left", editable="fraction", mode="inverse"),
    ]
    assert len(questions) == 44
    return questions


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_fractii_ordinare_inmultirea.json"
    payload = {
        "title": "Înmulțirea fracțiilor",
        "description": "Clasa a 5-a · Fracții ordinare",
        "difficulty": "easy",
        "questions": build_questions(),
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} intrebari in {target}.")


if __name__ == "__main__":
    main()
