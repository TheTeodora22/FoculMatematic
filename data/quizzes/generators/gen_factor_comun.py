"""Generează lecția „Factor comun” cu exerciții variate și interactive."""

import json
from pathlib import Path


def fmt(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def q(text, correct, wrong, explanation, points=10):
    answers = [str(correct), *(str(value) for value in wrong)]
    assert len(answers) == 4 and len(set(answers)) == 4
    return {
        "text": text,
        "points": points,
        "explanation": explanation,
        "options": [
            {"text": answers[1], "is_correct": False},
            {"text": answers[0], "is_correct": True},
            {"text": answers[2], "is_correct": False},
            {"text": answers[3], "is_correct": False},
        ],
    }


def nq(text, answer, explanation, wrong=None):
    wrong = wrong or [answer - 10, answer + 10, answer + 100]
    return q(text, fmt(answer), [fmt(value) for value in wrong], explanation)


def iq(text, question_type, interactive, explanation):
    return {
        "text": text,
        "type": question_type,
        "points": 10,
        "explanation": explanation,
        "interactive": interactive,
    }


def build_questions():
    questions = []

    # Calcule scurte, fiecare cu altă idee
    direct = [
        ("Calculează eficient 3 · 45 + 3 · 15.", 180, "Scoatem 3 factor comun: 3 · (45 + 15) = 3 · 60 = 180.", [150, 165, 195]),
        ("Calculează folosind factorul comun: 20 · 48 + 20 · 2.", 1_000, "20 · (48 + 2) = 20 · 50 = 1 000.", [960, 980, 1_020]),
        ("Calculează eficient 28 · 521 − 28 · 21.", 14_000, "28 · (521 − 21) = 28 · 500 = 14 000.", [13_500, 14_028, 15_000]),
        ("Calculează 128 · 337 + 128 · 663 prin scoaterea factorului comun.", 128_000, "128 · (337 + 663) = 128 · 1 000 = 128 000.", [127_000, 128_100, 129_000]),
        ("Calculează eficient 2 029 · 599 + 2 029.", 1_217_400, "Al doilea termen este 2 029 · 1. Obținem 2 029 · (599 + 1) = 2 029 · 600 = 1 217 400.", [1_215_400, 1_217_029, 1_219_400]),
        ("Calculează 1 000 · 372 + 259 · 1 000 − 153 · 1 000.", 478_000, "Scoatem 1 000 factor comun: 1 000 · (372 + 259 − 153) = 478 000.", [468_000, 477_000, 488_000]),
    ]
    for item in direct:
        questions.append(nq(*item))

    # Înțelegerea metodei
    questions.extend([
        q("Care este forma factorizată a expresiei 12 · 13 + 12 · 15 + 12 · 72?", "12 · (13 + 15 + 72)", ["12 · (13 · 15 · 72)", "12 + (13 + 15 + 72)", "36 · (13 + 15 + 72)"], "Factorul 12 apare în fiecare produs și se scoate în fața parantezei."),
        q("Care este forma factorizată corectă pentru 63 · 78 − 63 · 33 + 63 · 45?", "63 · (78 − 33 + 45)", ["63 · (78 − 33 · 45)", "63 · (78 + 33 − 45)", "189 · (78 − 33 + 45)"], "Păstrăm în paranteză semnele și factorii rămași."),
        q("În egalitatea 125 · 234 − 125 · 28 + 125 · 194 = 125 · (234 − 28 + 194), factorul comun este:", "125", ["234", "28", "194"], "125 este factor în toate cele trei produse."),
        q("Ce termen trebuie scris ca produs cu 1 înainte de a scoate factor comun din 2 413 · 1 001 − 2 413?", "2 413 = 2 413 · 1", ["2 413 = 1 · 1", "2 413 = 2 413 · 0", "2 413 = 2 413 + 1"], "Orice număr este produsul dintre el și 1."),
        q("De ce este mai rapid calculul 80 · 12 + 50 · 12 = 12 · (80 + 50)?", "Înlocuiește două înmulțiri cu o adunare și o înmulțire.", ["Schimbă valoarea expresiei.", "Elimină factorul 12.", "Transformă suma într-o diferență."], "Distributivitatea păstrează valoarea și reduce numărul operațiilor."),
    ])

    # Necunoscute și relații
    unknown = [
        ("Știind că x = 4, calculează (x + 1) · (2x + 11) · (3x − 7).", 475, "Factorii sunt 5, 19 și 5, deci produsul este 475.", [95, 375, 575]),
        ("Știind că y = 9, calculează (y + 5) · (2y − 4) · (3y + 3).", 5_880, "Factorii sunt 14, 14 și 30. Produsul este 14 · 14 · 30 = 5 880.", [4_880, 5_680, 6_880]),
        ("Știind că x = 5 și a + b = 13, calculează 3x + 7a + 7b.", 106, "3x + 7(a + b) = 15 + 91 = 106.", [96, 101, 111]),
        ("Știind că x = 5 și a + b = 13, calculează x(a + b) + 50.", 115, "x(a + b) + 50 = 5 · 13 + 50 = 115.", [65, 105, 125]),
        ("Determină x dacă a − b = 6 și x + 3a − 3b = 20.", 2, "3a − 3b = 3(a − b) = 18. Atunci x + 18 = 20, deci x = 2.", [1, 6, 14]),
        ("Determină x dacă a − b = 6 și 7a − 7b + x = 55.", 13, "7(a − b) + x = 42 + x = 55, deci x = 13.", [7, 42, 49]),
    ]
    for item in unknown:
        questions.append(nq(*item))

    # Probleme aplicate
    applied = [
        ("O echipă cumpără 12 tricouri la 80 lei și 12 șorturi la 50 lei. Cât costă echipamentul?", 1_560, "Pentru fiecare jucător costul este 80 + 50 = 130 lei. Pentru 12 jucători: 12 · 130 = 1 560 lei.", [1_440, 1_500, 1_680]),
        ("În 7 cutii sunt câte 12 borcane, iar în fiecare borcan sunt 9 bile. Câte bile sunt?", 756, "7 · 12 · 9 = 7 · 108 = 756.", [648, 728, 864]),
        ("Un biciclist merge 19 km în prima zi, de 4 ori mai mult în a doua, în a treia de 4 ori cât în primele două zile împreună, iar în ultima cu 5 km mai mult decât în a treia. Cât parcurge?", 860, "Zilele: 19, 76, 380 și 385 km. Totalul este 860 km.", [835, 855, 880]),
        ("Un penar are 9 pixuri a 5 lei, 5 creioane a 3 lei, două radiere a 2 lei și o ascuțitoare a 7 lei. Cât costă?", 71, "9 · 5 + 5 · 3 + 2 · 2 + 7 = 45 + 15 + 4 + 7 = 71 lei.", [67, 69, 74]),
        ("Un lot are 18 fete și 18 băieți. Fiecare primește un caiet de 7 lei și un pix de 3 lei. Care este costul total?", 360, "Sunt 36 elevi, iar un set costă 10 lei: 36 · 10 = 360 lei.", [180, 340, 380]),
        ("Un magazin pregătește 25 de pachete. Fiecare conține 4 caiete de 6 lei și 4 pixuri de 2 lei. Cât valorează toate pachetele?", 800, "Un pachet costă 4 · (6 + 2) = 32 lei. Toate costă 25 · 32 = 800 lei.", [600, 750, 850]),
    ]
    for item in applied:
        questions.append(nq(*item))

    # Raționament, cifre și șiruri
    reasoning = [
        ("Produsul a două numere este 414. Dacă mărim unul dintre factori cu 10, produsul devine 644. Care sunt factorii?", "23 și 18", ["21 și 19", "22 și 18", "23 și 20"], "Creșterea produsului este 230, adică 10 ori celălalt factor. Acesta este 23, iar 414 : 23 = 18."),
        ("Un factor este strict cuprins între 9 și 17, iar celălalt este cuprins între 11 și 22. Care este cel mai mic produs posibil?", "110", ["99", "121", "198"], "Cel mai mic prim factor este 10, iar al doilea este 11. Produsul minim este 110."),
        ("Care este cea mai mare valoare a produsului a două numere naturale cu suma 9?", "20", ["18", "21", "27"], "Factorii cât mai apropiați dau produs maxim: 4 · 5 = 20."),
        ("Dacă produsul numerelor naturale a și b este 72, care afirmație este sigur adevărată?", "Cel puțin unul dintre a și b este par.", ["Ambele sunt impare.", "Ambele au două cifre.", "Unul dintre ele este 9."], "Produsul a două numere impare ar fi impar, dar 72 este par."),
        ("Care poate fi ultima cifră a produsului a două numere naturale consecutive?", "6", ["1", "5", "9"], "Un produs de numere consecutive se poate termina cu 0, 2 sau 6; de exemplu 3 · 4 = 12 și 4 · 5 = 20, iar 7 · 8 = 56."),
        ("Care relație folosește greșit factorul comun?", "43 · 5 + 43 · 4 = 43 · (5 · 4)", ["28 · 7 + 28 · 12 = 28 · (7 + 12)", "121 · 9 − 121 = 121 · (9 − 1)", "8 · 5 + 8 · 6 − 8 = 8 · (5 + 6 − 1)"], "În paranteză trebuie păstrată adunarea: 43 · (5 + 4), nu înmulțirea."),
        ("Ce urmează în șirul 5, 15, 25, 35, ... dacă îl scriem folosind factor comun?", "45", ["40", "50", "55"], "Termenii sunt 5 · 1, 5 · 3, 5 · 5, 5 · 7; urmează 5 · 9 = 45."),
        ("Calculează rapid 702 · 65 + 35 · 702.", "70 200", ["7 020", "69 200", "70 902"], "Scoatem 702 factor comun: 702 · (65 + 35) = 702 · 100 = 70 200."),
        ("Dacă 24x + 24 · 15 = 24 · 40, cât este x?", "25", ["15", "24", "40"], "24 · (x + 15) = 24 · 40, deci x + 15 = 40 și x = 25."),
        ("Dacă 35 · 18 − 35x = 35 · 11, cât este x?", "7", ["6", "11", "29"], "35 · (18 − x) = 35 · 11, deci 18 − x = 11 și x = 7."),
        ("La un spectacol, 18 adulți și 18 copii cumpără fiecare câte un bilet. Biletul unui adult costă 30 lei, iar al unui copil 15 lei. Cât se încasează?", "810 lei", ["540 lei", "720 lei", "900 lei"], "Scoatem 18 factor comun: 18 · (30 + 15) = 18 · 45 = 810 lei."),
        ("Care expresie este sigur divizibilă cu 25?", "25 · 37 + 25 · 13", ["24 · 37 + 25 · 13", "25 · 37 + 13", "37 + 25 · 13"], "Expresia este 25 · (37 + 13), deci are factorul 25."),
    ]
    for text, correct, wrong, explanation in reasoning:
        questions.append(q(text, correct, wrong, explanation))

    # Construirea factorizării
    builders = [
        ("3 · 45 + 3 · 15", 3, [45, 15], ["+"], 180),
        ("20 · 48 + 20 · 2", 20, [48, 2], ["+"], 1_000),
        ("28 · 521 − 28 · 21", 28, [521, 21], ["−"], 14_000),
        ("12 · 13 + 12 · 15 + 12 · 72", 12, [13, 15, 72], ["+", "+"], 1_200),
        ("63 · 78 − 63 · 33 + 63 · 45", 63, [78, 33, 45], ["−", "+"], 5_670),
        ("2 413 · 1 001 − 2 413", 2_413, [1_001, 1], ["−"], 2_413_000),
        ("1 000 · 372 + 1 000 · 259 − 1 000 · 153", 1_000, [372, 259, 153], ["+", "−"], 478_000),
        ("125 · 234 − 125 · 28 + 125 · 194", 125, [234, 28, 194], ["−", "+"], 50_000),
    ]
    for expression, factor, terms, operators, result in builders:
        inner_expression = str(terms[0])
        for operator, term in zip(operators, terms[1:]):
            inner_expression += f" {operator} {term}"
        questions.append(iq(
            f"Construiește forma factorizată pentru {expression}.",
            "factor_builder",
            {"expression": expression, "common_factor": factor, "inner_terms": terms, "operators": operators, "result": result},
            f"Forma corectă este {factor} · ({inner_expression}), iar rezultatul este {fmt(result)}.",
        ))

    # Detectivul greșelilor
    error_sets = [
        (["43 · 5 + 43 · 4", "= 43 · (5 + 4)", "= 43 · 9", "= 387"], 3, "Toți pașii sunt corecți; în acest caz elevul trebuia să aleagă rezultatul corect."),
        (["28 · 7 + 28 · 12", "= 28 · (7 + 12)", "= 28 · 19", "= 512"], 3, "Ultimul calcul este greșit: 28 · 19 = 532."),
        (["121 · 9 − 121", "= 121 · (9 − 1)", "= 121 · 8", "= 968"], 3, "121 · 8 = 968; pașii afișați sunt corecți până la rezultat."),
        (["8 · 5 + 8 · 6 − 8", "= 8 · (5 + 6 − 1)", "= 8 · 10", "= 80"], 3, "Rezolvarea este corectă; ultimul pas confirmă rezultatul 80."),
        (["15 · 38 + 15 · 162", "= 15 · (38 + 162)", "= 15 · 100", "= 1 500"], 2, "38 + 162 este 200, nu 100."),
    ]
    # Primele, a treia și a patra sunt transformate în rezolvări cu o eroare discretă.
    error_sets[0] = (["43 · 5 + 43 · 4", "= 43 · (5 · 4)", "= 43 · 20", "= 860"], 1, "În paranteză trebuia păstrat semnul +: 43 · (5 + 4).")
    error_sets[2] = (["121 · 9 − 121", "= 121 · (9 − 1)", "= 121 · 10", "= 1 210"], 2, "9 − 1 = 8, nu 10.")
    error_sets[3] = (["8 · 5 + 8 · 6 − 8", "= 8 · (5 + 6 − 1)", "= 8 · 12", "= 96"], 2, "5 + 6 − 1 = 10, nu 12.")
    for steps, error_index, explanation in error_sets:
        questions.append(iq(
            f"În rezolvarea expresiei {steps[0]}, la ce pas apare prima greșeală?",
            "factor_error",
            {"steps": steps, "error_index": error_index},
            explanation,
        ))

    # Potrivirea formelor echivalente
    match_sets = [
        [
            ("7 · 18 + 7 · 12", "7 · (18 + 12)"),
            ("9 · 25 − 9 · 5", "9 · (25 − 5)"),
            ("4 · 16 + 4", "4 · (16 + 1)"),
        ],
        [
            ("12 · 8 + 12 · 2", "12 · (8 + 2)"),
            ("15 · 30 − 15 · 10", "15 · (30 − 10)"),
            ("25 · 3 + 25 · 7", "25 · (3 + 7)"),
        ],
        [
            ("6 · 14 + 6 · 5 − 6", "6 · (14 + 5 − 1)"),
            ("11 · 20 + 11 · 80", "11 · (20 + 80)"),
            ("32 · 9 − 32 · 4", "32 · (9 − 4)"),
        ],
        [
            ("100 · 27 + 100 · 73", "100 · (27 + 73)"),
            ("48 · 51 − 48", "48 · (51 − 1)"),
            ("13 · 6 + 13 · 14", "13 · (6 + 14)"),
        ],
        [
            ("125 · 16 − 125 · 8", "125 · (16 − 8)"),
            ("40 · 23 + 40 · 77", "40 · (23 + 77)"),
            ("72 · 5 + 72 · 4 + 72", "72 · (5 + 4 + 1)"),
        ],
    ]
    orders = [[2, 0, 1], [1, 2, 0], [2, 1, 0], [1, 0, 2], [0, 2, 1]]
    for pairs, order in zip(match_sets, orders):
        listed_expressions = "; ".join(left for left, _ in pairs)
        questions.append(iq(
            f"Potrivește fiecare expresie cu forma ei factorizată: {listed_expressions}.",
            "factor_match",
            {"pairs": [{"left": left, "right": right} for left, right in pairs], "right_order": order},
            "În fiecare pereche am scos în fața parantezei factorul care apare în toate produsele.",
        ))

    assert len(questions) == 53, len(questions)
    assert len({question["text"] for question in questions}) == len(questions)
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_operatii_factor_comun.json"
    payload = {
        "title": "Factor comun",
        "description": "Clasa a 5-a · Operații cu numere naturale",
        "difficulty": "medium",
        "questions": build_questions(),
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exercitii in {output.name}")


if __name__ == "__main__":
    main()
