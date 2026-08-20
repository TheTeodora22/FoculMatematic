"""Generează lecția despre adunarea și scăderea fracțiilor ordinare."""

import json
import math
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
        "options": [
            {"text": values[index], "is_correct": index == 0}
            for index in order
        ],
    }


def true_false(text, answer, explanation):
    return {
        "text": text,
        "type": "multiple_choice",
        "format": "true_false",
        "points": 10,
        "explanation": explanation,
        "options": [
            {"text": value, "is_correct": value == answer}
            for value in ("Adevărat", "Fals")
        ],
    }


def interactive(text, mode, data, explanation):
    return {
        "text": text,
        "type": "common_denominator",
        "format": "interactive",
        "points": 10,
        "explanation": explanation,
        "interactive": {"mode": mode, **data},
    }


def lcm(a, b):
    return a * b // math.gcd(a, b)


def pair(value):
    return [value.numerator, value.denominator]


def common_denominator(left, right):
    denominator = lcm(left[1], right[1])
    left_factor = denominator // left[1]
    right_factor = denominator // right[1]
    return interactive(
        f"Adu fracțiile {left[0]}/{left[1]} și {right[0]}/{right[1]} la cel mai mic numitor comun.",
        "build",
        {
            "left": list(left),
            "right": list(right),
            "answers": {
                "left_factor": left_factor,
                "right_factor": right_factor,
                "left_numerator": left[0] * left_factor,
                "right_numerator": right[0] * right_factor,
                "common_denominator": denominator,
            },
        },
        f"c.m.m.m.c.({left[1]}, {right[1]}) = {denominator}; factorii de amplificare sunt {left_factor} și {right_factor}.",
    )


def calculate(left, right, operation):
    denominator = lcm(left[1], right[1])
    left_numerator = left[0] * (denominator // left[1])
    right_numerator = right[0] * (denominator // right[1])
    result = Fraction(*left) + Fraction(*right) if operation == "+" else Fraction(*left) - Fraction(*right)
    return interactive(
        f"Calculează {left[0]}/{left[1]} {operation} {right[0]}/{right[1]}.",
        "calculate",
        {
            "left": list(left),
            "right": list(right),
            "operation": operation,
            "answers": {
                "left_numerator": left_numerator,
                "right_numerator": right_numerator,
                "common_denominator": denominator,
                "result_numerator": result.numerator,
                "result_denominator": result.denominator,
            },
        },
        f"La numitorul {denominator} obținem {left_numerator}/{denominator} {operation} {right_numerator}/{denominator}, iar rezultatul ireductibil este {result.numerator}/{result.denominator}.",
    )


def missing_term(left, right, operation, result, missing_side="right", mode="missing_term"):
    missing = Fraction(*right) if missing_side == "right" else Fraction(*left)
    left_label = "□" if missing_side == "left" else f"{left[0]}/{left[1]}"
    right_label = "□" if missing_side == "right" else f"{right[0]}/{right[1]}"
    return interactive(
        f"Completează egalitatea {left_label} {operation} {right_label} = {result[0]}/{result[1]}.",
        mode,
        {
            "left": list(left),
            "right": list(right),
            "result": list(result),
            "operation": operation,
            "missing_side": missing_side,
            "answers": {
                "missing_numerator": missing.numerator,
                "missing_denominator": missing.denominator,
            },
        },
        f"Fracția lipsă este {missing.numerator}/{missing.denominator}.",
    )


def choose_operator(left, right, result, operation):
    return interactive(
        f"Completează egalitatea {left[0]}/{left[1]} □ {right[0]}/{right[1]} = {result[0]}/{result[1]}.",
        "operator",
        {
            "left": list(left),
            "right": list(right),
            "result": list(result),
            "operation": operation,
            "answers": {"operator": operation},
        },
        f"Operația corectă este {operation}.",
    )


def error_case(text, left, right, operation, steps, error_index, explanation):
    return interactive(
        text,
        "error",
        {
            "left": list(left),
            "right": list(right),
            "operation": operation,
            "steps": steps,
            "answers": {"error_index": error_index},
        },
        explanation,
    )


def order_steps(text, steps, display_order, explanation):
    return interactive(
        text,
        "order_steps",
        {
            "left": [1, 2],
            "right": [1, 3],
            "steps": steps,
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
            "left": [1, 2],
            "right": [1, 3],
            "pairs": [{"operation": operation, "result": result} for operation, result in pairs],
            "result_order": [2, 0, 1],
            "answers": {f"match_{index}": index for index in range(len(pairs))},
        },
        "Aducem la același numitor, efectuăm operația și simplificăm fiecare rezultat.",
    )


def problem(text, left, right, operation):
    result = Fraction(*left) + Fraction(*right) if operation == "+" else Fraction(*left) - Fraction(*right)
    return interactive(
        text,
        "problem",
        {
            "left": list(left),
            "right": list(right),
            "operation": operation,
            "answers": {
                "operator": operation,
                "result_numerator": result.numerator,
                "result_denominator": result.denominator,
            },
        },
        f"Operația este {left[0]}/{left[1]} {operation} {right[0]}/{right[1]}, iar rezultatul ireductibil este {result.numerator}/{result.denominator}.",
    )


def mixed(left, right, operation):
    result = Fraction(*left) + Fraction(*right) if operation == "+" else Fraction(*left) - Fraction(*right)
    whole, remainder = divmod(result.numerator, result.denominator)
    return interactive(
        f"Calculează {left[0]}/{left[1]} {operation} {right[0]}/{right[1]} și scoate întregii din rezultat.",
        "mixed",
        {
            "left": list(left),
            "right": list(right),
            "operation": operation,
            "answers": {
                "whole": whole,
                "mixed_numerator": remainder,
                "mixed_denominator": result.denominator,
            },
        },
        f"Rezultatul este {result.numerator}/{result.denominator}, adică {whole} {remainder}/{result.denominator}.",
    )


def build_questions():
    questions = [
        grid("Calculează 3/11 + 5/11.", "8/11", ["8/22", "2/11", "15/11"], "Numitorul rămâne 11, iar numărătorii se adună."),
        grid("Calculează 17/18 − 5/18 și simplifică.", "2/3", ["12/18", "12/36", "11/18"], "17/18 − 5/18 = 12/18 = 2/3."),
        grid("Rezultatul lui 1/3 + 2/5 este:", "11/15", ["3/8", "3/15", "7/15"], "1/3 = 5/15 și 2/5 = 6/15."),
        grid("Rezultatul lui 7/8 − 1/6 este:", "17/24", ["6/2", "19/24", "6/14"], "7/8 = 21/24 și 1/6 = 4/24."),
        grid("Dintr-o grădină, 8/17 este plantată cu meri și 4/17 cu peri. Ce fracție rămâne liberă?", "5/17", ["12/17", "4/17", "5/34"], "Partea ocupată este 12/17, deci rămâne 17/17 − 12/17 = 5/17."),
        grid("Care calcul are rezultatul 1?", "3/5 + 2/5", ["3/5 − 2/5", "1/3 + 1/3", "5/6 − 1/3"], "La același numitor, 3/5 + 2/5 = 5/5 = 1."),
        true_false("La adunarea fracțiilor cu același numitor, adunăm numărătorii și păstrăm numitorul.", "Adevărat", "Aceasta este regula pentru fracțiile cu același numitor."),
        true_false("Pentru a calcula 1/3 + 1/4 putem aduna direct și numărătorii, și numitorii.", "Fals", "Mai întâi aducem fracțiile la același numitor."),
        true_false("După efectuarea unei adunări sau scăderi, rezultatul trebuie simplificat dacă este reductibil.", "Adevărat", "Răspunsul final se scrie, de regulă, în formă ireductibilă."),
    ]

    questions += [
        common_denominator((2, 3), (5, 8)),
        common_denominator((7, 10), (3, 4)),
        common_denominator((5, 12), (7, 18)),
        common_denominator((11, 15), (2, 9)),
        common_denominator((3, 14), (5, 21)),
        calculate((5, 12), (7, 18), "+"),
        calculate((11, 15), (2, 9), "-"),
        calculate((3, 8), (5, 6), "+"),
        calculate((13, 14), (5, 21), "-"),
        missing_term((3, 4), (1, 3), "+", (13, 12)),
        missing_term((1, 2), (2, 5), "-", (1, 10), missing_side="left"),
        missing_term((7, 8), (3, 8), "-", (1, 2)),
        missing_term((1, 3), (5, 12), "+", (3, 4), missing_side="left"),
        choose_operator((2, 3), (1, 6), (5, 6), "+"),
        choose_operator((7, 8), (3, 8), (1, 2), "-"),
        choose_operator((5, 12), (1, 4), (1, 6), "-"),
        error_case(
            "Identifică primul pas greșit al rezolvării.",
            (1, 3), (1, 4), "+",
            ["c.m.m.m.c.(3, 4) = 12", "1/3 = 4/12", "1/4 = 3/12", "4/12 + 3/12 = 7/24"],
            3,
            "Numitorul comun se păstrează: 4/12 + 3/12 = 7/12.",
        ),
        error_case(
            "Apasă primul pas care nu este corect.",
            (7, 10), (1, 4), "-",
            ["c.m.m.m.c.(10, 4) = 40", "7/10 = 14/20", "1/4 = 5/20", "14/20 − 5/20 = 9/20"],
            0,
            "Cel mai mic multiplu comun este 20, nu 40.",
        ),
        error_case(
            "Alege prima transformare greșită.",
            (2, 9), (5, 12), "+",
            ["c.m.m.m.c.(9, 12) = 36", "2/9 = 8/36", "5/12 = 20/36", "8/36 + 20/36 = 28/36"],
            2,
            "5/12 se amplifică cu 3, deci devine 15/36.",
        ),
        order_steps(
            "Așază corect pașii pentru calculul 2/3 + 5/8.",
            ["Determinăm c.m.m.m.c.(3, 8) = 24.", "Scriem 2/3 = 16/24 și 5/8 = 15/24.", "Adunăm: 16/24 + 15/24 = 31/24.", "Scoatem întregii: 31/24 = 1 7/24."],
            [2, 0, 3, 1],
            "Mai întâi alegem numitorul comun, apoi amplificăm, calculăm și scriem forma finală.",
        ),
        order_steps(
            "Așază corect pașii pentru calculul 11/15 − 2/9.",
            ["Determinăm c.m.m.m.c.(15, 9) = 45.", "Scriem 11/15 = 33/45 și 2/9 = 10/45.", "Scădem: 33/45 − 10/45 = 23/45.", "Verificăm că 23/45 este ireductibilă."],
            [1, 3, 0, 2],
            "Ordinea este: numitor comun, amplificare, scădere, verificarea formei ireductibile.",
        ),
        order_steps(
            "Construiește rezolvarea calculului 5/6 + 1/4.",
            ["Alegem numitorul comun 12.", "Transformăm: 5/6 = 10/12 și 1/4 = 3/12.", "Calculăm 10/12 + 3/12 = 13/12.", "Scriem 13/12 = 1 1/12."],
            [3, 1, 0, 2],
            "Pașii corecți duc la rezultatul 1 1/12.",
        ),
        match_results("Potrivește fiecare calcul cu rezultatul său.", [("2/7 + 3/7", "5/7"), ("11/12 − 3/12", "2/3"), ("1/3 + 1/6", "1/2")]),
        match_results("Leagă fiecare operație de valoarea corectă.", [("3/4 − 1/6", "7/12"), ("2/5 + 1/4", "13/20"), ("7/9 − 1/3", "4/9")]),
        match_results("Alege rezultatul potrivit pentru fiecare calcul.", [("5/8 + 3/4", "11/8"), ("13/15 − 2/5", "7/15"), ("1/2 + 5/12", "11/12")]),
        problem("Un elev a parcurs 1/3 dintr-un traseu dimineața și 2/5 după-amiaza. Ce fracție din traseu a parcurs?", (1, 3), (2, 5), "+"),
        problem("Dintr-o rolă s-au folosit dimineața 4 metri, apoi încă 7/10 metri. Câți metri s-au folosit în total?", (4, 1), (7, 10), "+"),
        problem("O plantă a crescut 1/2 cm într-o săptămână și 7/12 cm în următoarea. Care a fost creșterea totală?", (1, 2), (7, 12), "+"),
        problem("Un vas conținea 25 3/4 litri de ulei, iar apoi s-au scos 18 5/6 litri. Cât ulei a rămas?", (103, 4), (113, 6), "-"),
        mixed((3, 5), (7, 6), "+"),
        mixed((17, 8), (3, 4), "-"),
        mixed((7, 3), (3, 5), "+"),
        missing_term((2, 3), (7, 12), "+", (5, 4), missing_side="left", mode="inverse"),
        missing_term((11, 15), (2, 5), "-", (1, 3), mode="inverse"),
        missing_term((7, 8), (5, 8), "-", (1, 4), missing_side="left", mode="inverse"),
    ]

    assert len(questions) == 44
    return questions


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_fractii_ordinare_adunarea_si_scaderea.json"
    payload = {
        "title": "Adunarea și scăderea fracțiilor",
        "description": "Clasa a 5-a · Fracții ordinare",
        "difficulty": "easy",
        "questions": build_questions(),
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} intrebari in {target}.")


if __name__ == "__main__":
    main()
