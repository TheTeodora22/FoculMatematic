"""Generează lecția despre puterea cu exponent natural a unei fracții ordinare."""

import json
from fractions import Fraction
from pathlib import Path


def grid(text, correct, wrong, explanation):
    values = [str(correct), *map(str, wrong)]
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
        "text": text, "type": "fraction_power", "format": "interactive", "points": 10,
        "explanation": explanation, "interactive": {"mode": mode, **data},
    }


def build(base, exponent):
    numerator = base[0] ** exponent
    denominator = base[1] ** exponent
    return interactive(
        f"Calculează ({base[0]}/{base[1]})^{exponent}.", "build",
        {"base": list(base), "exponent": exponent, "answers": {
            "numerator_power": numerator, "denominator_power": denominator,
            "result_numerator": numerator, "result_denominator": denominator,
        }},
        f"Ridicăm separat numărătorul și numitorul: {base[0]}^{exponent}/{base[1]}^{exponent} = {numerator}/{denominator}.",
    )


def expand(base, exponent):
    factor = f"{base[0]}/{base[1]}"
    return interactive(
        f"Desfă ({factor})^{exponent} ca produs de factori identici.", "expand",
        {"base": list(base), "exponent": exponent, "answers": {f"factor_{index + 1}": factor for index in range(exponent)}},
        f"Puterea conține {exponent} factori egali cu {factor}.",
    )


def compress(base, exponent):
    factor = f"{base[0]}/{base[1]}"
    product = " · ".join([factor] * exponent)
    return interactive(
        f"Scrie produsul {product} sub forma unei singure puteri.", "compress",
        {"product": product, "answers": {"base": factor, "exponent": exponent}},
        f"Factorul {factor} apare de {exponent} ori, deci obținem ({factor})^{exponent}.",
    )


def fields_case(text, mode, expression, fields, answers, explanation):
    return interactive(text, mode, {"expression": expression, "fields": fields, "answers": answers}, explanation)


def choice_case(text, mode, expression, instruction, choices, answer_key, answer, explanation, fields=None, extra_answers=None):
    answers = {answer_key: answer, **(extra_answers or {})}
    return interactive(text, mode, {
        "expression": expression, "instruction": instruction,
        "choices": [{"value": value, "label": label} for value, label in choices],
        "answer_key": answer_key, "fields": fields or [], "answers": answers,
    }, explanation)


def error_case(text, steps, error_index, explanation):
    return interactive(text, "error", {"steps": steps, "answers": {"error_index": error_index}}, explanation)


def order_case(text, steps, display_order, explanation):
    return interactive(text, "order_steps", {
        "steps": steps, "display_order": display_order,
        "answers": {"order": ",".join(map(str, range(len(steps))))},
    }, explanation)


def match_case(text, pairs, order):
    return interactive(text, "match", {
        "pairs": [{"left": left, "right": right} for left, right in pairs],
        "result_order": order,
        "answers": {f"match_{index}": index for index in range(len(pairs))},
    }, "Aplicăm regula indicată și păstrăm aceeași bază sau același exponent, după caz.")


def visual(base_denominator, exponent, choices):
    cells = base_denominator ** exponent
    result = f"1/{cells}"
    return interactive(
        f"Selectează partea din întreg reprezentată de (1/{base_denominator})^{exponent}.", "visual",
        {"cell_count": cells, "filled_cells": 1, "caption": f"Întregul a fost împărțit succesiv de {exponent} ori în câte {base_denominator} părți.", "choices": choices, "answers": {"selected": result}},
        f"(1/{base_denominator})^{exponent} = 1/{base_denominator}^{exponent} = {result}.",
    )


def problem(text, base, exponent):
    result = Fraction(base[0] ** exponent, base[1] ** exponent)
    return interactive(text, "problem", {"base": list(base), "exponent": exponent, "answers": {
        "result_numerator": result.numerator, "result_denominator": result.denominator,
    }}, f"Calculăm ({base[0]}/{base[1]})^{exponent} = {result.numerator}/{result.denominator}.")


def build_questions():
    questions = [
        grid("Rezultatul lui (2/3)³ este:", "8/27", ["6/9", "8/9", "2/27"], "Ridicăm la cub atât 2, cât și 3."),
        grid("Cât este (5/7)⁰?", "1", ["0", "5/7", "7/5"], "Orice fracție nenulă ridicată la puterea 0 este 1."),
        grid("Scrierea sub formă de produs a lui (3/4)⁴ este:", "3/4 · 3/4 · 3/4 · 3/4", ["3/4 · 4", "3·4/4·4", "12/16"], "Exponentul 4 arată că baza apare ca factor de patru ori."),
        grid("Rezultatul lui (2/5)³ · (2/5)² este:", "(2/5)⁵", ["(2/5)⁶", "(4/10)⁵", "(2/5)¹"], "La înmulțirea puterilor cu aceeași bază, adunăm exponenții."),
        grid("Rezultatul lui [(3/7)²]³ este:", "(3/7)⁶", ["(3/7)⁵", "(9/49)³", "(3/7)⁹"], "La puterea unei puteri, înmulțim exponenții."),
        true_false("Pentru orice fracție nenulă a/b, avem (a/b)¹ = a/b.", "Adevărat", "Exponentul 1 păstrează baza neschimbată."),
        true_false("La ridicarea unei fracții la putere se ridică la putere numai numărătorul.", "Fals", "Se ridică la putere atât numărătorul, cât și numitorul."),
        true_false("(2/3)² · (5/7)² = (10/21)².", "Adevărat", "Puterile au același exponent, deci putem înmulți bazele."),
        build((2, 3), 3), build((3, 5), 4), build((4, 7), 2), build((5, 6), 3),
        expand((2, 5), 3), expand((4, 9), 2), expand((3, 7), 4),
        compress((5, 8), 3), compress((2, 11), 4), compress((7, 9), 2),
        fields_case("Completează exponentul din egalitatea (2/3)^□ = 16/81.", "missing", "(2/3)^□ = 16/81", [{"key": "exponent", "label": "Exponent"}], {"exponent": 4}, "2⁴/3⁴ = 16/81, deci exponentul este 4."),
        fields_case("Completează baza: (□)³ = 27/125.", "missing", "(□)³ = 27/125", [{"key": "base", "label": "Baza fracției"}], {"base": "3/5"}, "Rădăcina cubică a lui 27 este 3, iar a lui 125 este 5."),
        fields_case("Completează numărătorul: (□/4)² = 9/16.", "missing", "(□/4)² = 9/16", [{"key": "numerator", "label": "Numărător"}], {"numerator": 3}, "Numărul al cărui pătrat este 9 este 3."),
        fields_case("Completează numitorul: (5/□)³ = 125/216.", "missing", "(5/□)³ = 125/216", [{"key": "denominator", "label": "Numitor"}], {"denominator": 6}, "Numitorul căutat are cubul 216, deci este 6."),
        choice_case("Alege regula potrivită pentru (4/9)³ · (4/9)⁵.", "rule", "(4/9)³ · (4/9)⁵", "Ce regulă aplicăm?", [("add", "Păstrăm baza și adunăm exponenții"), ("multiply", "Păstrăm baza și înmulțim exponenții"), ("bases", "Înmulțim bazele și exponenții")], "rule", "add", "Bazele sunt egale, deci adunăm exponenții."),
        choice_case("Alege regula potrivită pentru (7/10)⁹ : (7/10)⁴.", "rule", "(7/10)⁹ : (7/10)⁴", "Ce regulă aplicăm?", [("subtract", "Păstrăm baza și scădem exponenții"), ("divide", "Împărțim exponenții"), ("invert", "Inversăm prima bază")], "rule", "subtract", "La împărțirea puterilor cu aceeași bază, scădem exponenții."),
        choice_case("Alege regula potrivită pentru [(2/5)³]⁴.", "rule", "[(2/5)³]⁴", "Ce regulă aplicăm?", [("multiply", "Păstrăm baza și înmulțim exponenții"), ("add", "Adunăm exponenții"), ("keep", "Păstrăm numai exponentul exterior")], "rule", "multiply", "La puterea unei puteri, exponenții se înmulțesc."),
        choice_case("Alege transformarea corectă pentru (3/4)⁵ · (2/7)⁵.", "rule", "(3/4)⁵ · (2/7)⁵", "Puterile au același exponent.", [("product", "[(3/4) · (2/7)]⁵"), ("sum", "[(3/4) + (2/7)]⁵"), ("ten", "(6/28)¹⁰")], "rule", "product", "Înmulțim bazele și păstrăm exponentul 5."),
        choice_case("Construiește exponentul rezultat pentru (5/8)⁶ · (5/8)³.", "exponent_rule", "(5/8)⁶ · (5/8)³", "Alege operația dintre exponenți și completează rezultatul.", [("+", "6 + 3"), ("−", "6 − 3"), ("·", "6 · 3")], "operation", "+", "Exponenții se adună: 6 + 3 = 9.", [{"key": "result_exponent", "label": "Exponent final"}], {"result_exponent": 9}),
        choice_case("Construiește exponentul rezultat pentru (3/11)⁸ : (3/11)².", "exponent_rule", "(3/11)⁸ : (3/11)²", "Alege operația dintre exponenți și completează rezultatul.", [("−", "8 − 2"), ("+", "8 + 2"), ("·", "8 · 2")], "operation", "−", "Exponenții se scad: 8 − 2 = 6.", [{"key": "result_exponent", "label": "Exponent final"}], {"result_exponent": 6}),
        choice_case("Construiește exponentul rezultat pentru [(7/9)²]⁵.", "exponent_rule", "[(7/9)²]⁵", "Alege operația dintre exponenți și completează rezultatul.", [("·", "2 · 5"), ("+", "2 + 5"), ("−", "5 − 2")], "operation", "·", "Exponenții se înmulțesc: 2 · 5 = 10.", [{"key": "result_exponent", "label": "Exponent final"}], {"result_exponent": 10}),
        choice_case("Construiește exponentul rezultat pentru (4/13)⁷ : (4/13)⁷.", "exponent_rule", "(4/13)⁷ : (4/13)⁷", "Alege operația și completează exponentul.", [("−", "7 − 7"), ("+", "7 + 7"), ("·", "7 · 7")], "operation", "−", "Diferența exponenților este 0, iar puterea este 1.", [{"key": "result_exponent", "label": "Exponent final"}], {"result_exponent": 0}),
        error_case("Identifică primul pas greșit în calculul lui (2/3)³.", ["Ridicăm numărătorul: 2³ = 8.", "Păstrăm numitorul: 3.", "Obținem 8/3."], 1, "Și numitorul trebuie ridicat la cub: 3³ = 27."),
        error_case("Apasă prima transformare incorectă pentru (5/7)² · (5/7)³.", ["Bazele sunt egale.", "Înmulțim exponenții: 2 · 3 = 6.", "Scriem (5/7)⁶."], 1, "La înmulțire adunăm exponenții și obținem exponentul 5."),
        error_case("Găsește primul pas greșit în calculul [(3/4)²]³.", ["Păstrăm baza 3/4.", "Adunăm exponenții: 2 + 3 = 5.", "Obținem (3/4)⁵."], 1, "La puterea unei puteri înmulțim exponenții: 2 · 3 = 6."),
        order_case("Așază pașii calculului (3/5)³.", ["Ridicăm numărătorul: 3³ = 27.", "Ridicăm numitorul: 5³ = 125.", "Scriem rezultatul 27/125."], [2, 0, 1], "Numărătorul și numitorul se ridică la același exponent."),
        order_case("Construiește rezolvarea lui (2/7)⁴ · (2/7)³.", ["Observăm că bazele sunt egale.", "Adunăm exponenții: 4 + 3 = 7.", "Păstrăm baza 2/7.", "Obținem (2/7)⁷."], [3, 1, 0, 2], "Mai întâi recunoaștem regula, apoi adunăm exponenții și păstrăm baza."),
        order_case("Ordonează pașii pentru [(4/9)²]³.", ["Identificăm puterea unei puteri.", "Înmulțim exponenții: 2 · 3 = 6.", "Păstrăm baza 4/9.", "Scriem (4/9)⁶."], [2, 0, 3, 1], "Puterea unei puteri păstrează baza și înmulțește exponenții."),
        match_case("Potrivește fiecare putere cu rezultatul ei.", [("(1/2)³", "1/8"), ("(2/3)²", "4/9"), ("(3/5)³", "27/125")], [2, 0, 1]),
        match_case("Potrivește fiecare expresie cu puterea simplificată.", [("(2/7)³ · (2/7)⁴", "(2/7)⁷"), ("(5/9)⁸ : (5/9)³", "(5/9)⁵"), ("[(3/4)²]⁵", "(3/4)¹⁰")], [1, 2, 0]),
        match_case("Leagă fiecare produs de forma cu un singur exponent.", [("(2/3)⁴ · (5/7)⁴", "(10/21)⁴"), ("(3/8)² · (4/5)²", "(3/10)²"), ("(7/9)³ : (2/5)³", "(35/18)³")], [2, 0, 1]),
        visual(2, 3, ["1/4", "1/6", "1/8", "3/8"]), visual(3, 2, ["1/6", "1/9", "2/9", "1/27"]), visual(2, 4, ["1/8", "1/12", "1/16", "4/16"]),
        fields_case("Scrie 81/256 ca putere cu baza 3/4.", "given_base", "81/256 = (3/4)^□", [{"key": "exponent", "label": "Exponent"}], {"exponent": 4}, "81 = 3⁴ și 256 = 4⁴."),
        fields_case("Scrie 32/243 ca putere cu baza 2/3.", "given_base", "32/243 = (2/3)^□", [{"key": "exponent", "label": "Exponent"}], {"exponent": 5}, "32 = 2⁵ și 243 = 3⁵."),
        fields_case("Scrie 343/216 ca putere cu exponentul 3.", "given_exponent", "343/216 = (□)³", [{"key": "base", "label": "Baza"}], {"base": "7/6"}, "343 = 7³ și 216 = 6³."),
        problem("O foaie se înjumătățește succesiv de 4 ori. Ce fracție din foaia inițială reprezintă una dintre bucățile finale?", (1, 2), 4),
    ]
    assert len(questions) == 46
    assert len({question["text"] for question in questions}) == len(questions)
    return questions


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_fractii_ordinare_puterea.json"
    payload = {
        "title": "Puterea cu exponent natural a unei fracții ordinare",
        "description": "Clasa a 5-a · Fracții ordinare",
        "difficulty": "easy",
        "questions": build_questions(),
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} întrebări în {target}.")


if __name__ == "__main__":
    main()
