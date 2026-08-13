"""Generează lecția despre înmulțirea fracțiilor zecimale finite."""

import json
from decimal import Decimal
from pathlib import Path


def interactive(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10, "interactive": data, "explanation": explanation}


def grid(text, correct, wrong, explanation):
    return {"text": text, "format": "grid", "points": 10, "explanation": explanation, "options": [
        {"text": wrong[0], "is_correct": False}, {"text": correct, "is_correct": True},
        {"text": wrong[1], "is_correct": False}, {"text": wrong[2], "is_correct": False},
    ]}


def decimal_places(value):
    return len(value.split(",")[1]) if "," in value else 0


def plain_digits(value):
    return value.replace(",", "").lstrip("0") or "0"


def carries(multiplicand, multiplier, result_width):
    answer = [False] * result_width
    carry = 0
    offset = result_width - len(multiplicand)
    for index in range(len(multiplicand) - 1, -1, -1):
        total = int(multiplicand[index]) * int(multiplier) + carry
        carry = total // 10
        target = offset + index - 1
        if carry and target >= 0:
            answer[target] = True
    return answer


def display_decimal(digits, places):
    digits = digits.zfill(places + 1)
    if not places:
        return str(int(digits))
    return f"{digits[:-places]},{digits[-places:]}"


def column(value, multiplier, label):
    first_places = decimal_places(value)
    first = plain_digits(value)
    result = str(int(first) * multiplier)
    width = max(len(first), len(result), first_places + 1)
    first = first.zfill(width)
    result = result.zfill(width)
    data = {
        "multiplicand": first,
        "multiplier": str(multiplier),
        "correct_result": result,
        "carry_columns": carries(first, str(multiplier), width),
        "multiplicand_decimal_places": first_places,
        "multiplier_decimal_places": 0,
        "decimal_places": first_places,
    }
    answer = display_decimal(result, first_places)
    place_word = "cifră" if first_places == 1 else "cifre"
    return interactive(
        f"Înmulțește în coloană {value} × {multiplier} ({label}).",
        "column_multiplication", data,
        f"Înmulțim cifrele ca la numere naturale, apoi punem virgula la {first_places} {place_word} de la dreapta. Rezultatul este {answer}.",
    )


def direct(expression, answer, label, explanation=None):
    return interactive(
        f"Calculează expresia {label}.", "decimal_workbench",
        {"mode": "missing", "expression": expression, "fields": [{"key": "missing", "label": "Rezultatul"}], "answers": {"missing": answer}},
        explanation or f"Calculăm atent produsul și poziția virgulei. Rezultatul este {answer}.",
    )


def problem(text, expression, answer, explanation):
    return interactive(text, "decimal_workbench", {"mode": "missing", "expression": expression, "fields": [{"key": "missing", "label": "Răspuns"}], "answers": {"missing": answer}}, explanation)


def detective(label, steps, error_index, explanation):
    return interactive(f"Detectivul greșelilor {label}: apasă primul pas greșit.", "divisibility_error", {"steps": steps, "error_index": error_index}, explanation)


def build_questions():
    questions = []

    for row in [
        ("1,5", 6, "A"), ("2,75", 3, "B"), ("24,21", 7, "C"), ("8,00", 4, "D"),
        ("44,32", 5, "E"), ("72,56", 5, "F"), ("14,052", 8, "G"), ("7,29", 7, "H"),
    ]:
        questions.append(column(*row))

    questions += [
        direct("2,3 × 10", "23", "A", "La înmulțirea cu 10, virgula se mută cu un loc la dreapta: 23."),
        direct("1,73 × 10", "17,3", "B", "Virgula se mută cu un loc la dreapta: 17,3."),
        direct("0,03 × 100", "3", "C", "La înmulțirea cu 100, virgula se mută două locuri la dreapta: 3."),
        direct("12,51 × 100", "1251", "D", "Mutăm virgula două locuri la dreapta: 1251."),
        direct("0,253 × 1000", "253", "E", "Mutăm virgula trei locuri la dreapta: 253."),
        direct("4,20035 × 10000", "42003,5", "F", "Mutăm virgula patru locuri la dreapta: 42003,5."),
        direct("0,002 × 10000", "20", "G", "Mutăm virgula patru locuri la dreapta: 20."),
    ]

    questions += [
        direct("0,7 × 10 × 3,8", "26,6", "H"),
        direct("0,431 × 8 × 2,56", "8,82688", "I"),
        direct("3,7 × (2,59 + 2,41)", "18,5", "J", "Mai întâi calculăm paranteza: 2,59 + 2,41 = 5, apoi 3,7 × 5 = 18,5."),
        direct("6,12 × (4,23 − 4,03)", "1,224", "K", "Diferența din paranteză este 0,20, iar 6,12 × 0,20 = 1,224."),
        direct("2 × 0,1 × 5", "1", "L", "Grupăm 2 × 5 = 10, apoi 10 × 0,1 = 1."),
        direct("6,12 × 5,93 × (78,124 + 21,876)", "3629,16", "M", "Paranteza este 100; apoi 6,12 × 5,93 × 100 = 3629,16."),
    ]

    questions += [
        detective("A", ["Pentru 4,5 × 3,7 eliminăm temporar virgulele", "Calculăm 45 × 37 = 1665", "Factorii au împreună două zecimale", "Produsul este 166,5"], 3, "Produsul trebuie să aibă două zecimale: 16,65."),
        detective("B", ["2,05 × 0,23", "Calculăm 205 × 23 = 4715", "Factorii au împreună patru zecimale", "Rezultatul este 4,715"], 3, "Cu patru zecimale, rezultatul corect este 0,4715."),
        detective("C", ["0,03 × 100", "Mutăm virgula două locuri spre stânga", "Obținem 3"], 1, "La înmulțirea cu 100, virgula se mută două locuri spre dreapta."),
        detective("D", ["8,4 × 0,25", "Scriem 0,25 = 1/4", "Calculăm 8,4 : 4 = 2,1", "Produsul este 21"], 3, "Produsul este 2,1, nu 21."),
    ]

    questions += [
        problem("Un magazin primește 60 de saci a câte 45,75 kg și 40 de saci a câte 38,5 kg. Câte kilograme de făină primește?", "60 × 45,75 + 40 × 38,5 = □", "4285", "Cele două cantități sunt 2745 kg și 1540 kg; totalul este 4285 kg."),
        problem("Un turist parcurge 0,75 dintr-un traseu de 20 km în prima zi. Câți kilometri parcurge?", "0,75 × 20 = □", "15", "0,75 × 20 = 15 km."),
        problem("Un corn cântărește 0,079 kg. Cât cântăresc 13 cornuri?", "0,079 × 13 = □", "1,027", "Cele 13 cornuri cântăresc 1,027 kg."),
        problem("Într-o călimară sunt 0,023 l de cerneală. Câtă cerneală este în 12 călimări?", "0,023 × 12 = □", "0,276", "În total sunt 0,276 l."),
        problem("Un magazin vinde 92,55 m de stofă dimineața, iar după-amiaza de 2,5 ori mai mult. Câți metri vinde după-amiaza?", "92,55 × 2,5 = □", "231,375", "După-amiaza se vând 231,375 m."),
        problem("Un pachet conține 12 manuale de câte 0,483 kg, iar ambalajul cântărește 0,244 kg. Cât cântărește pachetul?", "12 × 0,483 + 0,244 = □", "6,04", "Manualele cântăresc 5,796 kg; cu ambalajul, pachetul are 6,04 kg."),
    ]

    questions += [
        grid("Rezultatul calculului 123,04 × 100 este:", "12 304", ["1 230,4", "123,4", "1,2304"], "Mutăm virgula două poziții spre dreapta."),
        grid("Un număr natural este cuprins între 6,32 × 1,3 și 6,32 × 1,9. Care poate fi acesta?", "9", ["6", "7", "13"], "Limitele sunt 8,216 și 12,008; dintre variante, 9 se află în interval."),
        grid("Care produs este egal cu 1?", "2 × 0,1 × 5", ["5 × 2,7 × 2", "3,5 × 2 × 1,6", "2,5 × 3,14"], "2 × 5 = 10, iar 10 × 0,1 = 1."),
    ]

    assert len(questions) == 34
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_fractii_zecimale_inmultirea.json"
    payload = {
        "title": "Înmulțirea fracțiilor zecimale cu un număr finit de zecimale nenule",
        "description": "Clasa a 5-a · Fracții zecimale",
        "difficulty": "medium",
        "questions": build_questions(),
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
