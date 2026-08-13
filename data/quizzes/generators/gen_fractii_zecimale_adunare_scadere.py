"""Generează lecția despre adunarea și scăderea fracțiilor zecimale."""

import json
from decimal import Decimal
from pathlib import Path


def iq(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10, "interactive": data, "explanation": explanation}


def grid(text, correct, wrong, explanation):
    return {"text": text, "format": "grid", "points": 10, "explanation": explanation, "options": [
        {"text": str(wrong[0]), "is_correct": False}, {"text": str(correct), "is_correct": True},
        {"text": str(wrong[1]), "is_correct": False}, {"text": str(wrong[2]), "is_correct": False},
    ]}


def decimal_text(value, places=None):
    number = Decimal(str(value).replace(",", "."))
    if places is None:
        text = format(number, "f").rstrip("0").rstrip(".")
    else:
        text = f"{number:.{places}f}"
    return text.replace(".", ",")


def aligned_digits(a, b, operation):
    da, db = Decimal(a.replace(",", ".")), Decimal(b.replace(",", "."))
    places = max(len(a.split(",")[1]) if "," in a else 0, len(b.split(",")[1]) if "," in b else 0)
    scale = 10 ** places
    ia, ib = int(da * scale), int(db * scale)
    result = ia + ib if operation == "add" else ia - ib
    width = max(len(str(ia)), len(str(ib)), len(str(result)), places + 1)
    return str(ia).zfill(width), str(ib).zfill(width), str(result).zfill(width), places


def carries(a, b):
    result, carry = [False] * len(a), 0
    for index in range(len(a) - 1, -1, -1):
        carry = 1 if int(a[index]) + int(b[index]) + carry >= 10 else 0
        if carry and index > 0:
            result[index - 1] = True
    return result


def borrows(a, b):
    top, bottom, result = list(map(int, a)), list(map(int, b)), [False] * len(a)
    for index in range(len(top) - 1, -1, -1):
        if top[index] >= bottom[index]:
            continue
        lender = index - 1
        while lender >= 0 and top[lender] == 0:
            top[lender] = 9
            result[lender] = True
            lender -= 1
        top[lender] -= 1
        top[index] += 10
        result[index] = True
    return result


def column(a, b, operation, label):
    first, second, result, places = aligned_digits(a, b, operation)
    answer = decimal_text(Decimal(a.replace(",", ".")) + Decimal(b.replace(",", ".")) if operation == "add" else Decimal(a.replace(",", ".")) - Decimal(b.replace(",", ".")), places)
    data = {"decimal_places": places, "correct_result": result}
    if operation == "add":
        data.update({"addend1": first, "addend2": second, "carry_columns": carries(first, second)})
        kind, verb = "column_addition", "Adună"
    else:
        data.update({"minuend": first, "subtrahend": second, "borrow_columns": borrows(first, second)})
        kind, verb = "column_subtraction", "Scade"
    return iq(f"{verb} în coloană {a} {'+' if operation == 'add' else '−'} {b} ({label}).", kind, data, f"Aliniem virgulele și completăm cu zerouri dacă este nevoie. Rezultatul este {answer}.")


def direct(expression, answer, label):
    answers = {"missing": answer}
    return iq(f"Calculează expresia zecimală {label}.", "decimal_workbench", {"mode": "missing", "expression": expression, "fields": [{"key": "missing", "label": "Rezultatul"}], "answers": answers}, f"Respectăm ordinea operațiilor și aliniem zecimalele. Rezultatul este {answer}.")


def error(label, steps, error_index, explanation):
    return iq(f"Detectivul greșelilor {label}: apasă primul pas greșit.", "divisibility_error", {"steps": steps, "error_index": error_index}, explanation)


def problem(text, expression, answer, explanation):
    answers = {"missing": answer}
    return iq(text, "decimal_workbench", {"mode": "missing", "expression": expression, "fields": [{"key": "missing", "label": "Răspuns"}], "answers": answers}, explanation)


def build_questions():
    q = []
    for row in [
        ("0,28", "0,69", "add", "A"), ("10,3", "4,5", "add", "B"),
        ("24,25", "0,97", "add", "C"), ("75,468", "256,309", "add", "D"),
        ("0,44", "29,107", "add", "E"), ("2,3", "8,5", "add", "F"),
        ("12,7", "5,8", "subtract", "G"), ("14,75", "1,26", "subtract", "H"),
        ("0,4853", "0,2178", "subtract", "I"), ("43,256", "21,8", "subtract", "J"),
        ("3,60", "2,18", "subtract", "K"), ("218,00", "12,45", "subtract", "L"),
    ]:
        q.append(column(*row))

    q += [
        direct("2,3 + 8,5", "10,8", "A"),
        direct("17,5 + 32,32 + 10", "59,82", "B"),
        direct("11,05 + 4,275 + 90", "105,325", "C"),
        direct("13,5 + 2,7 − 6,8", "9,4", "D"),
        direct("456,258 − 208,208 + 54,65", "302,7", "E"),
        direct("18,3458 − 6,0059 + 10,203", "22,5429", "F"),
    ]

    q += [
        error("A", ["Scriem 10,3 deasupra lui 4,5", "Aliniem virgulele", "Calculăm 103 + 45 = 148", "Rezultatul este 1,48"], 3, "După alinierea zecimalelor, 10,3 + 4,5 = 14,8."),
        error("B", ["Pentru 3,60 − 2,18 adăugăm un zero", "Scădem 360 − 218 = 142", "Așezăm virgula: 14,2"], 2, "Sunt două zecimale, deci rezultatul este 1,42."),
        error("C", ["14,75 − 1,26", "Scădem sutimile: 5 − 6 = 1", "Este nevoie de împrumut la sutimi", "Rezultatul corect este 13,49"], 1, "Nu putem calcula 5 − 6 fără împrumut; acesta este primul pas greșit."),
        error("D", ["0,44 + 29,107", "Scriem 0,440 + 29,107", "Adunăm 440 + 29107 = 29447", "Rezultatul este 29,447"], 2, "440 + 29107 = 29547, deci suma corectă este 29,547."),
    ]

    q += [
        problem("Într-un depozit sunt 126,75 t de făină și se aduc încă 24,5 t. Câte tone sunt acum?", "126,75 + 24,5 = □", "151,25", "126,75 + 24,50 = 151,25 t."),
        problem("La aprozar erau 29,72 kg de lămâi și s-au vândut 14,35 kg. Câte kilograme au rămas?", "29,72 − 14,35 = □", "15,37", "Rămân 15,37 kg."),
        problem("Dintr-un balot de 34,5 m s-au vândut 14,15 m, apoi cu 2,7 m mai puțin. Cât a rămas?", "34,5 − 14,15 − (14,15 − 2,7) = □", "8,9", "În ziua a doua s-au vândut 11,45 m; au rămas 8,9 m."),
        problem("Un biciclist parcurge 21,25 km, apoi cu 7,3 km mai mult, iar în ziua a treia cu 10 km mai puțin decât în a doua zi. Cât parcurge în total?", "21,25 + 28,55 + 18,55 = □", "68,35", "Distanța totală este 68,35 km."),
        problem("Un joc costă 41,35 lei. Ce rest primești din 50 de lei?", "50 − 41,35 = □", "8,65", "Restul este 8,65 lei."),
        problem("Cumperi un tricou de 24,75 lei și o pereche de mănuși de 23,48 lei. Cât plătești?", "24,75 + 23,48 = □", "48,23", "Plătești 48,23 lei."),
    ]

    q += [
        direct("a,b + b,a = 2,2; determină a + b", "2", "G"),
        direct("43,1 + 3,9 − 1,2", "45,8", "H"),
        direct("5,71 + 12,91 − 7,52", "11,1", "I"),
    ]

    q += [
        grid("Rezultatul calculului 13,5 + 7,32 este:", "20,82", ["6,18", "8,67", "20,35"], "13,50 + 7,32 = 20,82."),
        grid("Rezultatul calculului 1,73 − 1,56 este:", "0,17", ["1,17", "3,29", "2,17"], "1,73 − 1,56 = 0,17."),
        grid("Restul primit din 100 lei pentru o cumpărătură de 79,85 lei este:", "20,15 lei", ["21,15 lei", "20,25 lei", "19,15 lei"], "100,00 − 79,85 = 20,15."),
    ]
    assert len(q) == 34, len(q)
    return q


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_fractii_zecimale_adunarea_si_scaderea.json"
    payload = {"title": "Adunarea și scăderea fracțiilor zecimale cu un număr finit de zecimale nenule", "description": "Clasa a 5-a · Fracții zecimale", "difficulty": "medium", "questions": build_questions()}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
