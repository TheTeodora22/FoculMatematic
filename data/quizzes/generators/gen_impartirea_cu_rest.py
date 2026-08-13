"""Generează lecția „Împărțirea cu rest a numerelor naturale” pentru clasa a V-a."""

import json
from pathlib import Path


def fmt(value):
    return f"{value:,}".replace(",", " ") if isinstance(value, int) else str(value)


def grid(text, correct, wrong, explanation):
    correct = fmt(correct)
    wrong = [fmt(value) for value in wrong]
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3
    return {
        "text": text, "format": "grid", "points": 10, "explanation": explanation,
        "options": [
            {"text": wrong[0], "is_correct": False},
            {"text": correct, "is_correct": True},
            {"text": wrong[1], "is_correct": False},
            {"text": wrong[2], "is_correct": False},
        ],
    }


def true_false(text, answer, explanation):
    return {
        "text": text, "format": "true_false", "points": 10, "explanation": explanation,
        "options": [
            {"text": "Adevărat", "is_correct": answer},
            {"text": "Fals", "is_correct": not answer},
        ],
    }


def interactive(text, question_type, data, explanation):
    return {
        "text": text, "type": question_type, "format": "interactive", "points": 10,
        "explanation": explanation, "interactive": data,
    }


def intermediate_remainders(dividend, divisor):
    result, current = [], 0
    for digit in str(dividend):
        current = current * 10 + int(digit)
        result.append(current % divisor)
        current %= divisor
    return result


def division_text(dividend, divisor):
    return f"câtul {dividend // divisor}, restul {dividend % divisor}"


def build_questions():
    questions = []

    # Calcul direct: suficient pentru fixarea algoritmului, fără serii repetitive.
    for dividend, divisor, wrong in [
        (104, 5, ["câtul 19, restul 9", "câtul 21, restul 1", "câtul 20, restul 5"]),
        (235, 7, ["câtul 32, restul 11", "câtul 34, restul 3", "câtul 33, restul 5"]),
        (566, 9, ["câtul 61, restul 17", "câtul 63, restul 1", "câtul 62, restul 9"]),
        (1_117, 12, ["câtul 92, restul 13", "câtul 94, restul 9", "câtul 93, restul 12"]),
        (2_141, 15, ["câtul 141, restul 26", "câtul 143, restul 6", "câtul 142, restul 15"]),
        (1_726, 11, ["câtul 155, restul 21", "câtul 157, restul 9", "câtul 156, restul 11"]),
    ]:
        quotient, remainder = divmod(dividend, divisor)
        questions.append(grid(
            f"Determinați câtul și restul împărțirii {fmt(dividend)} : {fmt(divisor)}.",
            division_text(dividend, divisor), wrong,
            f"{fmt(dividend)} = {fmt(divisor)} · {fmt(quotient)} + {fmt(remainder)}, iar {remainder} < {divisor}.",
        ))

    # Proba împărțirii și interpretarea corectă a relației D = Î × C + R.
    questions.extend([
        grid("Care este proba corectă pentru împărțirea 474 : 21, cu câtul 22 și restul 12?", "474 = 21 · 22 + 12", ["474 = 21 · 12 + 22", "474 = 21 · 22 − 12", "474 = 22 · 12 + 21"], "Proba este 21 · 22 + 12 = 474 și 12 < 21."),
        grid("Care egalitate descrie o împărțire cu rest corectă?", "99 = 17 · 5 + 14", ["36 = 7 · 4 + 8", "82 = 6 · 13 + 6", "55 = 5 · 10 + 5"], "În varianta corectă, egalitatea este adevărată și restul 14 este mai mic decât 17."),
        grid("În egalitatea 453 = 21 · 21 + 12, care este împărțitorul?", 21, [12, 22, 453], "În forma D = Î · C + R, împărțitorul este 21."),
        grid("În egalitatea 112 = 10 · 10 + 12, de ce nu avem o împărțire cu rest corectă?", "Restul nu este mai mic decât împărțitorul", ["Câtul este prea mic", "Deîmpărțitul trebuie să fie impar", "Împărțitorul trebuie să fie mai mare decât deîmpărțitul"], "Restul 12 nu poate fi rest la împărțirea la 10; trebuie să fie între 0 și 9."),
    ])

    # Gândire despre resturi.
    questions.extend([
        grid("Câte resturi diferite sunt posibile la împărțirea unui număr la 6?", 6, [5, 7, 12], "Resturile posibile sunt 0, 1, 2, 3, 4 și 5."),
        grid("Care sunt toate numerele naturale care, împărțite la 6, au câtul 13?", "78, 79, 80, 81, 82, 83", ["79, 80, 81, 82, 83, 84", "78, 79, 80, 81, 82", "78, 84, 90, 96, 102, 108"], "Numerele sunt 6 · 13 + r, unde r poate fi 0, 1, 2, 3, 4 sau 5."),
        grid("Care este cel mai mic număr natural de trei cifre care dă restul 8 la împărțirea la 11?", 107, [108, 118, 99], "107 = 11 · 9 + 8."),
        grid("Care este cel mai mare număr natural de trei cifre care dă restul 8 la împărțirea la 11?", 998, [988, 989, 999], "998 = 11 · 90 + 8."),
        grid("Care este suma tuturor resturilor posibile la împărțirea la 7?", 21, [7, 28, 49], "Resturile posibile sunt 0, 1, 2, 3, 4, 5, 6, cu suma 21."),
        grid("Un număr împărțit la 10 are câtul de două ori mai mare decât restul. Care este cel mai mic număr pozitiv posibil?", 21, [12, 20, 42], "Pentru restul 1, câtul este 2, deci numărul este 10 · 2 + 1 = 21."),
    ])

    # Probleme în contexte variate.
    questions.extend([
        grid("Radu împarte 44 de bomboane în mod egal la 7 prieteni. Câte bomboane îi rămân?", 2, [1, 5, 6], "44 = 7 · 6 + 2."),
        grid("130 de elevi merg în autocare cu câte 24 de locuri. Câte autocare sunt necesare pentru toți elevii?", 6, [5, 7, 10], "Se umplu 5 autocare și rămân 10 elevi, deci este necesar și al șaselea autocar."),
        grid("905 cărți sunt puse în cutii de câte 40. Câte cutii se umplu complet?", 22, [21, 23, 25], "905 = 40 · 22 + 25, deci 22 de cutii sunt pline."),
        grid("O panglică de 257 cm se taie în bucăți de câte 12 cm. Ce lungime rămâne netăiată?", "5 cm", ["4 cm", "11 cm", "17 cm"], "257 = 12 · 21 + 5."),
        grid("Un joc oferă o viață bonus la fiecare 9 monede. Din 76 de monede, câte rămân după obținerea tuturor vieților posibile?", 4, [3, 7, 8], "76 = 9 · 8 + 4."),
        grid("Un fermier pune 1 003 mere în lăzi de câte 35. Câte mere rămân în afara lăzilor complete?", 23, [18, 28, 33], "1 003 = 35 · 28 + 23."),
    ])

    # Adevărat/fals doar pentru ideile-cheie.
    questions.extend([
        true_false("Restul unei împărțiri poate fi egal cu împărțitorul.", False, "Restul trebuie să fie strict mai mic decât împărțitorul."),
        true_false("Dacă un număr dă restul 3 la împărțirea la 6, atunci este divizibil cu 3.", True, "Numărul are forma 6q + 3 = 3(2q + 1)."),
        true_false("Există un număr care dă restul 3 la împărțirea la 6 și restul 2 la împărțirea la 3.", False, "Orice număr de forma 6q + 3 este divizibil cu 3, deci are restul 0 la împărțirea la 3."),
        true_false("La împărțirea la 15, restul 14 este posibil.", True, "Orice rest de la 0 la 14 este posibil la împărțirea la 15."),
    ])

    # Împărțiri în coloană cu rest final nenul.
    for dividend, divisor in [(104, 5), (235, 7), (566, 9), (1_117, 12), (2_141, 15), (1_726, 11)]:
        quotient, remainder = divmod(dividend, divisor)
        questions.append(interactive(
            f"Efectuați în coloană împărțirea {fmt(dividend)} : {fmt(divisor)}.",
            "column_division",
            {"dividend": dividend, "divisor": divisor, "quotient": quotient, "remainder": remainder, "remainders": intermediate_remainders(dividend, divisor)},
            f"Câtul este {quotient}, iar restul final este {remainder}. Verificare: {divisor} · {quotient} + {remainder} = {fmt(dividend)}.",
        ))

    # Relația împărțirii: fiecare element poate lipsi, inclusiv restul.
    relation_rows = [
        (104, 5, 20, 4, "remainder"), (235, 7, 33, 4, "quotient"),
        (566, 9, 62, 8, "dividend"), (1_117, 12, 93, 1, "divisor"),
        (2_141, 15, 142, 11, "remainder"), (1_726, 11, 156, 10, "quotient"),
    ]
    for index, (dividend, divisor, quotient, remainder, missing) in enumerate(relation_rows, 1):
        questions.append(interactive(
            f"Completați valoarea lipsă din relația împărțirii cu rest, seria {index}.",
            "division_relation",
            {"dividend": dividend, "divisor": divisor, "quotient": quotient, "remainder": remainder, "missing": missing},
            f"Relația completă este {fmt(dividend)} = {divisor} · {quotient} + {remainder}.",
        ))

    # Tabele scurte: trei relații într-un singur exercițiu.
    table_sets = [
        [(104, 5, "quotient"), (235, 7, "remainder"), (566, 9, "dividend")],
        [(474, 21, "remainder"), (453, 22, "quotient"), (121, 10, "divisor")],
        [(1_117, 12, "quotient"), (2_141, 15, "remainder"), (1_726, 11, "dividend")],
        [(257, 12, "remainder"), (1_003, 35, "quotient"), (905, 40, "divisor")],
        [(82, 6, "dividend"), (998, 11, "quotient"), (107, 11, "remainder")],
        [(1_428, 49, "quotient"), (362, 72, "remainder"), (297, 17, "divisor")],
    ]
    for index, raw_rows in enumerate(table_sets, 1):
        rows = []
        for dividend, divisor, missing in raw_rows:
            quotient, remainder = divmod(dividend, divisor)
            rows.append({"dividend": dividend, "divisor": divisor, "quotient": quotient, "remainder": remainder, "missing": missing})
        questions.append(interactive(
            f"Completați celulele lipsă din tabelul împărțirii cu rest, seria {index}.",
            "division_table", {"rows": rows},
            "Pe fiecare rând folosim D = Î · C + R și verificăm R < Î.",
        ))

    # Probleme cu răspuns numeric: reconstrucție, resturi de expresii și raționament.
    numeric_problems = [
        ("Un număr împărțit la 49 are câtul 29 și restul 7. Determinați numărul.", 1_428, "", "Numărul este 49 · 29 + 7 = 1 428."),
        ("Un număr împărțit la 6 are câtul 13 și restul 4. Determinați numărul.", 82, "", "Numărul este 6 · 13 + 4 = 82."),
        ("Scrieți cel mai mic număr de trei cifre care dă restul 8 la împărțirea la 11.", 107, "", "107 = 11 · 9 + 8."),
        ("Scrieți cel mai mare număr de trei cifre care dă restul 8 la împărțirea la 11.", 998, "", "998 = 11 · 90 + 8."),
        ("Calculați suma tuturor resturilor posibile la împărțirea la 7.", 21, "", "0 + 1 + 2 + 3 + 4 + 5 + 6 = 21."),
        ("Dacă a și b sunt numere naturale, determinați restul împărțirii lui 17a + 17b + 25 la 17.", 8, "", "Termenii 17a și 17b se împart exact, iar 25 dă restul 8."),
        ("Dacă a și b sunt numere naturale, determinați restul împărțirii lui 16a + 28b + 13 la 4.", 1, "", "Primii doi termeni sunt multipli de 4, iar 13 dă restul 1."),
        ("Determinați restul împărțirii numărului 1 · 2 · 3 · … · 203 + 2 003 la 2 002.", 1, "", "Produsul conține factorul 2 002, iar 2 003 = 2 002 + 1."),
        ("Suma a trei numere este 121. Primul împărțit la al treilea dă câtul 10 și restul 5, iar al doilea dă câtul 5 și restul 4. Determinați al treilea număr.", 7, "", "Numerele sunt 10c + 5, 5c + 4 și c; din 16c + 9 = 121 obținem c = 7."),
        ("Suma a trei numere este 135. Primele două, împărțite la al treilea, dau câturile 12 și 31 și resturile 1 și 2. Determinați cel mai mare număr.", 95, "", "Al treilea este 3, iar primele două sunt 37 și 95."),
        ("Un număr este cu 72 mai mare decât altul. Suma lor împărțită la diferență dă câtul 5 și restul 2. Determinați numărul mai mic.", 145, "", "Suma este 72 · 5 + 2 = 362; numărul mic este (362 − 72) : 2 = 145."),
        ("Suma a trei numere este 297. Primul împărțit la al doilea dă câtul 2 și restul 25, iar la al treilea dă câtul 11 și restul 8. Determinați primul număr.", 195, "", "Din relații rezultă numerele 195, 85 și 17."),
    ]
    for text, answer, suffix, explanation in numeric_problems:
        questions.append(interactive(text, "numeric_input", {"answer": answer, "suffix": suffix}, explanation))

    assert len(questions) == 56, len(questions)
    assert len({question["text"] for question in questions}) == len(questions)
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_operatii_impartirea_numerelor_naturale.json"
    payload = {
        "title": "Împărțirea cu rest a numerelor naturale",
        "description": "Clasa a 5-a · Operații cu numere naturale",
        "difficulty": "medium",
        "questions": build_questions(),
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
