"""Generează lecția „Împărțirea cu rest 0” pentru clasa a V-a."""

import json
from pathlib import Path


def fmt(value):
    return f"{value:,}".replace(",", " ") if isinstance(value, int) else str(value)


def q(text, correct, wrong, explanation):
    correct, wrong = fmt(correct), [fmt(value) for value in wrong]
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3
    return {"text": text, "format": "grid", "points": 10, "explanation": explanation, "options": [
        {"text": wrong[0], "is_correct": False}, {"text": correct, "is_correct": True},
        {"text": wrong[1], "is_correct": False}, {"text": wrong[2], "is_correct": False},
    ]}


def tf(text, answer, explanation):
    return {"text": text, "format": "true_false", "points": 10, "explanation": explanation, "options": [
        {"text": "Adevărat", "is_correct": answer}, {"text": "Fals", "is_correct": not answer},
    ]}


def iq(text, question_type, interactive, explanation):
    return {"text": text, "type": question_type, "format": "interactive", "points": 10, "explanation": explanation, "interactive": interactive}


def remainders(dividend, divisor):
    result, current = [], 0
    for digit in str(dividend):
        current = current * 10 + int(digit)
        result.append(current % divisor)
        current %= divisor
    return result


def build_questions():
    questions = []

    # 5 grile de calcul direct, cu dificultăți diferite.
    for dividend, divisor, wrong in [
        (624, 4, [146, 154, 166]), (1_560, 65, [14, 25, 240]),
        (1_960, 70, [18, 27, 280]), (6_496, 112, [48, 56, 68]),
        (157_541, 257, [603, 6110, 621]),
    ]:
        quotient = dividend // divisor
        questions.append(q(f"Calculați câtul {fmt(dividend)} : {fmt(divisor)}.", quotient, wrong, f"{fmt(dividend)} : {fmt(divisor)} = {fmt(quotient)}, deoarece {fmt(quotient)} · {fmt(divisor)} = {fmt(dividend)}."))

    # Proba împărțirii și factor necunoscut.
    questions.extend([
        q("Care este proba corectă pentru 2 268 : 63 = 36?", "36 · 63 = 2 268", ["36 + 63 = 2 268", "2 268 · 63 = 36", "2 268 − 36 = 63"], "La împărțirea exactă, câtul înmulțit cu împărțitorul dă deîmpărțitul."),
        q("Știind că 47 160 : 72 = 655, ce calcul verifică rezultatul?", "655 · 72", ["655 + 72", "47 160 · 72", "47 160 − 655"], "Calculăm 655 · 72 și trebuie să obținem 47 160."),
        q("Care egalitate este echivalentă cu a : 19 = 34?", "a = 19 · 34", ["a = 34 : 19", "a = 34 − 19", "a = 19 + 34"], "Deîmpărțitul este produsul dintre împărțitor și cât."),
        q("Dacă x : 35 = 28, cât este x?", 980, [63, 805, 1_225], "x = 35 · 28 = 980."),
        q("Dacă 4 860 : x = 45, cât este x?", 108, [45, 98, 135], "x = 4 860 : 45 = 108."),
        q("Numărul 742 împărțit la un număr dă câtul 53. Care este împărțitorul?", 14, [7, 13, 53], "Împărțitorul este 742 : 53 = 14."),
        q("Câtul numerelor 13 500 și 125 este:", 108, [98, 105, 118], "13 500 : 125 = 108."),
    ])

    # Adevărat sau fals — doar proprietăți care merită reținute.
    questions.extend([
        tf("La o împărțire exactă, deîmpărțitul este egal cu împărțitorul înmulțit cu câtul.", True, "Relația este D = Î · C."),
        tf("Dacă 960 : 12 = 80, atunci 960 : (12 · 5) = 80 · 5.", False, "Mărirea împărțitorului de 5 ori micșorează câtul de 5 ori: rezultatul este 16."),
        tf("Egalitatea 646 : 19 + 361 : 19 = (646 + 361) : 19 este corectă.", True, "Ambele membre sunt 53; împărțirea este distributivă față de adunare când termenii se împart exact."),
        tf("Împărțirea numerelor naturale este comutativă.", False, "De exemplu, 12 : 3 = 4, dar 3 : 12 nu are cât natural exact."),
    ])

    # Probleme aplicate — contexte diferite.
    questions.extend([
        q("4 860 kg de cartofi sunt puse egal în 108 lăzi. Câte kilograme sunt în fiecare ladă?", 45, [35, 54, 108], "4 860 : 108 = 45 kg."),
        q("Un club cumpără echipament identic pentru 78 de elevi și plătește 6 396 lei. Cât costă un echipament?", 82, [72, 78, 92], "6 396 : 78 = 82 lei."),
        q("La o cantină, 18 kg de salam costă 414 lei. Cât costă un kilogram?", 23, [18, 22, 24], "414 : 18 = 23 lei."),
        q("40 de cutii conțin împreună 1 120 de pachete. Câte pachete sunt într-o cutie?", 28, [24, 30, 40], "1 120 : 40 = 28."),
        q("Un depozit are 75 de cutii, fiecare cu 5 flacoane. Acestea se împart egal la 25 de farmacii. Câte flacoane primește o farmacie?", 15, [3, 25, 75], "Sunt 75 · 5 = 375 flacoane, iar 375 : 25 = 15."),
        q("O carte are 336 de pagini. Mara citește același număr de pagini în fiecare zi și termină în 14 zile. Câte pagini citește zilnic?", 24, [14, 22, 28], "336 : 14 = 24 pagini."),
        q("O fabrică ambalează 2 940 de biscuiți în pachete de câte 35. Câte pachete obține?", 84, [74, 80, 94], "2 940 : 35 = 84."),
        q("Un traseu de 1 872 km este parcurs în 24 de etape egale. Câți kilometri are o etapă?", 78, [68, 72, 88], "1 872 : 24 = 78 km."),
    ])

    # 1. Împărțire în coloană.
    for dividend, divisor in [(624, 4), (735, 35), (1_560, 65), (6_496, 112)]:
        questions.append(iq(f"Efectuați în coloană împărțirea {fmt(dividend)} : {fmt(divisor)}.", "column_division", {"dividend": dividend, "divisor": divisor, "quotient": dividend // divisor, "remainders": remainders(dividend, divisor)}, f"Câtul este {fmt(dividend // divisor)}, iar ultimul rest este 0."))

    # 2. Cifre lipsă.
    for number, (dividend, divisor, missing) in enumerate([
        (624, 4, ["dividend:1", "quotient:1"]), (735, 35, ["divisor:1", "quotient:2"]),
        (1_560, 65, ["dividend:2", "divisor:2", "quotient:3"]), (42_000, 100, ["dividend:1", "quotient:3"]),
    ], 1):
        quotient, width = dividend // divisor, len(str(dividend))
        questions.append(iq(f"Completați cifrele lipsă din împărțirea exactă, seria {number}.", "missing_digits", {"operation": "divide", "dividend": str(dividend).zfill(width), "divisor": str(divisor).zfill(width), "quotient": str(quotient).zfill(width), "missing": missing}, f"Împărțirea completă este {fmt(dividend)} : {fmt(divisor)} = {fmt(quotient)}."))

    # 3. Detectivul greșelilor.
    for dividend, divisor, shown, column in [(624, 4, 166, 1), (1_560, 65, 34, 2), (644, 28, 33, 1), (2_268, 63, 26, 2)]:
        quotient, width = dividend // divisor, len(str(dividend))
        questions.append(iq(f"Un elev a scris {fmt(dividend)} : {fmt(divisor)} = {shown}. Apăsați coloana greșită.", "error_spotting", {"operation": "divide", "dividend": str(dividend).zfill(width), "divisor": str(divisor).zfill(width), "shown_result": str(shown).zfill(width), "correct_result": str(quotient).zfill(width), "error_column": column}, f"Câtul corect este {fmt(quotient)}."))

    # 4. Relația împărțirii.
    for number, (dividend, divisor, missing) in enumerate([(2_268, 63, "quotient"), (4_860, 108, "divisor"), (742, 14, "dividend"), (13_500, 125, "quotient")], 1):
        questions.append(iq(f"Completați valoarea lipsă din relația împărțirii, seria {number}.", "division_relation", {"dividend": dividend, "divisor": divisor, "quotient": dividend // divisor, "missing": missing}, "Deîmpărțitul = împărțitor × cât."))

    # 7. Mașină „împarte la”.
    for value, rows in [(4, [(624, None), (None, 200), (1_440, None)]), (7, [(735, None), (None, 112), (2_450, None)]), (12, [(960, None), (None, 125), (2_016, None)]), (25, [(2_500, None), (None, 84), (4_500, None)])]:
        questions.append(iq(f"Mașina împarte la {value}. Completați căsuțele.", "input_output", {"operation": "divide", "value": value, "rows": [{"input": i, "output": o} for i, o in rows]}, "Pentru ieșire împărțim; pentru intrarea lipsă înmulțim ieșirea cu regula."))

    # 13. Lanțuri de operații.
    chains = [
        (1_800, [("divide", 12), ("multiply", 5), ("subtract", 50)]),
        (2_400, [("divide", 8), ("add", 75), ("divide", 5)]),
        (6_300, [("divide", 7), ("divide", 9), ("multiply", 4)]),
        (4_800, [("divide", 16), ("add", 60), ("divide", 6)]),
    ]
    for number, (start, raw_steps) in enumerate(chains, 1):
        current, steps = start, []
        for operation, value in raw_steps:
            current = {"divide": current // value, "multiply": current * value, "add": current + value, "subtract": current - value}[operation]
            steps.append({"operation": operation, "value": value, "result": current})
        questions.append(iq(f"Completați toate rezultatele din lanțul de operații, seria {number}.", "operation_chain", {"start": start, "steps": steps}, "Efectuăm operațiile succesiv, de la stânga la dreapta."))

    # 15. Tabelul împărțirii.
    table_sets = [
        [(624, 4, "quotient"), (735, 35, "divisor"), (1_560, 65, "dividend")],
        [(2_268, 63, "quotient"), (4_860, 108, "divisor"), (742, 14, "dividend")],
        [(6_496, 112, "quotient"), (2_940, 35, "divisor"), (1_872, 24, "dividend")],
        [(42_000, 100, "quotient"), (13_500, 125, "divisor"), (1_120, 40, "dividend")],
    ]
    for number, rows in enumerate(table_sets, 1):
        questions.append(iq(f"Completați celulele lipsă din tabelul {number}.", "division_table", {"rows": [{"dividend": d, "divisor": v, "quotient": d // v, "missing": m} for d, v, m in rows]}, "Pe fiecare rând folosim relația D = Î · C."))

    # 17. Distribuire egală — răspuns direct.
    for text, answer, suffix, explanation in [
        ("4 860 kg de cartofi se distribuie egal în 108 lăzi. Câte kilograme intră într-o ladă?", 45, "kg", "4 860 : 108 = 45."),
        ("6 396 de lei reprezintă costul a 78 de echipamente identice. Cât costă unul?", 82, "lei", "6 396 : 78 = 82."),
        ("2 940 de biscuiți se pun câte 35 într-un pachet. Câte pachete se obțin?", 84, "pachete", "2 940 : 35 = 84."),
        ("1 872 km se împart în 24 de etape egale. Câți kilometri are o etapă?", 78, "km", "1 872 : 24 = 78."),
    ]:
        questions.append(iq(text, "numeric_input", {"answer": answer, "suffix": suffix}, explanation))

    # 19. Prețul unei bucăți.
    for product, quantity, total in [("felicitare de naștere", 225, 900), ("felicitare pentru prieten", 120, 360), ("card de mulțumire", 96, 384), ("card aniversar", 76, 228)]:
        questions.append(iq(f"Pentru {quantity} bucăți din produsul «{product}» s-au plătit {total} lei. Cât costă o bucată?", "numeric_input", {"answer": total // quantity, "suffix": "lei"}, f"{total} : {quantity} = {total // quantity} lei."))

    assert len(questions) == 60, len(questions)
    assert len({item["text"] for item in questions}) == len(questions)
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_operatii_impartirea_cu_rest.json"
    payload = {"title": "Împărțirea numerelor naturale cu rest 0", "description": "Clasa a 5-a · Operații cu numere naturale", "difficulty": "easy", "questions": build_questions()}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exercitii in {output.name}")


if __name__ == "__main__":
    main()
