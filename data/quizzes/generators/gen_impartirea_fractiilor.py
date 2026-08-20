"""Generează lecția despre împărțirea fracțiilor ordinare."""

import json
from fractions import Fraction
from pathlib import Path


def grid(text, correct, wrong, explanation):
    values = [str(correct), *[str(value) for value in wrong]]
    order = [2, 0, 3, 1]
    return {
        "text": text, "type": "multiple_choice", "format": "grid", "points": 10,
        "explanation": explanation,
        "options": [{"text": values[index], "is_correct": index == 0} for index in order],
    }


def true_false(text, answer, explanation):
    return {
        "text": text, "type": "multiple_choice", "format": "true_false", "points": 10,
        "explanation": explanation,
        "options": [{"text": value, "is_correct": value == answer} for value in ("Adevărat", "Fals")],
    }


def interactive(text, mode, data, explanation):
    return {
        "text": text, "type": "fraction_division", "format": "interactive", "points": 10,
        "explanation": explanation, "interactive": {"mode": mode, **data},
    }


def reciprocal(value, label=None):
    label = label or f"{value[0]}/{value[1]}"
    return interactive(
        f"Scrie inversa numărului {label}.",
        "reciprocal",
        {"left": [1, 1], "right": list(value), "answers": {"inverse_numerator": value[1], "inverse_denominator": value[0]}},
        f"Schimbăm numărătorul cu numitorul și obținem {value[1]}/{value[0]}.",
    )


def build(left, right):
    result = Fraction(*left) / Fraction(*right)
    return interactive(
        f"Calculează {left[0]}/{left[1]} : {right[0]}/{right[1]}.",
        "build",
        {
            "left": list(left), "right": list(right),
            "answers": {
                "inverse_numerator": right[1], "inverse_denominator": right[0],
                "result_numerator": result.numerator, "result_denominator": result.denominator,
            },
        },
        f"Înmulțim {left[0]}/{left[1]} cu inversa {right[1]}/{right[0]} și obținem {result.numerator}/{result.denominator}.",
    )


def cross_cancel(left, right, cancellations):
    multiplier = (right[1], right[0])
    result = Fraction(*left) / Fraction(*right)
    answers = {"result_numerator": result.numerator, "result_denominator": result.denominator}
    items = []
    for index, (first, second, factor) in enumerate(cancellations):
        items.append({"first": first, "second": second, "factor": factor, "first_result": first // factor, "second_result": second // factor})
        answers.update({f"{index}:factor": factor, f"{index}:first_result": first // factor, f"{index}:second_result": second // factor})
    return interactive(
        f"Inversează a doua fracție, simplifică și calculează {left[0]}/{left[1]} : {right[0]}/{right[1]}.",
        "cross_cancel",
        {"left": list(left), "right": list(right), "multiplier": list(multiplier), "cancellations": items, "answers": answers},
        f"După inversare și simplificare obținem {result.numerator}/{result.denominator}.",
    )


def visual(left, right, piece_count, filled_pieces, candidates, groups):
    return interactive(
        f"Folosește bara pentru a calcula {left[0]}/{left[1]} : {right[0]}/{right[1]}.",
        "visual",
        {
            "left": list(left), "right": list(right),
            "dividend_label": f"{left[0]}/{left[1]}", "divisor_label": f"{right[0]}/{right[1]}",
            "piece_count": piece_count, "filled_pieces": filled_pieces,
            "candidates": candidates, "answers": {"groups": groups},
        },
        f"În partea colorată încap {groups} grupuri complete de mărimea {right[0]}/{right[1]}.",
    )


def missing(left, right, result, missing_side="right", editable="fraction", mode="missing"):
    value = right if missing_side == "right" else left
    if editable == "numerator":
        blank, answers = f"□/{value[1]}", {"missing_numerator": value[0]}
    elif editable == "denominator":
        blank, answers = f"{value[0]}/□", {"missing_denominator": value[1]}
    else:
        blank, answers = "□/□", {"missing_numerator": value[0], "missing_denominator": value[1]}
    left_label = blank if missing_side == "left" else f"{left[0]}/{left[1]}"
    right_label = blank if missing_side == "right" else f"{right[0]}/{right[1]}"
    return interactive(
        f"Completează egalitatea {left_label} : {right_label} = {result[0]}/{result[1]}.",
        mode,
        {
            "left": list(left), "right": list(right), "result": list(result), "missing": list(value),
            "missing_side": missing_side, "editable": editable, "answers": answers,
        },
        f"Fracția lipsă este {value[0]}/{value[1]}.",
    )


def cancel_select(left, right, candidates, correct):
    multiplier = (right[1], right[0])
    return interactive(
        f"După inversare, alege simplificările permise pentru {left[0]}/{left[1]} : {right[0]}/{right[1]}.",
        "cancel_select",
        {
            "left": list(left), "right": list(right), "multiplier": list(multiplier),
            "candidates": [{"id": item_id, "label": label} for item_id, label in candidates],
            "answers": {"selected": ",".join(sorted(correct))},
        },
        "După inversare, simplificăm numai un numărător cu un numitor.",
    )


def error_case(text, left, right, steps, error_index, explanation):
    return interactive(text, "error", {"left": list(left), "right": list(right), "steps": steps, "answers": {"error_index": error_index}}, explanation)


def order_steps(text, left, right, steps, display_order, explanation):
    return interactive(
        text, "order_steps",
        {"left": list(left), "right": list(right), "steps": steps, "display_order": display_order, "answers": {"order": ",".join(str(index) for index in range(len(steps)))}},
        explanation,
    )


def match_results(text, pairs):
    return interactive(
        text, "match",
        {
            "left": [1, 2], "right": [1, 3],
            "pairs": [{"operation": operation, "result": result} for operation, result in pairs],
            "result_order": [2, 0, 1], "answers": {f"match_{index}": index for index in range(len(pairs))},
        },
        "Înmulțim prima fracție cu inversa celei de-a doua și simplificăm.",
    )


def problem(text, left, right):
    result = Fraction(*left) / Fraction(*right)
    return interactive(
        text, "problem",
        {"left": list(left), "right": list(right), "answers": {"result_numerator": result.numerator, "result_denominator": result.denominator}},
        f"Calculăm {left[0]}/{left[1]} : {right[0]}/{right[1]} = {result.numerator}/{result.denominator}.",
    )


def mixed(left_label, right_label, left, right):
    result = Fraction(*left) / Fraction(*right)
    whole, remainder = divmod(result.numerator, result.denominator)
    return interactive(
        f"Calculează {left_label} : {right_label} și scrie rezultatul ca număr mixt.",
        "mixed",
        {
            "left": list(left), "right": list(right), "left_label": left_label, "right_label": right_label,
            "answers": {"whole": whole, "mixed_numerator": remainder, "mixed_denominator": result.denominator},
        },
        f"Câtul este {result.numerator}/{result.denominator}, adică {whole} {remainder}/{result.denominator}.",
    )


def build_questions():
    questions = [
        grid("Inversa fracției 3/7 este:", "7/3", ["3/7", "4/8", "7/4"], "Schimbăm între ele numărătorul și numitorul."),
        grid("Rezultatul lui 5/6 : 10/21 este:", "7/4", ["50/126", "4/7", "25/63"], "5/6 : 10/21 = 5/6 · 21/10 = 7/4."),
        grid("Calculează 4 : 2/3.", "6", ["8/3", "2/3", "3/2"], "4/1 · 3/2 = 12/2 = 6."),
        grid("Rezultatul lui 2 1/4 : 3/5 este:", "3 3/4", ["1 7/20", "5/12", "2 2/5"], "9/4 · 5/3 = 45/12 = 15/4 = 3 3/4."),
        grid("Din 4 1/2 metri de material se taie bucăți de 3/4 metru. Câte bucăți se obțin?", "6", ["3", "4", "8"], "9/2 : 3/4 = 9/2 · 4/3 = 6."),
        true_false("Pentru a împărți două fracții, înmulțim prima fracție cu inversa celei de-a doua.", "Adevărat", "Aceasta este regula împărțirii fracțiilor."),
        true_false("La o împărțire de fracții trebuie inversată prima fracție.", "Fals", "Se inversează numai a doua fracție, adică împărțitorul."),
        true_false("Produsul dintre o fracție nenulă și inversa ei este 1.", "Adevărat", "a/b · b/a = 1 pentru a și b nenule."),
        reciprocal((3, 7)),
        reciprocal((5, 1), "5"),
        reciprocal((9, 4), "2 1/4"),
        build((3, 4), (2, 5)),
        build((5, 6), (10, 21)),
        build((16, 27), (8, 9)),
        build((7, 12), (14, 15)),
        cross_cancel((5, 6), (10, 21), [(5, 10, 5), (21, 6, 3)]),
        cross_cancel((16, 27), (8, 9), [(16, 8, 8), (9, 27, 9)]),
        cross_cancel((14, 25), (7, 15), [(14, 7, 7), (15, 25, 5)]),
        visual((3, 4), (1, 4), 4, 3, [1, 2, 3, 4, 5], 3),
        visual((5, 6), (1, 6), 6, 5, [3, 4, 5, 6, 7], 5),
        visual((4, 5), (2, 5), 5, 4, [1, 2, 3, 4], 2),
        missing((3, 5), (3, 4), (4, 5), editable="fraction"),
        missing((4, 7), (2, 3), (6, 7), editable="denominator"),
        missing((3, 4), (5, 6), (9, 10), missing_side="left", editable="fraction"),
        cancel_select((5, 6), (10, 21), [("a", "5 cu 10"), ("b", "21 cu 6"), ("c", "5 cu 6"), ("d", "21 cu 10")], ["a", "b"]),
        cancel_select((16, 27), (8, 9), [("a", "16 cu 8"), ("b", "9 cu 27"), ("c", "16 cu 27"), ("d", "9 cu 8")], ["a", "b"]),
        error_case("Identifică primul pas greșit în calculul 3/4 : 2/5.", (3, 4), (2, 5), ["Păstrăm fracția 3/4.", "Inversăm 3/4 și obținem 4/3.", "Înmulțim fracțiile obținute."], 1, "Trebuie inversată a doua fracție: inversa lui 2/5 este 5/2."),
        error_case("Apasă prima transformare greșită pentru 1 1/2 : 3/4.", (3, 2), (3, 4), ["1 1/2 = 2/2.", "Inversa lui 3/4 este 4/3.", "Înmulțim prima fracție cu 4/3."], 0, "1 1/2 se transformă în 3/2, nu în 2/2."),
        error_case("Alege primul pas incorect în calculul 8/15 : 4/9.", (8, 15), (4, 9), ["Inversa lui 4/9 este 9/4.", "Scriem 8/15 · 9/4.", "Simplificăm 8 cu 4 și obținem 4 și 1.", "Simplificăm 9 cu 15 prin 3."], 2, "8 și 4 simplificate prin 4 devin 2 și 1."),
        order_steps("Așază pașii calculului 5/6 : 10/21.", (5, 6), (10, 21), ["Inversăm 10/21 și obținem 21/10.", "Scriem 5/6 · 21/10.", "Simplificăm 5 cu 10 și 21 cu 6.", "Înmulțim 1/2 · 7/2 = 7/4."], [2, 0, 3, 1], "Inversăm împărțitorul înainte de simplificare și înmulțire."),
        order_steps("Construiește rezolvarea lui 2 1/4 : 3/5.", (9, 4), (3, 5), ["Transformăm 2 1/4 în 9/4.", "Inversăm 3/5 și obținem 5/3.", "Calculăm 9/4 · 5/3 = 15/4.", "Scriem 15/4 = 3 3/4."], [3, 1, 0, 2], "Introducem întregii, inversăm a doua fracție, calculăm și scoatem întregii."),
        order_steps("Ordonează pașii calculului 6 : 9/10.", (6, 1), (9, 10), ["Scriem 6 ca 6/1.", "Inversăm 9/10 și obținem 10/9.", "Simplificăm 6 cu 9 prin 3.", "Calculăm 2/1 · 10/3 = 20/3."], [1, 3, 0, 2], "Numărul natural se scrie cu numitorul 1, apoi aplicăm regula împărțirii."),
        match_results("Potrivește fiecare împărțire cu rezultatul ei.", [("3/4 : 2/5", "15/8"), ("5/6 : 10/9", "3/4"), ("7/8 : 7/12", "3/2")]),
        match_results("Leagă fiecare calcul de valoarea corectă.", [("4 : 2/3", "6"), ("3/5 : 9/10", "2/3"), ("11/12 : 11/18", "3/2")]),
        match_results("Alege câtul potrivit pentru fiecare calcul.", [("1 1/2 : 3/4", "2"), ("2 1/4 : 3/5", "15/4"), ("3 1/3 : 5/6", "4")]),
        problem("Din 4 1/2 metri de material se taie bucăți de câte 3/4 metru. Câte bucăți se pot obține?", (9, 2), (3, 4)),
        problem("Într-un sac sunt 8 2/3 kg de cafea. Câte pungi de câte 2/3 kg se pot umple?", (26, 3), (2, 3)),
        problem("Un cablu de 2 3/10 metri este tăiat în bucăți de câte 3/5 metru. Câte asemenea lungimi conține cablul?", (23, 10), (3, 5)),
        mixed("4 1/2", "2/3", (9, 2), (2, 3)),
        mixed("8 1/5", "3/10", (41, 5), (3, 10)),
        mixed("2 1/6", "1 3/4", (13, 6), (7, 4)),
        missing((2, 3), (4, 9), (3, 2), missing_side="left", editable="fraction", mode="inverse"),
        missing((5, 6), (3, 5), (25, 18), editable="fraction", mode="inverse"),
        missing((3, 4), (7, 8), (6, 7), missing_side="left", editable="fraction", mode="inverse"),
    ]
    assert len(questions) == 44
    return questions


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_fractii_ordinare_impartirea.json"
    payload = {
        "title": "Împărțirea fracțiilor ordinare",
        "description": "Clasa a 5-a · Fracții ordinare",
        "difficulty": "easy",
        "questions": build_questions(),
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} intrebari in {target}.")


if __name__ == "__main__":
    main()
