"""Generează grilele lecției „Scăderea numerelor naturale”."""

import json
from pathlib import Path


def fmt(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def q(text, correct, wrong, explanation, points=10):
    correct = str(correct)
    wrong = [str(item) for item in wrong]
    assert len(wrong) == 3
    assert correct not in wrong
    assert len(set(wrong)) == 3
    return {
        "text": text,
        "points": points,
        "explanation": explanation,
        "options": [
            {"text": wrong[0], "is_correct": False},
            {"text": correct, "is_correct": True},
            {"text": wrong[1], "is_correct": False},
            {"text": wrong[2], "is_correct": False},
        ],
    }


def nq(text, answer, explanation, wrong=None):
    if wrong is None:
        candidates = [max(0, answer - 10), answer + 10, answer + 100]
        wrong = []
        for candidate in candidates:
            if candidate != answer and candidate not in wrong:
                wrong.append(candidate)
        candidate = answer + 1
        while len(wrong) < 3:
            if candidate != answer and candidate not in wrong:
                wrong.append(candidate)
            candidate += 1
    return q(text, fmt(answer), [fmt(item) for item in wrong], explanation)


def interactive_q(text, question_type, interactive, explanation, points=10):
    return {
        "text": text,
        "type": question_type,
        "points": points,
        "explanation": explanation,
        "interactive": interactive,
    }


def borrow_columns(minuend: int, subtrahend: int) -> list[bool]:
    width = len(str(minuend))
    top = [int(digit) for digit in str(minuend)]
    bottom = [int(digit) for digit in str(subtrahend).zfill(width)]
    borrows = [False] * width
    for index in range(width - 1, -1, -1):
        if top[index] >= bottom[index]:
            continue
        lender = index - 1
        while lender >= 0 and top[lender] == 0:
            top[lender] = 9
            borrows[lender] = True
            lender -= 1
        assert lender >= 0
        top[lender] -= 1
        top[index] += 10
        borrows[index] = True
    return borrows


def build_questions():
    questions = []

    # 1. Calcule directe
    direct = [
        (2_537, 1_322, [1_115, 1_205, 1_315]),
        (6_795, 3_063, [3_632, 3_832, 4_732]),
        (3_172, 2_183, [889, 999, 1_089]),
        (2_105, 1_537, [468, 578, 668]),
        (25_002, 7_279, [17_623, 17_823, 18_723]),
        (40_010, 17_073, [22_837, 23_037, 23_937]),
        (23_002, 8_792, [14_110, 14_310, 15_210]),
        (20_030, 15_086, [4_844, 5_044, 5_944]),
        (100_000, 45_678, [54_222, 54_422, 55_322]),
        (90_000, 8_999, [80_001, 81_101, 82_001]),
        (540_321, 98_765, [440_556, 442_556, 451_556]),
        (1_000_000, 345_678, [654_222, 655_322, 664_322]),
    ]
    for minuend, subtrahend, variants in direct[:5]:
        answer = minuend - subtrahend
        wrong = variants
        questions.append(
            nq(
                f"Calculați diferența {fmt(minuend)} − {fmt(subtrahend)}.",
                answer,
                f"{fmt(minuend)} − {fmt(subtrahend)} = {fmt(answer)}. Verificare: {fmt(answer)} + {fmt(subtrahend)} = {fmt(minuend)}.",
                wrong,
            )
        )

    # 2. Termen necunoscut
    unknown = [
        ("Dacă îl adunăm pe x cu 577, obținem 867. Cât este x?", 290, "x = 867 − 577 = 290."),
        ("Adunând 529 cu numărul natural x, obținem 630. Cât este x?", 101, "x = 630 − 529 = 101."),
        ("Dacă îl adunăm pe x cu 1 286, se obține 5 875. Cât este x?", 4_589, "x = 5 875 − 1 286 = 4 589."),
        ("Suma dintre x și 44 561 este 894 552. Determinați x.", 849_991, "x = 894 552 − 44 561 = 849 991."),
        ("Determinați x din egalitatea 247 + x = 783.", 536, "Termenul necunoscut este diferența dintre sumă și termenul cunoscut: x = 783 − 247 = 536."),
        ("Determinați x din egalitatea x + 318 = 2 467.", 2_149, "x = 2 467 − 318 = 2 149."),
        ("Determinați x din egalitatea 735 − x = 517.", 218, "Scăzătorul este diferența dintre descăzut și rezultat: x = 735 − 517 = 218."),
        ("Determinați x din egalitatea x − 482 = 267.", 749, "Descăzutul se obține adunând diferența cu scăzătorul: x = 267 + 482 = 749."),
        ("Determinați x din egalitatea 23 536 − x = 10 039.", 13_497, "x = 23 536 − 10 039 = 13 497."),
        ("Determinați x din egalitatea 873 − x = 243.", 630, "x = 873 − 243 = 630."),
        ("Determinați x din egalitatea x − 215 = 772.", 987, "x = 772 + 215 = 987."),
        ("Determinați x din egalitatea 7 815 − x + 737 = 3 511.", 5_041, "Grupăm termenii cunoscuți: 7 815 + 737 = 8 552. Apoi 8 552 − x = 3 511, deci x = 5 041."),
    ]
    for text, answer, explanation in unknown[:7]:
        questions.append(nq(text, answer, explanation))

    # 3. Ordinea operațiilor și paranteze
    parentheses = [
        ("Calculați 789 − 542 − 15.", 232, "Scăderile se efectuează de la stânga la dreapta: 789 − 542 = 247, apoi 247 − 15 = 232."),
        ("Calculați 1 299 − (234 − 199).", 1_264, "Mai întâi calculăm paranteza: 234 − 199 = 35. Apoi 1 299 − 35 = 1 264."),
        ("Calculați 16 801 − [5 622 − (1 240 − 559)].", 11_860, "1 240 − 559 = 681, apoi 5 622 − 681 = 4 941, iar 16 801 − 4 941 = 11 860."),
        ("Calculați 78 952 − (568 − 422) − (4 587 − 2 559).", 76_778, "Parantezele sunt 146 și 2 028. Atunci 78 952 − 146 − 2 028 = 76 778."),
        ("Calculați 5 000 − (1 250 + 750).", 3_000, "În paranteză avem 1 250 + 750 = 2 000, deci 5 000 − 2 000 = 3 000."),
        ("Calculați 7 200 − (1 800 − 600).", 6_000, "1 800 − 600 = 1 200, apoi 7 200 − 1 200 = 6 000."),
        ("Calculați 10 000 − (2 400 + 1 600) − 500.", 5_500, "2 400 + 1 600 = 4 000. Rezultă 10 000 − 4 000 − 500 = 5 500."),
        ("Calculați 8 500 − [1 200 + (900 − 400)].", 6_800, "900 − 400 = 500, apoi 1 200 + 500 = 1 700, iar 8 500 − 1 700 = 6 800."),
    ]
    for text, answer, explanation in parentheses[:5]:
        questions.append(nq(text, answer, explanation))

    # 4. Numere extreme și cifre
    extreme = [
        ("Calculați diferența dintre cel mai mare și cel mai mic număr de patru cifre identice.", 8_888, "Numerele sunt 9 999 și 1 111. Diferența este 9 999 − 1 111 = 8 888."),
        ("Calculați diferența dintre cel mai mare și cel mai mic număr de trei cifre distincte.", 885, "Cel mai mare este 987, iar cel mai mic este 102. Diferența este 987 − 102 = 885."),
        ("Calculați diferența dintre cel mai mare și cel mai mic număr de patru cifre distincte.", 8_853, "Cel mai mare este 9 876, iar cel mai mic este 1 023. Diferența este 8 853."),
        ("Calculați diferența dintre cel mai mare număr de patru cifre distincte și cel mai mic număr de trei cifre distincte.", 9_774, "Numerele sunt 9 876 și 102, iar 9 876 − 102 = 9 774."),
        ("Calculați diferența dintre cel mai mic număr de patru cifre identice și cel mai mare număr de trei cifre identice.", 112, "Numerele sunt 1 111 și 999. Diferența este 1 111 − 999 = 112."),
        ("Calculați diferența dintre cel mai mare număr par de patru cifre distincte și cel mai mic număr impar de trei cifre distincte.", 9_773, "Numerele sunt 9 876 și 103. Diferența este 9 876 − 103 = 9 773."),
    ]
    for text, answer, explanation in extreme[:4]:
        questions.append(nq(text, answer, explanation))
    questions.append(
        nq(
            "Câte numere de forma abcd verifică egalitatea abcd − b53 − 7 000 = 2 000, dacă b53 este număr de trei cifre?",
            9,
            "Egalitatea impune a = 9, c = 5 și d = 3. Cifra b poate fi oricare dintre 1, 2, ..., 9, deci există 9 numere.",
            [8, 10, 90],
        )
    )
    # 5. Probleme aplicate
    applied = [
        ("La nașterea lui Radu, tatăl său avea 28 de ani. Câți ani are Radu când tatăl său are 40 de ani?", 12, "Diferența de vârstă rămâne 28 de ani. Radu are 40 − 28 = 12 ani."),
        ("La nașterea lui Radu, tatăl său avea 28 de ani. Câți ani va avea tatăl când Radu va împlini 18 ani?", 46, "Tatăl este cu 28 de ani mai mare: 18 + 28 = 46."),
        ("Determinați numărul cu 176 mai mic decât suma numerelor 98 și 99.", 21, "98 + 99 = 197, iar 197 − 176 = 21."),
        ("Horia și Radu au împreună 794 lei, Radu și Clara au 676 lei, iar toți trei au 1 250 lei. Câți lei are Radu?", 220, "Clara are 1 250 − 794 = 456 lei. Atunci Radu are 676 − 456 = 220 lei."),
        ("Un autocar parcurge 349 km în prima zi, cu 52 km mai puțin în a doua zi, iar în a treia zi cu 276 km mai puțin decât în primele două zile la un loc. Câți kilometri are traseul?", 1_016, "A doua zi: 349 − 52 = 297 km. A treia zi: 349 + 297 − 276 = 370 km. Total: 349 + 297 + 370 = 1 016 km."),
        ("Suma a două numere naturale este 98, iar diferența lor este 82. Care este numărul mai mare?", 90, "Numărul mai mare este (98 + 82) : 2 = 90, iar cel mic este 8."),
        ("Suma a trei numere este 2 002. Dacă din fiecare se scade același număr, se obțin 175, 318 și 723. Ce număr s-a scăzut?", 262, "Suma rezultatelor este 1 216. S-au scăzut în total 2 002 − 1 216 = 786, adică de trei ori același număr. Numărul este 786 : 3 = 262."),
        ("Suma a trei numere este 2 002. Scăzând același număr din fiecare, obținem 175, 318 și 723. Care a fost cel mai mare număr inițial?", 985, "Numărul scăzut este 262. Cel mai mare număr inițial a fost 723 + 262 = 985."),
        ("O bibliotecă are 1 250 de cărți. După ce împrumută 378, apoi încă 245, câte cărți rămân?", 627, "În total s-au împrumutat 378 + 245 = 623 de cărți. Rămân 1 250 − 623 = 627."),
        ("O mamă are 37 de ani, iar copilul ei 9 ani. Care va fi diferența lor de vârstă peste 6 ani?", 28, "Diferența de vârstă nu se schimbă: 37 − 9 = 28 de ani."),
        ("Trei copii au împreună 2 000 lei. Primul și al doilea au 1 250 lei, iar al doilea și al treilea au 1 400 lei. Câți lei are al doilea copil?", 650, "Al treilea are 2 000 − 1 250 = 750 lei. Al doilea are 1 400 − 750 = 650 lei."),
        ("Un depozit avea 8 500 de cutii. În prima zi a trimis 2 340, iar în a doua cu 875 mai puține decât în prima. Câte cutii au rămas?", 4_695, "În a doua zi a trimis 2 340 − 875 = 1 465. Au rămas 8 500 − 2 340 − 1 465 = 4 695."),
    ]
    for text, answer, explanation in applied[:8]:
        questions.append(nq(text, answer, explanation))

    # 6. Relații între necunoscute
    algebra = [
        ("Știind că x + 2y = 24 și x + y = 19, determinați y.", 5, "Scădem a doua egalitate din prima: (x + 2y) − (x + y) = 24 − 19, deci y = 5."),
        ("Știind că 3x + 2y = 18 și 2x + 2y = 14, determinați x.", 4, "Scădem egalitățile: x = 18 − 14 = 4."),
        ("Știind că x + 2y + z = 17 și x + y = 10, determinați y + z.", 7, "Scădem a doua sumă din prima: y + z = 17 − 10 = 7."),
        ("Dacă a − b = 215 și b − c = 132, determinați a − c.", 347, "a − c = (a − b) + (b − c) = 215 + 132 = 347."),
        ("Dacă a − c = 138 și b − c = 129, determinați a − b.", 9, "Scădem cele două diferențe: (a − c) − (b − c) = a − b = 138 − 129 = 9."),
        ("Dacă a − b = 72 și (a − c) − (b + c) = 18, determinați c.", 27, "Expresia este a − b − 2c = 18. Cum a − b = 72, avem 72 − 2c = 18, deci 2c = 54 și c = 27."),
        ("Dacă a − b = 350 și b − c = 125, determinați a − c.", 475, "a − c = (a − b) + (b − c) = 350 + 125 = 475."),
        ("Dacă m − n = 84, cât este (m + 25) − (n + 25)?", 84, "Adăugarea aceluiași număr la ambii termeni nu schimbă diferența."),
    ]
    for text, answer, explanation in algebra[:6]:
        questions.append(nq(text, answer, explanation))

    # 7. Șiruri și calcule cu structură
    structured = [
        ("Calculați (10 + 15 + 20 + ... + 2 010) − (9 + 13 + 17 + ... + 1 609).", 80_601, "Ambele sume au 401 termeni. Diferențele termen cu termen sunt 1, 2, 3, ..., 401, iar suma lor este 401 · 402 : 2 = 80 601."),
        ("Calculați (10 + 20 + 30 + ... + 2 020) − (9 + 18 + 27 + ... + 1 818).", 20_503, "Fiecare sumă are 202 termeni. Diferența termenilor de același rang este 1 + 2 + ... + 202 = 202 · 203 : 2 = 20 503."),
        ("Calculați 400 000 + 40 000 + 4 000 + 400 + 40 + 4 − 3 − 30 − 300 − 3 000 − 30 000 − 300 000.", 111_111, "Prima grupă are suma 444 444, iar a doua 333 333. Diferența este 111 111."),
        ("Care este următorul termen al șirului 5 000, 4 875, 4 750, 4 625, ...?", 4_500, "La fiecare pas se scade 125. Așadar 4 625 − 125 = 4 500."),
        ("O mașină de calcul scade 275 din numărul introdus. Ce număr trebuie introdus pentru a obține 925?", 1_200, "Dacă x − 275 = 925, atunci x = 925 + 275 = 1 200."),
    ]
    for text, answer, explanation in structured[:4]:
        questions.append(nq(text, answer, explanation))

    # 8. Proprietăți, estimare și depistarea erorilor
    questions.extend(
        [
            q(
                "Care afirmație despre scăderea numerelor naturale este adevărată?",
                "a − 0 = a, pentru orice număr natural a",
                ["0 − a = a, pentru orice a", "a − a = a, pentru orice a", "a − b = b − a, pentru orice a și b"],
                "Scăderea lui 0 nu schimbă numărul: a − 0 = a.",
            ),
            q(
                "Care afirmație este falsă?",
                "Scăderea este comutativă: a − b = b − a",
                ["a − a = 0", "a − 0 = a", "Diferența se verifică adunând-o cu scăzătorul"],
                "Scăderea nu este comutativă. De exemplu, 8 − 3 = 5, dar 3 − 8 nu este număr natural.",
            ),
            q(
                "Dacă scădem același număr natural din descăzut și din scăzător, fără a ieși din numerele naturale, atunci:",
                "diferența rămâne aceeași",
                ["diferența se dublează", "diferența crește cu acel număr", "diferența devine întotdeauna 0"],
                "(a − k) − (b − k) = a − b, deoarece −k și +k se reduc.",
            ),
            q(
                "Dacă mărim descăzutul cu 25 și păstrăm același scăzător, ce se întâmplă cu diferența?",
                "Crește cu 25",
                ["Scade cu 25", "Rămâne aceeași", "Se dublează"],
                "(a + 25) − b = (a − b) + 25.",
            ),
            q(
                "Dacă mărim scăzătorul cu 40, iar descăzutul rămâne neschimbat, ce se întâmplă cu diferența?",
                "Scade cu 40",
                ["Crește cu 40", "Rămâne aceeași", "Crește de 40 de ori"],
                "a − (b + 40) = (a − b) − 40, dacă scăderea este posibilă în numere naturale.",
            ),
            q(
                "Care afirmație despre diferența unor numere de aceeași paritate este adevărată?",
                "Diferența a două numere de aceeași paritate este pară.",
                ["Diferența a două numere pare este impară.", "Diferența a două numere impare este impară.", "Diferența unui număr par și a unuia impar este pară."],
                "Par − par și impar − impar dau rezultate pare.",
            ),
            q(
                "Care afirmație despre diferența unor numere de parități diferite este adevărată?",
                "Diferența dintre un număr par și un număr impar este impară.",
                ["Este întotdeauna pară.", "Este întotdeauna 0.", "Nu poate fi stabilită."],
                "Numerele de parități diferite au o diferență impară, atunci când scăderea este posibilă.",
            ),
            nq(
                "Un elev a calculat 5 032 − 1 876 = 3 256. Care este rezultatul corect?",
                3_156,
                "Calculul corect este 5 032 − 1 876 = 3 156. Verificare: 3 156 + 1 876 = 5 032.",
                [3_056, 3_256, 4_156],
            ),
            q(
                "Fără a efectua calculul exact, care este cea mai bună estimare pentru 8 124 − 3 087?",
                "aproximativ 5 000",
                ["aproximativ 3 000", "aproximativ 8 000", "aproximativ 11 000"],
                "Rotunjim la mii: 8 124 ≈ 8 000 și 3 087 ≈ 3 000. Diferența estimată este 5 000.",
            ),
            q(
                "Cum verificăm corect egalitatea 9 432 − 3 217 = 6 215?",
                "6 215 + 3 217 = 9 432",
                ["9 432 + 3 217 = 6 215", "6 215 − 3 217 = 9 432", "9 432 + 6 215 = 3 217"],
                "La verificarea scăderii, adunăm diferența cu scăzătorul și trebuie să obținem descăzutul.",
            ),
        ][:7]
    )

    # 9. Exerciții interactive: scădere în coloană
    column_values = [
        (8_642, 3_217),
        (7_532, 2_418),
        (8_753, 2_864),
        (6_431, 2_785),
        (9_005, 4_237),
        (32_410, 17_685),
    ]
    for minuend, subtrahend in column_values:
        width = len(str(minuend))
        result = minuend - subtrahend
        questions.append(
            interactive_q(
                f"Așază scăderea în coloană și calculează {fmt(minuend)} − {fmt(subtrahend)}.",
                "column_subtraction",
                {
                    "minuend": str(minuend),
                    "subtrahend": str(subtrahend).zfill(width),
                    "correct_result": str(result).zfill(width),
                    "borrow_columns": borrow_columns(minuend, subtrahend),
                },
                f"Rezultatul este {fmt(result)}. Marcăm fiecare coloană în care am avut nevoie să împrumutăm o zece.",
            )
        )

    # 10. Exerciții interactive: cifre lipsă
    missing_values = [
        (734, 269, ["minuend:1", "subtrahend:1"]),
        (862, 347, ["minuend:2", "result:1"]),
        (5_421, 2_367, ["minuend:1", "subtrahend:2", "result:2"]),
        (9_005, 4_237, ["minuend:2", "subtrahend:1", "result:3"]),
        (7_812, 3_496, ["subtrahend:2", "result:1", "result:3"]),
        (32_410, 17_685, ["minuend:3", "subtrahend:1", "result:2"]),
    ]
    for minuend, subtrahend, missing in missing_values:
        width = len(str(minuend))
        result = minuend - subtrahend
        rows = {
            "minuend": str(minuend),
            "subtrahend": str(subtrahend).zfill(width),
            "result": str(result).zfill(width),
        }
        masked = dict(rows)
        for key in missing:
            row_name, raw_index = key.split(":")
            index = int(raw_index)
            masked[row_name] = masked[row_name][:index] + "□" + masked[row_name][index + 1:]
        questions.append(
            interactive_q(
                f"Completează scăderea {masked['minuend']} − {masked['subtrahend']} = {masked['result']}.",
                "missing_digits",
                {
                    "minuend": str(minuend),
                    "subtrahend": str(subtrahend).zfill(width),
                    "result": str(result).zfill(width),
                    "missing": missing,
                },
                f"Scăderea completă este {fmt(minuend)} − {fmt(subtrahend)} = {fmt(result)}.",
            )
        )

    # 11. Exerciții interactive: detectivul greșelilor
    error_values = [
        (5_032, 1_876, 3_256, 1),
        (8_425, 2_317, 6_118, 2),
        (9_764, 3_528, 6_235, 3),
        (7_500, 2_486, 5_114, 1),
        (6_342, 2_197, 4_045, 1),
        (32_410, 17_685, 14_735, 3),
    ]
    for minuend, subtrahend, shown_result, error_column in error_values:
        width = len(str(minuend))
        correct_result = minuend - subtrahend
        questions.append(
            interactive_q(
                f"Un elev a scris {fmt(minuend)} − {fmt(subtrahend)} = {fmt(shown_result)}, dar a greșit o singură cifră. Apasă coloana greșită.",
                "error_spotting",
                {
                    "minuend": str(minuend),
                    "subtrahend": str(subtrahend).zfill(width),
                    "shown_result": str(shown_result).zfill(width),
                    "correct_result": str(correct_result).zfill(width),
                    "error_column": error_column,
                },
                f"Rezultatul corect este {fmt(correct_result)}. Cifra greșită era în coloana indicată.",
            )
        )

    # 12. Exerciții interactive: paranteze pentru un rezultat dat
    parentheses_targets = [
        (["80", "− 30", "+ 10"], 1, 3, 40),
        (["90", "− 40", "+ 15"], 1, 3, 35),
        (["120", "− 35", "+ 25"], 1, 3, 60),
        (["150", "− 60", "− 10"], 1, 3, 100),
        (["250", "− 90", "− 60"], 1, 3, 220),
        (["500", "− 180", "+ 120"], 1, 3, 200),
    ]
    for tokens, open_index, close_index, target in parentheses_targets:
        expression = " ".join(tokens)
        questions.append(
            interactive_q(
                f"Trage parantezele în expresia {expression} astfel încât rezultatul să fie {fmt(target)}.",
                "parentheses_target",
                {
                    "tokens": tokens,
                    "correct_open_index": open_index,
                    "correct_close_index": close_index,
                    "target": target,
                },
                f"Parantezele se așază înaintea celui de-al doilea termen și după ultimul termen; expresia obținută are valoarea {fmt(target)}.",
            )
        )

    # 13. Exerciții interactive: mașina intrare–ieșire
    machine_values = [
        (275, [(1_200, None), (None, 625), (1_500, None)]),
        (125, [(900, None), (None, 475), (1_250, None)]),
        (340, [(1_000, None), (None, 860), (2_000, None)]),
        (1_025, [(2_500, None), (None, 975), (4_000, None)]),
        (2_350, [(7_000, None), (None, 3_900), (10_000, None)]),
        (4_075, [(9_500, None), (None, 5_925), (12_000, None)]),
    ]
    for value, raw_rows in machine_values:
        rows = [{"input": input_value, "output": output_value} for input_value, output_value in raw_rows]
        questions.append(
            interactive_q(
                f"Mașina scade {fmt(value)} din fiecare număr introdus. Completează toate căsuțele libere.",
                "input_output",
                {"operation": "subtract", "value": value, "rows": rows},
                "Pentru o ieșire lipsă scădem regula din intrare; pentru o intrare lipsă adunăm regula la ieșire.",
            )
        )

    assert len(questions) == 77, len(questions)
    assert len({item["text"] for item in questions}) == len(questions)
    return questions


def main():
    output = (
        Path(__file__).resolve().parent.parent
        / "clasa_5_operatii_scaderea_numerelor_naturale.json"
    )
    payload = {
        "title": "Scăderea numerelor naturale",
        "description": "Clasa a 5-a · Operații cu numere naturale",
        "difficulty": "easy",
        "questions": build_questions(),
    }
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Scrise {len(payload['questions'])} exercitii in {output.name}")


if __name__ == "__main__":
    main()
