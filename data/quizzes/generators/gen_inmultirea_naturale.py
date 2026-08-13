"""Generează lecția echilibrată despre înmulțirea numerelor naturale."""

import json
from pathlib import Path


def fmt(value):
    return f"{value:,}".replace(",", " ") if isinstance(value, int) else str(value)


def q(text, correct, wrong, explanation):
    correct = fmt(correct)
    wrong = [fmt(value) for value in wrong]
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3
    return {
        "text": text,
        "points": 10,
        "explanation": explanation,
        "options": [
            {"text": wrong[0], "is_correct": False},
            {"text": correct, "is_correct": True},
            {"text": wrong[1], "is_correct": False},
            {"text": wrong[2], "is_correct": False},
        ],
    }


def interactive_q(text, question_type, interactive, explanation):
    return {
        "text": text,
        "type": question_type,
        "points": 10,
        "explanation": explanation,
        "interactive": interactive,
    }


def multiplication_carries(multiplicand, multiplier):
    result = str(multiplicand * multiplier)
    source = str(multiplicand)
    carries = [False] * len(result)
    carry = 0
    offset = len(result) - len(source)
    for source_index in range(len(source) - 1, -1, -1):
        total = int(source[source_index]) * multiplier + carry
        carry = total // 10
        target_index = offset + source_index - 1
        if carry and target_index >= 0:
            carries[target_index] = True
    return carries


def build_questions():
    questions = []

    # Calcule de bază — doar câteva exemple reprezentative.
    for first, second, wrong in [
        (12, 35, [410, 430, 520]),
        (35, 25, [775, 825, 975]),
        (128, 45, [5_660, 5_750, 6_760]),
        (324, 15, [4_760, 4_850, 5_860]),
        (128, 204, [25_112, 26_012, 27_112]),
        (305, 207, [62_035, 63_125, 64_135]),
    ]:
        product = first * second
        questions.append(q(f"Calculați produsul {fmt(first)} · {fmt(second)}.", product, wrong, f"{fmt(first)} · {fmt(second)} = {fmt(product)}."))

    # Asociativitate și comutativitate.
    questions.extend([
        q("Calculați rapid 2 · 37 · 5.", 370, [185, 360, 740], "Grupăm 2 · 5 = 10, apoi 10 · 37 = 370."),
        q("Calculați rapid 25 · 17 · 4.", 1_700, [1_600, 1_725, 2_700], "25 · 4 = 100, iar 100 · 17 = 1 700."),
        q("Calculați rapid 250 · 2 · 4 · 5.", 10_000, [5_000, 8_000, 20_000], "250 · 4 = 1 000 și 2 · 5 = 10; produsul este 10 000."),
        q("Ce regrupare calculează cel mai rapid 16 · 25 · 14?", "(16 · 25) · 14", ["16 · (25 + 14)", "(16 + 25) · 14", "16 · (25 − 14)"], "16 · 25 = 400, apoi 400 · 14 = 5 600."),
        q("Care produs are aceeași valoare ca 18 · 7 · 5?", "18 · 5 · 7", ["18 · (7 + 5)", "18 · 7 + 5", "18 + 7 · 5"], "Comutativitatea permite schimbarea ordinii factorilor."),
    ])

    # Distributivitate și calcul mintal.
    questions.extend([
        q("Calculați 35 · 99 folosind 99 = 100 − 1.", 3_465, [3_365, 3_500, 3_535], "35 · 99 = 35 · 100 − 35 = 3 465."),
        q("Calculați 27 · 101.", 2_727, [2_627, 2_700, 2_827], "27 · 101 = 27 · 100 + 27 = 2 727."),
        q("Calculați 15 · 102.", 1_530, [1_500, 1_520, 1_630], "15 · 102 = 15 · 100 + 15 · 2 = 1 530."),
        q("Care expresie este egală cu 48 · 23?", "48 · 20 + 48 · 3", ["48 · 20 + 3", "48 + 20 · 3", "48 · 20 · 3"], "Aplicăm distributivitatea față de adunare: 48(20 + 3)."),
        q("Calculați 64 · 125 folosind o grupare convenabilă.", 8_000, [7_000, 8_125, 16_000], "64 · 125 = 8 · (8 · 125) = 8 · 1 000 = 8 000."),
    ])

    # Factori necunoscuți și cifre.
    questions.extend([
        q("Dacă 4 · (x + 11) = 60, cât este x?", 4, [3, 5, 11], "x + 11 = 15, deci x = 4."),
        q("Dacă 9 · (2y − 4) = 126, cât este y?", 9, [7, 8, 11], "2y − 4 = 14, deci 2y = 18 și y = 9."),
        q("Produsul a două numere este 414. Dacă un factor este 18, care este celălalt?", 23, [18, 22, 24], "414 : 18 = 23."),
        q("În numărul 2x34, produsul cifrelor este 24. Care este cifra x?", 4, [2, 3, 6], "2 · x · 3 · 4 = 24x = 96, deci x = 4."),
        q("Care este ultima cifră a produsului 32 · 34 · 37?", 6, [2, 4, 8], "Folosim ultimele cifre: 2 · 4 · 7 = 56, deci ultima cifră este 6."),
    ])

    # Probleme aplicate și de strategie.
    questions.extend([
        q("Un biciclist parcurge 19 km în prima zi, de 4 ori mai mult în a doua, de 3 ori mai mult decât în prima în a treia și de 5 ori mai mult decât în a treia în ultima zi. Câți kilometri parcurge în total?", 437, [418, 456, 513], "Zilele sunt 19, 76, 57 și 285 km; totalul este 437 km."),
        q("Într-un penar sunt 9 pixuri, 5 creioane, 2 radiere și o ascuțitoare. Pixul costă 5 lei, creionul 3 lei, radiera 2 lei, iar ascuțitoarea 7 lei. Cât costă penarul plin?", 71, [61, 69, 81], "9 · 5 + 5 · 3 + 2 · 2 + 7 = 71 lei."),
        q("Un factor este cuprins între 9 și 17, iar celălalt între 11 și 22. Care este cel mai mare produs posibil?", 374, [187, 352, 484], "Alegem factorii cei mai mari: 17 · 22 = 374."),
        q("Care este cel mai mare produs a două numere naturale cu suma 9?", 20, [18, 21, 24], "Factorii cât mai apropiați dau produsul maxim: 4 · 5 = 20."),
        q("Suma a două numere este 431 și 2a + 5b = 1 696. Care este b?", 278, [153, 263, 293], "Din a = 431 − b rezultă 862 + 3b = 1 696, deci b = 278."),
        q("Din 7 cutii, fiecare cu 12 borcane, iar fiecare borcan cu 9 bile, câte bile sunt în total?", 756, [108, 588, 864], "7 · 12 · 9 = 756."),
        q("Un dreptunghi are lungimea 24 m și lățimea de 3 ori mai mică. Care este aria lui?", 192, [64, 72, 576], "Lățimea este 24 : 3 = 8 m, iar aria este 24 · 8 = 192 m²."),
        q("O sală are 18 rânduri a câte 24 de locuri. La un spectacol rămân libere 37 de locuri. Câți spectatori sunt?", 395, [358, 405, 432], "Sala are 18 · 24 = 432 de locuri; 432 − 37 = 395 spectatori."),
    ])

    # Proprietăți și raționament — puține, dar diferite.
    questions.extend([
        q("Care afirmație este adevărată pentru orice număr natural a?", "a · 1 = a", ["a · 0 = a", "a · a = a", "a · 2 = a"], "Numărul 1 este elementul neutru al înmulțirii."),
        q("Dacă un factor este 0, produsul este:", 0, [1, "egal cu celălalt factor", "imposibil de stabilit"], "Orice număr înmulțit cu 0 dă 0."),
        q("Dacă a este par și b este impar, ce paritate are a · b?", "par", ["impar", "mereu 1", "imposibil de stabilit"], "Un factor par face produsul par."),
        q("Dacă produsul a · b este impar, atunci:", "a și b sunt amândoi impari", ["a și b sunt amândoi pari", "exact unul este par", "cel puțin unul este 0"], "Un produs este impar numai dacă ambii factori sunt impari."),
        q("Ultima cifră a produsului a două numere naturale consecutive poate fi:", "0, 2 sau 6", ["doar 4", "1, 3 sau 5", "doar 8"], "Produsele n(n+1) au ultima cifră posibilă 0, 2 sau 6."),
        q("Există un număr natural n pentru care n(n + 1) = 2 017?", "Nu", ["Da, n = 44", "Da, n = 45", "Da, n = 2017"], "44 · 45 = 1 980, iar 45 · 46 = 2 070; 2 017 este între ele."),
    ])

    # Înmulțire în coloană cu transport.
    for multiplicand, multiplier in [(128, 4), (305, 7), (246, 3), (412, 6), (125, 8), (1_024, 5)]:
        result = multiplicand * multiplier
        questions.append(interactive_q(
            f"Calculează în coloană produsul {fmt(multiplicand)} · {multiplier}.",
            "column_multiplication",
            {"multiplicand": str(multiplicand), "multiplier": str(multiplier), "correct_result": str(result), "carry_columns": multiplication_carries(multiplicand, multiplier)},
            f"Produsul este {fmt(result)}. Transporturile se obțin succesiv de la dreapta la stânga.",
        ))

    # Cifre lipsă în înmulțiri.
    missing_values = [
        (128, 4, ["factor1:1", "result:1"]),
        (305, 7, ["factor1:2", "result:2"]),
        (246, 3, ["factor1:1", "result:2"]),
        (35, 25, ["factor1:1", "factor2:1", "result:2"]),
        (48, 23, ["factor1:2", "factor2:2", "result:1"]),
        (125, 8, ["factor1:2", "result:1", "result:3"]),
    ]
    for number, (factor1, factor2, missing) in enumerate(missing_values, start=1):
        result = factor1 * factor2
        width = len(str(result))
        questions.append(interactive_q(
            f"Completează cifrele lipsă din înmulțirea în coloană, seria {number}.",
            "missing_digits",
            {"operation": "multiply", "factor1": str(factor1).zfill(width), "factor2": str(factor2).zfill(width), "result": str(result), "missing": missing},
            f"Înmulțirea completă este {fmt(factor1)} · {fmt(factor2)} = {fmt(result)}.",
        ))

    # Detectivul greșelilor.
    for factor1, factor2, shown, error_column in [
        (128, 4, 502, 1), (305, 7, 2_035, 1), (246, 3, 728, 1),
        (412, 6, 2_462, 2), (125, 8, 1_100, 1), (1_024, 5, 5_020, 1),
    ]:
        correct = factor1 * factor2
        width = len(str(correct))
        questions.append(interactive_q(
            f"Un elev a scris {fmt(factor1)} · {factor2} = {fmt(shown)}. Apasă coloana greșită.",
            "error_spotting",
            {"operation": "multiply", "factor1": str(factor1).zfill(width), "factor2": str(factor2).zfill(width), "shown_result": str(shown), "correct_result": str(correct), "error_column": error_column},
            f"Produsul corect este {fmt(correct)}.",
        ))

    # Paranteze care schimbă ordinea operațiilor.
    for tokens, open_index, close_index, target in [
        (["13", "+ 2", "· 5"], 0, 2, 75),
        (["19", "− 5", "· 3"], 1, 3, 4),
        (["24", "− 4", "· 6"], 0, 2, 120),
        (["7", "· 8", "+ 2"], 1, 3, 70),
        (["18", "+ 2", "· 4"], 0, 2, 80),
        (["100", "− 9", "· 8"], 1, 3, 28),
    ]:
        questions.append(interactive_q(
            f"Trage parantezele astfel încât rezultatul expresiei să fie {target}.",
            "parentheses_drag",
            {"tokens": tokens, "correct_open_index": open_index, "correct_close_index": close_index},
            f"Cu parantezele în pozițiile corecte, rezultatul este {target}.",
        ))

    # Mașini intrare–ieșire.
    for value, rows in [
        (3, [(12, None), (None, 45), (28, None)]),
        (4, [(25, None), (None, 144), (125, None)]),
        (5, [(48, None), (None, 625), (306, None)]),
        (7, [(32, None), (None, 700), (215, None)]),
        (11, [(45, None), (None, 1_353), (708, None)]),
        (25, [(16, None), (None, 2_500), (124, None)]),
    ]:
        questions.append(interactive_q(
            f"Mașina înmulțește cu {value}. Completează toate căsuțele libere.",
            "input_output",
            {"operation": "multiply", "value": value, "rows": [{"input": i, "output": o} for i, o in rows]},
            "Pentru ieșire înmulțim cu regula; pentru intrarea lipsă împărțim ieșirea la regulă.",
        ))

    assert len(questions) == 65, len(questions)
    assert len({item["text"] for item in questions}) == len(questions)
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_operatii_inmultirea_numerelor_naturale.json"
    payload = {
        "title": "Înmulțirea numerelor naturale, proprietăți",
        "description": "Clasa a 5-a · Operații cu numere naturale",
        "difficulty": "easy",
        "questions": build_questions(),
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exercitii in {output.name}")


if __name__ == "__main__":
    main()
