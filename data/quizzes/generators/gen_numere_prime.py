"""Generează lecția Numere prime. Numere compuse pentru clasa a V-a."""

import json
from pathlib import Path


def is_prime(number):
    if number < 2:
        return False
    return all(number % divisor for divisor in range(2, int(number ** 0.5) + 1))


def proper_divisors(number):
    return [value for value in range(1, number) if number % value == 0]


def interactive(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10, "interactive": data, "explanation": explanation}


def true_false(text, answer, explanation):
    return {"text": text, "format": "true_false", "points": 10, "explanation": explanation, "options": [
        {"text": "Adevărat", "is_correct": answer}, {"text": "Fals", "is_correct": not answer},
    ]}


def grid(text, correct, wrong, explanation):
    correct, wrong = str(correct), [str(value) for value in wrong]
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3
    return {"text": text, "format": "grid", "points": 10, "explanation": explanation, "options": [
        {"text": wrong[0], "is_correct": False}, {"text": correct, "is_correct": True},
        {"text": wrong[1], "is_correct": False}, {"text": wrong[2], "is_correct": False},
    ]}


def sort_prime(values, label):
    def zone(value):
        if value == 1:
            return "neither"
        return "prime" if is_prime(value) else "composite"
    return interactive(
        f"Sortează numerele din setul {label} în cele trei zone.", "divisibility_sort",
        {"mode": "two_zones", "zones": [
            {"id": "prime", "label": "Numere prime"},
            {"id": "composite", "label": "Numere compuse"},
            {"id": "neither", "label": "Nici prim, nici compus"},
        ], "cards": [{"id": f"n{value}", "label": str(value), "zone": zone(value)} for value in values]},
        "Numărul 1 nu este nici prim, nici compus; un număr prim are exact doi divizori.",
    )


def prime_hunt(values, label):
    correct = [str(value) for value in values if is_prime(value)]
    return interactive(
        f"Vânătoarea {label}: selectează toate numerele prime.", "divisibility_select",
        {"mode": "criteria", "cards": [{"id": str(value), "label": str(value)} for value in values], "correct_ids": correct},
        f"Numerele prime din panou sunt: {', '.join(correct)}.",
    )


def trial(number, divisors, label):
    tests = [{"divisor": divisor, "remainder": number % divisor} for divisor in divisors]
    answers = {f"remainder:{row['divisor']}": row["remainder"] for row in tests}
    answers["classification"] = "prim" if is_prime(number) else "compus"
    return interactive(
        f"Laboratorul {label}: verifică numărul {number} prin împărțirile indicate și clasifică-l.", "prime_workbench",
        {"mode": "trial", "number": number, "tests": tests, "answers": answers},
        f"{number} este {'prim' if is_prime(number) else 'compus'}; resturile completate arată dacă apare un divizor propriu.",
    )


def error_detective(label, steps, error_index, explanation):
    return interactive(f"Detectivul greșelilor {label}: apasă primul pas greșit.", "divisibility_error", {"steps": steps, "error_index": error_index}, explanation)


def factor_product(target, factors, distractors, label):
    entries = []
    for index, value in enumerate(factors + distractors):
        entries.append({"id": f"c{index}", "value": value})
    correct_ids = [entry["id"] for entry in entries[:len(factors)]]
    return interactive(
        f"Construcția {label}: formează numărul compus {target} folosind numai factorii primi potriviți.", "prime_workbench",
        {"mode": "factor_product", "target": target, "slot_count": len(factors), "cards": entries, "correct_ids": correct_ids, "answers": {"factors": ",".join(map(str, sorted(factors)))}},
        f"{target} = {' · '.join(map(str, factors))}.",
    )


def prime_pair(target, operator, left, right, label):
    return interactive(
        f"Completează scrierea {label} cu două numere prime.", "prime_workbench",
        {"mode": "prime_pair", "target": target, "operator": operator, "unordered_pair": operator in {"+", "×"}, "fields": [{"key": "left"}, {"key": "right"}], "answers": {"left": left, "right": right}},
        f"O scriere corectă este {left} {operator} {right} = {target}; ambele numere sunt prime.",
    )


def prime_equation(equation, answers, label):
    fields = [{"key": key, "label": key} for key in answers]
    return interactive(
        f"Ecuația cu numere prime {label}: determină necunoscutele.", "prime_workbench",
        {"mode": "prime_equation", "equation": equation, "fields": fields, "answers": answers},
        "Înlocuirea valorilor prime găsite verifică egalitatea.",
    )


def select_n(text, candidates, valid, explanation):
    return interactive(text, "divisibility_select", {"mode": "criteria", "cards": [{"id": str(value), "label": str(value)} for value in candidates], "correct_ids": [str(value) for value in valid]}, explanation)


def escape_room(label, clues, answers):
    clue_data = [{"key": f"digit:{index}", "text": text} for index, text in enumerate(clues)]
    answer_data = {f"digit:{index}": value for index, value in enumerate(answers)}
    return interactive(
        f"Camera de evadare {label}: află codul din trei cifre.", "prime_workbench",
        {"mode": "escape_code", "clues": clue_data, "answers": answer_data},
        f"Codul este {''.join(map(str, answers))}.",
    )


def perfect_number(number, candidates, label):
    divisors = proper_divisors(number)
    total = sum(divisors)
    verdict = "perfect" if total == number else "nu este perfect"
    return interactive(
        f"Proiectul {label}: verifică dacă {number} este număr perfect.", "prime_workbench",
        {"mode": "perfect_number", "number": number, "candidates": candidates, "correct_ids": list(map(str, divisors)), "answers": {"divisors": ",".join(map(str, divisors)), "sum": total}},
        f"Divizorii mai mici decât numărul sunt {', '.join(map(str, divisors))}; suma este {total}, deci {number} {verdict}.",
    )


def build_questions():
    questions = []

    for values, label in [
        ([1, 2, 4, 5, 9, 11, 15, 17], "A"),
        ([1, 3, 6, 7, 13, 18, 19, 20], "B"),
        ([1, 23, 25, 29, 33, 37, 49, 53], "C"),
        ([1, 61, 67, 71, 77, 83, 91, 97], "D"),
    ]:
        questions.append(sort_prime(values, label))

    for values, label in [
        ([138, 179, 183, 318, 381, 813], "A"),
        ([71, 73, 79, 81, 83, 87, 89, 91], "B"),
        ([101, 103, 105, 107, 109, 111, 113, 115], "C"),
        ([157, 163, 167, 169, 173, 177, 179, 181], "D"),
    ]:
        questions.append(prime_hunt(values, label))

    questions.extend([
        trial(71, [2, 3, 5, 7], "A"),
        trial(157, [2, 3, 5, 7, 11, 13], "B"),
        trial(221, [2, 3, 5, 7, 11, 13], "C"),
        trial(241, [2, 3, 5, 7, 11, 13], "D"),
    ])

    questions.extend([
        error_detective("A", ["71 : 2 dă restul 1", "71 : 3 dă restul 2", "71 : 5 dă restul 0", "71 este compus"], 2, "71 : 5 dă restul 1, nu 0; numărul 71 este prim."),
        error_detective("B", ["221 : 13 = 17", "13 este divizor propriu al lui 221", "221 este număr prim"], 2, "Existența divizorului propriu 13 dovedește că 221 este compus."),
        error_detective("C", ["1 are un singur divizor", "Un număr prim are exact doi divizori", "Prin urmare, 1 este număr prim"], 2, "Numărul 1 nu este prim, deoarece nu are exact doi divizori."),
        error_detective("D", ["2 are divizorii 1 și 2", "2 este număr prim", "Toate numerele prime sunt impare"], 2, "Numărul 2 este singurul număr prim par."),
    ])

    for target, factors, distractors, label in [
        (30, [2, 3, 5], [7, 11], "A"),
        (42, [2, 3, 7], [5, 11], "B"),
        (60, [2, 2, 3, 5], [7, 11], "C"),
        (84, [2, 2, 3, 7], [5, 11], "D"),
    ]:
        questions.append(factor_product(target, factors, distractors, label))

    for target, left, right, label in [(30, 13, 17, "30 = □ + □"), (26, 7, 19, "26 = □ + □"), (38, 19, 19, "38 = □ + □"), (24, 11, 13, "24 = □ + □")]:
        questions.append(prime_pair(target, "+", left, right, label))
    for target, left, right, label in [(46, 53, 7, "46 = □ − □"), (26, 31, 5, "26 = □ − □"), (41, 43, 2, "41 = □ − □"), (27, 29, 2, "27 = □ − □")]:
        questions.append(prime_pair(target, "−", left, right, label))
    for target, left, right, label in [(39, 3, 13, "39 = □ · □"), (85, 5, 17, "85 = □ · □"), (77, 7, 11, "77 = □ · □"), (143, 11, 13, "143 = □ · □")]:
        questions.append(prime_pair(target, "×", left, right, label))

    questions.extend([
        prime_equation("5a + 12b = 89", {"a": 13, "b": 2}, "A"),
        prime_equation("15a + 3b = 180", {"a": 11, "b": 5}, "B"),
        prime_equation("7a + 5b = 59", {"a": 7, "b": 2}, "C"),
        prime_equation("4a + 3b = 43", {"a": 7, "b": 5}, "D"),
    ])

    candidates = list(range(0, 8))
    questions.extend([
        select_n("Selectează valorile lui n pentru care (n + 1)(n + 13) este număr prim.", candidates, [n for n in candidates if is_prime((n + 1) * (n + 13))], "Un produs este prim numai când unul dintre factorii naturali este 1; aici rezultă n = 0."),
        select_n("Selectează valorile lui n pentru care n² + 30n este număr prim.", candidates, [n for n in candidates if is_prime(n * n + 30 * n)], "n² + 30n = n(n + 30), iar în intervalul dat numai n = 1 produce numărul prim 31."),
        select_n("Selectează valorile lui n dintre 6 și 12 pentru care n² − 6n este număr prim.", list(range(6, 13)), [n for n in range(6, 13) if is_prime(n * n - 6 * n)], "n² − 6n = n(n − 6); singura valoare potrivită este n = 7."),
        select_n("Testează n = 0, 1, 2, 3 și selectează cazurile în care 6ⁿ + 3ⁿ + 2ⁿ + 1 este compus.", list(range(4)), [n for n in range(4) if not is_prime(6 ** n + 3 ** n + 2 ** n + 1)], "Pentru fiecare valoare indicată, expresia obținută este un număr compus."),
    ])

    offset_sets = [(1, 11, 27), (1, 7, 13), (3, 9, 15)]
    for index, offsets in enumerate(offset_sets, start=1):
        pool = list(range(0, 21))
        valid = [n for n in pool if all(is_prime(n + offset) for offset in offsets)]
        assert valid
        expression = ", ".join(f"n + {offset}" for offset in offsets)
        questions.append(select_n(f"Selectează valorile lui n pentru care toate numerele {expression} sunt prime (setul {index}).", pool, valid, f"Verificarea fiecărei valori lasă soluțiile: {', '.join(map(str, valid))}."))

    questions.extend([
        escape_room("A", ["Singurul număr prim par", "Cifra unităților numărului prim 19", "Cel mai mic număr prim impar"], [2, 9, 3]),
        escape_room("B", ["Numărul de divizori ai unui număr prim", "Cifra unităților lui 37", "Numărul prim dintre 4 și 6"], [2, 7, 5]),
        escape_room("C", ["Cifra zecilor lui 71", "Restul împărțirii lui 13 la 5", "Numărul prim care divide 9"], [7, 3, 3]),
    ])

    questions.extend([
        true_false("Numărul 1 este număr prim.", False, "Numărul 1 are un singur divizor și nu este nici prim, nici compus."),
        true_false("Numărul 2 este singurul număr prim par.", True, "Orice alt număr par are cel puțin divizorii 1, 2 și numărul însuși."),
        true_false("Orice număr natural mai mare decât 1 este prim sau compus.", True, "Aceasta este clasificarea prezentată în lecție."),
        true_false("Dacă un număr are un divizor propriu, atunci numărul este compus.", True, "Divizorul propriu este diferit de 1 și de numărul însuși."),
        true_false("Toate numerele impare sunt prime.", False, "De exemplu, 9 este impar și compus: 9 = 3 · 3."),
    ])

    questions.extend([
        perfect_number(6, [1, 2, 3, 4, 5], "A"),
        perfect_number(28, [1, 2, 4, 7, 14, 21], "B"),
        perfect_number(12, [1, 2, 3, 4, 6, 8], "C"),
    ])

    questions.extend([
        grid("Care dintre numere este prim?", 179, [138, 183, 813], "179 nu are niciun divizor propriu; celelalte numere sunt divizibile cu 3."),
        grid("Care dintre numere are exact doi divizori?", 97, [1, 91, 100], "97 are numai divizorii 1 și 97."),
        grid("Care număr dovedește că 299 este compus?", 13, [7, 11, 17], "299 = 13 · 23."),
        grid("Care este o scriere a lui 85 ca produs de două numere prime?", "5 · 17", ["1 · 85", "7 · 12", "3 · 28"], "5 și 17 sunt prime, iar produsul lor este 85."),
        grid("Care dintre numere nu este nici prim, nici compus?", 1, [2, 4, 9], "În lecție, numărul 1 este cazul special: nici prim, nici compus."),
        grid("Care număr este perfect?", 6, [8, 10, 12], "Divizorii lui 6 mai mici decât el sunt 1, 2 și 3, iar suma lor este 6."),
    ])

    assert len(questions) == 60, len(questions)
    assert len({question["text"] for question in questions}) == 60
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_numere_prime_numere_compuse.json"
    payload = {"title": "Numere prime. Numere compuse", "description": "Clasa a 5-a · Recunoașterea numerelor prime și compuse", "difficulty": "medium", "questions": build_questions()}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
