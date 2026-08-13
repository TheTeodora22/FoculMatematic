"""Generează lecția introductivă despre divizori, multipli și valori comune."""

import json
from pathlib import Path


def grid(text, correct, wrong, explanation):
    correct, wrong = str(correct), [str(value) for value in wrong]
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3
    return {"text": text, "format": "grid", "points": 10, "explanation": explanation, "options": [
        {"text": wrong[0], "is_correct": False}, {"text": correct, "is_correct": True},
        {"text": wrong[1], "is_correct": False}, {"text": wrong[2], "is_correct": False},
    ]}


def tf(text, answer, explanation):
    return {"text": text, "format": "true_false", "points": 10, "explanation": explanation, "options": [
        {"text": "Adevărat", "is_correct": answer}, {"text": "Fals", "is_correct": not answer},
    ]}


def iq(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10, "interactive": data, "explanation": explanation}


def divisors(number):
    return [value for value in range(1, number + 1) if number % value == 0]


def common_divisors(a, b):
    return [value for value in divisors(min(a, b)) if a % value == 0 and b % value == 0]


def first_common_multiple(a, b):
    return next(value for value in range(max(a, b), a * b + 1) if value % a == 0 and value % b == 0)


def fields_for(answers):
    return [{"key": key} for key in answers]


def build_questions():
    questions = []

    # 1. Completează relația a = b · c.
    for a, b, c, missing in [(56, 7, 8, "c"), (120, 15, 8, "b"), (143, 13, 11, "a")]:
        answers = {missing: locals()[missing]}
        questions.append(iq(
            f"Completați relația care arată că {b} divide {a}.", "divisibility_values",
            {"mode": "relation", "a": a, "b": b, "c": c, "missing": missing, "fields": fields_for(answers), "answers": answers},
            f"{a} = {b} · {c}; de aceea {b} este divizor al lui {a}, iar {a} este multiplu de {b}.",
        ))

    # 2. Divizor sau multiplu?
    for a, b in [(7, 56), (13, 143), (8, 120)]:
        cards = [
            {"id": "a_div", "label": f"{a} este divizor al lui {b}"},
            {"id": "b_mult", "label": f"{b} este multiplu de {a}"},
            {"id": "a_mult", "label": f"{a} este multiplu de {b}"},
            {"id": "b_div", "label": f"{b} este divizor al lui {a}"},
        ]
        questions.append(iq(
            f"Alegeți toate denumirile corecte pentru relația {b} = {a} · {b // a}.", "divisibility_select",
            {"mode": "role", "cards": cards, "correct_ids": ["a_div", "b_mult"]},
            f"{a} este divizor, iar {b} este multiplu, deoarece împărțirea {b} : {a} este exactă.",
        ))

    # 4. Perechi de factori.
    for number in [36, 48, 60]:
        pairs = [[value, number // value] for value in range(1, int(number ** 0.5) + 1) if number % value == 0]
        answers = {}
        for index, pair in enumerate(pairs):
            answers[f"pair:{index}:left"] = pair[0]
            answers[f"pair:{index}:right"] = pair[1]
        questions.append(iq(
            f"Construiți toate perechile de factori pentru numărul {number}.", "divisibility_values",
            {"mode": "factor_pairs", "number": number, "pairs": pairs, "fields": fields_for(answers), "answers": answers},
            "Fiecare pereche are produsul egal cu numărul dat; numerele din perechi sunt divizori.",
        ))

    # 5. Fabrica divizorilor.
    for number in [24, 40, 63]:
        values = divisors(number)
        answers = {"list": ",".join(map(str, values))}
        questions.append(iq(
            f"Fabrica divizorilor: scrieți toți divizorii numărului {number}.", "divisibility_values",
            {"mode": "divisor_list", "number": number, "fields": fields_for(answers), "answers": answers},
            f"Divizorii lui {number} sunt: {', '.join(map(str, values))}.",
        ))

    # 6 și 7. Selectarea divizorilor și a multiplilor.
    select_divisor_sets = [(28, [1, 2, 4, 7, 14, 28, 3, 6, 12]), (45, [1, 3, 5, 9, 15, 45, 6, 10, 20]), (64, [1, 2, 4, 8, 16, 32, 64, 6, 12])]
    for number, values in select_divisor_sets:
        cards = [{"id": str(value), "label": str(value)} for value in values]
        correct = [str(value) for value in values if number % value == 0]
        questions.append(iq(f"Selectați toți divizorii lui {number}.", "divisibility_select", {"mode": "divisors", "cards": cards, "correct_ids": correct}, f"Un număr este selectat dacă {number} se împarte exact la el."))

    for base, values in [(6, [6, 12, 18, 20, 24, 30, 35, 42, 48]), (7, [7, 14, 19, 21, 28, 32, 35, 42, 49]), (9, [9, 18, 25, 27, 36, 45, 50, 54, 63])]:
        cards = [{"id": str(value), "label": str(value)} for value in values]
        correct = [str(value) for value in values if value % base == 0]
        questions.append(iq(f"Selectați toți multiplii lui {base}.", "divisibility_select", {"mode": "multiples", "cards": cards, "correct_ids": correct}, f"Multiplii selectați se pot scrie sub forma {base} · n."))

    # 8. Sortare în două zone.
    for divisor, values in [(4, [12, 14, 20, 22, 28, 31, 36, 42]), (6, [18, 20, 24, 27, 30, 35, 42, 50]), (9, [18, 25, 27, 36, 44, 54, 63, 70])]:
        zones = [{"id": "yes", "label": f"Divizibile cu {divisor}"}, {"id": "no", "label": f"Nu sunt divizibile cu {divisor}"}]
        cards = [{"id": str(value), "label": str(value), "zone": "yes" if value % divisor == 0 else "no"} for value in values]
        questions.append(iq(f"Sortați numerele după relația de divizibilitate cu {divisor}.", "divisibility_sort", {"mode": "two_zones", "zones": zones, "cards": cards}, "În prima zonă intră numai numerele care se împart exact la numărul dat."))

    # 9. Diagramă pentru divizorii comuni.
    for a, b in [(24, 40), (18, 30), (36, 48)]:
        da, db = set(divisors(a)), set(divisors(b))
        chosen = sorted(da | db)
        zones = [{"id": "a", "label": f"Numai pentru {a}"}, {"id": "common", "label": "Divizori comuni"}, {"id": "b", "label": f"Numai pentru {b}"}]
        cards = []
        for value in chosen:
            zone = "common" if value in da and value in db else "a" if value in da else "b"
            cards.append({"id": str(value), "label": str(value), "zone": zone})
        questions.append(iq(f"Așezați divizorii numerelor {a} și {b} în diagrama corectă.", "divisibility_sort", {"mode": "venn", "zones": zones, "cards": cards}, f"În intersecție se află: {', '.join(map(str, common_divisors(a, b)))}."))

    # 11. Cel mai mare divizor comun, construit din liste.
    for a, b in [(40, 24), (60, 48), (60, 72)]:
        da, db = divisors(a), divisors(b)
        answer = max(common_divisors(a, b))
        answers = {"greatest": answer}
        questions.append(iq(f"Comparați listele și marcați cel mai mare divizor comun al numerelor {a} și {b}.", "divisibility_values", {"mode": "greatest_common", "a": a, "b": b, "divisors_a": da, "divisors_b": db, "fields": fields_for(answers), "answers": answers}, f"Cel mai mare element care apare în ambele liste este {answer}."))

    # 12. Șirul multiplilor.
    sequence_specs = [(4, [4, None, 12, None, 20, 24]), (7, [7, 14, None, 28, None, 42]), (9, [9, None, 27, 36, None, 54])]
    for base, raw in sequence_specs:
        answers, items = {}, []
        for index, value in enumerate(raw):
            expected = base * (index + 1)
            if value is None:
                key = f"term:{index}"; answers[key] = expected; items.append({"key": key})
            else: items.append(value)
        questions.append(iq(f"Completați șirul multiplilor lui {base}.", "divisibility_values", {"mode": "sequence", "rows": [{"label": f"Multiplii lui {base}", "items": items}], "fields": fields_for(answers), "answers": answers}, f"Șirul continuă adunând de fiecare dată {base}."))

    # 13. Două șiruri de multipli.
    for a, b in [(4, 6), (6, 9), (8, 12)]:
        answers, rows = {}, []
        for base in (a, b):
            items = []
            for index in range(1, 7):
                value = base * index
                if index in {3, 5}:
                    key = f"{base}:{index}"; answers[key] = value; items.append({"key": key})
                else: items.append(value)
            rows.append({"label": f"Multiplii lui {base}", "items": items})
        questions.append(iq(f"Completați cele două șiruri și observați multiplii comuni ai lui {a} și {b}.", "divisibility_values", {"mode": "dual_sequence", "rows": rows, "fields": fields_for(answers), "answers": answers}, "Valorile care apar în ambele șiruri sunt multipli comuni."))

    # 14. Linie temporală pentru repetări simultane.
    for a, b, count, context in [(15, 18, 3, "mașini"), (7, 5, 3, "proiectoare"), (9, 12, 3, "semnale")]:
        first = first_common_multiple(a, b)
        moments = ",".join(str(first * factor) for factor in range(1, count + 1))
        answers = {"moments": moments}
        questions.append(iq(f"Două {context} repetă o acțiune la fiecare {a}, respectiv {b} secunde. Marcați primele {count} momente comune.", "divisibility_values", {"mode": "timeline", "a": a, "b": b, "count": count, "fields": fields_for(answers), "answers": answers}, f"Primele momente comune sunt {moments.replace(',', ', ')} secunde."))

    # 15. Primul multiplu comun.
    for a, b in [(8, 12), (9, 15), (12, 18)]:
        first = first_common_multiple(a, b)
        answers = {"first": first}
        questions.append(iq(f"Construiți șirurile și găsiți primul multiplu comun al numerelor {a} și {b}.", "divisibility_values", {"mode": "first_common", "a": a, "b": b, "multiples_a": [a * i for i in range(1, first // a + 1)], "multiples_b": [b * i for i in range(1, first // b + 1)], "fields": fields_for(answers), "answers": answers}, f"Primul număr pozitiv din ambele șiruri este {first}."))

    # 20. Detectivul greșelilor.
    error_sets = [
        (["Divizorii lui 18 sunt căutați în perechi.", "1 · 18 și 2 · 9 sunt produse corecte.", "3 · 5 = 18.", "Lista finală conține 1, 2, 3, 5, 9, 18."], 2, "3 · 5 este 15; perechea corectă este 3 · 6."),
        (["Multiplii lui 7 se obțin înmulțind cu numere naturale.", "7 · 1 = 7, 7 · 2 = 14.", "7 · 3 = 20.", "Următorul multiplu ar fi 28."], 2, "7 · 3 = 21, nu 20."),
        (["Divizorii lui 24 sunt 1, 2, 3, 4, 6, 8, 12, 24.", "Divizorii lui 40 sunt 1, 2, 4, 5, 8, 10, 20, 40.", "Divizorii comuni sunt 1, 2, 4, 8.", "Cel mai mare divizor comun este 10."], 3, "Cel mai mare element comun este 8."),
    ]
    for index, (steps, error_index, explanation) in enumerate(error_sets, 1):
        questions.append(iq(f"Detectivul divizibilității: apăsați primul pas greșit din rezolvarea {index}.", "divisibility_error", {"steps": steps, "error_index": error_index}, explanation))

    # 21. Corectarea afirmațiilor.
    questions.extend([
        grid("Înlocuiți numărul greșit: «Divizorii lui 16 sunt 1, 2, 4, 6, 8, 16». Cu ce trebuie înlocuit 6?", "Nu trebuie să apară niciun număr în loc", [3, 12, 32], "6 nu divide 16, iar lista completă rămâne 1, 2, 4, 8, 16."),
        grid("Corectați afirmația: «Primii multipli pozitivi ai lui 9 sunt 9, 18, 26, 36». Ce număr îl înlocuiește pe 26?", 27, [24, 28, 29], "9 · 3 = 27."),
        grid("Corectați afirmația: «Cel mai mare divizor comun al lui 40 și 24 este 4». Valoarea corectă este:", 8, [2, 6, 12], "Divizorii comuni sunt 1, 2, 4 și 8."),
    ])

    # 22. Adevărat sau fals, numai din teoria lecției.
    questions.extend([
        tf("14 este multiplu de 7.", True, "14 = 7 · 2."),
        tf("13 divide 143.", True, "143 = 13 · 11."),
        tf("59 este divizibil cu 7.", False, "59 : 7 are restul 3."),
        tf("4 este divizor comun al numerelor 8 și 20.", True, "Atât 8, cât și 20 se împart exact la 4."),
    ])

    # 25. Bingo de divizibilitate.
    for divisor, values in [(4, [8, 10, 12, 15, 16, 18, 20, 22, 24, 27, 28, 30]), (6, [12, 14, 18, 20, 24, 25, 30, 32, 36, 40, 42, 45]), (9, [9, 12, 18, 20, 27, 30, 36, 40, 45, 50, 54, 63])]:
        cards = [{"id": str(value), "label": str(value)} for value in values]
        correct = [str(value) for value in values if value % divisor == 0]
        questions.append(iq(f"Bingo: găsiți toate numerele divizibile cu {divisor}.", "divisibility_select", {"mode": "bingo", "cards": cards, "correct_ids": correct}, f"Sunt corecte numai numerele care se împart exact la {divisor}."))

    # Grile simple pentru fixarea vocabularului și calculelor din lecție.
    questions.extend([
        grid("Care număr este divizor al lui 30?", 5, [4, 7, 8], "30 = 5 · 6."),
        grid("Care număr este multiplu de 12?", 84, [70, 82, 86], "84 = 12 · 7."),
        grid("Care este lista completă a divizorilor lui 10?", "1, 2, 5, 10", ["1, 2, 10", "2, 5, 10", "1, 5, 10, 20"], "Toate cele patru numere împart exact pe 10."),
        grid("Care este un divizor comun al numerelor 27 și 36?", 9, [4, 6, 12], "27 = 9 · 3 și 36 = 9 · 4."),
        grid("Care este un multiplu comun al numerelor 8 și 12?", 48, [20, 32, 36], "48 = 8 · 6 = 12 · 4."),
        grid("Care este cel mai mare divizor comun al numerelor 60 și 48?", 12, [6, 8, 24], "Divizorii comuni sunt 1, 2, 3, 4, 6 și 12."),
        grid("Care este primul multiplu pozitiv comun al numerelor 9 și 12?", 36, [18, 27, 48], "36 apare primul în ambele șiruri de multipli."),
        grid("120 de flori se așază în rânduri egale. Care variantă folosește toate florile?", "8 rânduri a câte 15", ["7 rânduri a câte 15", "9 rânduri a câte 14", "11 rânduri a câte 10"], "8 · 15 = 120."),
    ])

    assert len(questions) == 60, len(questions)
    assert len({question["text"] for question in questions}) == len(questions)
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_divizibilitatea_numerelor_naturale.json"
    payload = {"title": "Divizibilitatea numerelor naturale", "description": "Clasa a 5-a · Divizor. Multiplu. Divizori și multipli comuni", "difficulty": "medium", "questions": build_questions()}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
