"""Generează lecția „Scrierea în baza 10. Scrierea în baza 2” pentru clasa a V-a."""

import json
from pathlib import Path


def grid(text, correct, wrong, explanation):
    correct, wrong = str(correct), [str(value) for value in wrong]
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3
    return {
        "text": text, "format": "grid", "points": 10, "explanation": explanation,
        "options": [
            {"text": wrong[0], "is_correct": False}, {"text": correct, "is_correct": True},
            {"text": wrong[1], "is_correct": False}, {"text": wrong[2], "is_correct": False},
        ],
    }


def true_false(text, answer, explanation):
    return {
        "text": text, "format": "true_false", "points": 10, "explanation": explanation,
        "options": [
            {"text": "Adevărat", "is_correct": answer}, {"text": "Fals", "is_correct": not answer},
        ],
    }


def interactive(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10, "explanation": explanation, "interactive": data}


def binary(value):
    return format(value, "b")


def terms_for(number, base):
    return [
        {"digit": int(digit), "exponent": len(number) - index - 1, "contribution": int(digit) * base ** (len(number) - index - 1)}
        for index, digit in enumerate(number)
    ]


def division_rows(number):
    rows = []
    current = number
    while current:
        rows.append({"dividend": current, "quotient": current // 2, "remainder": current % 2})
        current //= 2
    return rows


def build_questions():
    questions = []

    # 3. Scara împărțirilor succesive la 2.
    for number in [18, 27, 35, 68, 97]:
        rows = division_rows(number)
        answers = {}
        for index, row in enumerate(rows):
            answers[f"{index}:quotient"] = row["quotient"]
            answers[f"{index}:remainder"] = row["remainder"]
        questions.append(interactive(
            f"Transformați numărul {number} din baza 10 în baza 2 folosind împărțiri succesive la 2.",
            "base_values", {"mode": "division_ladder", "number": number, "rows": rows, "answers": answers},
            f"Citind resturile de jos în sus obținem {binary(number)}₂.",
        ))

    # 4 și 5. Descompuneri în puteri ale bazei.
    for number in ["812", "1121", "67008", "12014"]:
        terms = terms_for(number, 10)
        answers = {f"{index}:contribution": term["contribution"] for index, term in enumerate(terms)}
        questions.append(interactive(
            f"Descompuneți numărul {int(number):,} în puteri ale lui 10.".replace(",", " "),
            "base_values", {"mode": "decompose", "base": 10, "number": number, "terms": terms, "answers": answers},
            "Fiecare cifră se înmulțește cu puterea lui 10 corespunzătoare poziției sale.",
        ))
    for number in ["101", "1101", "1010101", "11001011"]:
        terms = terms_for(number, 2)
        answers = {f"{index}:contribution": term["contribution"] for index, term in enumerate(terms)}
        questions.append(interactive(
            f"Descompuneți numărul {number}₂ în puteri ale lui 2.",
            "base_values", {"mode": "decompose", "base": 2, "number": number, "terms": terms, "answers": answers},
            f"Suma contribuțiilor este {int(number, 2)}, deci {number}₂ = {int(number, 2)}₁₀.",
        ))

    # 6 și 7. Compunerea numerelor din puteri.
    decimal_sets = [
        [(8, 800, "8 · 10²"), (1, 10, "1 · 10¹"), (2, 2, "2 · 10⁰")],
        [(1, 1000, "1 · 10³"), (1, 100, "1 · 10²"), (2, 20, "2 · 10¹"), (1, 1, "1 · 10⁰")],
        [(6, 60000, "6 · 10⁴"), (7, 7000, "7 · 10³"), (8, 8, "8 · 10⁰")],
        [(1, 10000, "1 · 10⁴"), (2, 2000, "2 · 10³"), (1, 10, "1 · 10¹"), (4, 4, "4 · 10⁰")],
    ]
    for index, raw in enumerate(decimal_sets, 1):
        terms = [{"value": value, "label": label} for _, value, label in raw]
        answer = sum(term["value"] for term in terms)
        questions.append(interactive(
            f"Compuneți numărul în baza 10 din suma de puteri, seria {index}.",
            "base_values", {"mode": "compose", "base": 10, "terms": terms, "answers": {"number": str(answer)}},
            f"Adunând contribuțiile obținem {answer:,}.".replace(",", " "),
        ))
    binary_sets = [
        [(16, "1 · 2⁴"), (4, "1 · 2²"), (1, "1 · 2⁰")],
        [(32, "1 · 2⁵"), (8, "1 · 2³"), (2, "1 · 2¹")],
        [(64, "1 · 2⁶"), (16, "1 · 2⁴"), (4, "1 · 2²"), (1, "1 · 2⁰")],
        [(128, "1 · 2⁷"), (64, "1 · 2⁶"), (8, "1 · 2³"), (2, "1 · 2¹"), (1, "1 · 2⁰")],
    ]
    for index, raw in enumerate(binary_sets, 1):
        terms = [{"value": value, "label": label} for value, label in raw]
        decimal = sum(term["value"] for term in terms)
        questions.append(interactive(
            f"Compuneți numărul în baza 2 din puterile date, seria {index}.",
            "base_values", {"mode": "compose", "base": 2, "terms": terms, "answers": {"number": binary(decimal)}},
            f"Suma este {decimal}, iar {decimal}₁₀ = {binary(decimal)}₂.",
        ))

    # 8. Tabele poziționale cu tipuri diferite de celule lipsă.
    for index, (number, base) in enumerate([("5072", 10), ("12014", 10), ("110101", 2), ("1011001", 2)], 1):
        source_terms = terms_for(number, base)
        rows, answers = [], {}
        missing_cycle = ["digit", "exponent", "contribution"]
        for row_index, term in enumerate(source_terms):
            missing = missing_cycle[row_index % len(missing_cycle)]
            rows.append({**term, "missing": missing})
            answers[f"{row_index}:{missing}"] = term[missing]
        questions.append(interactive(
            f"Completați tabelul pozițional pentru {number} în baza {base}, seria {index}.",
            "base_values", {"mode": "place_table", "base": base, "number": number, "rows": rows, "answers": answers},
            f"Contribuția unei cifre este cifra · {base}^exponent.",
        ))

    # 9. Asociere prin drag-and-drop între cifre/poziții și puteri.
    drag_specs = [
        ("812₁₀", [("cifra 8", "10²"), ("cifra 1", "10¹"), ("cifra 2", "10⁰")]),
        ("5072₁₀", [("cifra 5", "10³"), ("cifra 0", "10²"), ("cifra 7", "10¹"), ("cifra 2", "10⁰")]),
        ("1101₂", [("primul 1", "2³"), ("al doilea 1", "2²"), ("cifra 0", "2¹"), ("ultimul 1", "2⁰")]),
        ("10110₂", [("primul 1", "2⁴"), ("primul 0", "2³"), ("al doilea 1", "2²"), ("al doilea 0", "2⁰")]),
    ]
    for index, (number, pairs) in enumerate(drag_specs, 1):
        questions.append(interactive(
            f"Potriviți prin tragere cifrele selectate din {number} cu puterile pozițiilor lor.",
            "base_match", {"pairs": [{"left": left, "right": right} for left, right in pairs], "right_order": list(reversed(range(len(pairs))))},
            "Puterea poziției crește de la dreapta spre stânga, începând cu exponentul 0.",
        ))

    # 10. Comutatoare 0/1.
    for value in [13, 18, 27, 35, 68]:
        questions.append(interactive(
            f"Aprindeți biții potriviți pentru a reprezenta numărul {value} în baza 2.",
            "binary_toggle", {"decimal": value, "binary": binary(value)},
            f"{value}₁₀ = {binary(value)}₂.",
        ))

    # 11. Cifre binare lipsă.
    for value, missing in [(13, [1]), (18, [1, 3]), (27, [2, 4]), (45, [1, 4]), (77, [2, 5])]:
        representation = binary(value)
        digits = [int(digit) for digit in representation]
        answers = {f"digit:{position}": digits[position] for position in missing}
        questions.append(interactive(
            f"Completați cifrele lipsă din scrierea în baza 2 a numărului {value}.",
            "base_values", {"mode": "missing_digits", "base": 2, "digits": digits, "missing_indices": missing, "decimal": value, "answers": answers},
            f"Scrierea completă este {representation}₂.",
        ))

    # 12. Potrivirea formelor echivalente.
    match_sets = [
        [("5₁₀", "101₂"), ("9₁₀", "1001₂"), ("12₁₀", "1100₂"), ("15₁₀", "1111₂")],
        [("18₁₀", "10010₂"), ("21₁₀", "10101₂"), ("26₁₀", "11010₂"), ("31₁₀", "11111₂")],
        [("1011₂", "2³ + 2¹ + 2⁰"), ("1100₂", "2³ + 2²"), ("10001₂", "2⁴ + 2⁰"), ("10110₂", "2⁴ + 2² + 2¹")],
        [("3 · 10² + 4 · 10 + 2", "342₁₀"), ("7 · 10³ + 5", "7005₁₀"), ("9 · 10² + 8 · 10", "980₁₀"), ("10⁴ + 2 · 10² + 1", "10201₁₀")],
    ]
    for index, pairs in enumerate(match_sets, 1):
        questions.append(interactive(
            f"Potriviți reprezentările echivalente, seria {index}.",
            "base_match", {"pairs": [{"left": left, "right": right} for left, right in pairs], "right_order": [2, 0, 3, 1]},
            "Fiecare cartonaș trebuie asociat cu aceeași valoare scrisă în altă formă.",
        ))

    # 13. Detectivul erorilor de conversie.
    error_sets = [
        (["13 : 2 = 6, rest 1", "6 : 2 = 3, rest 0", "3 : 2 = 1, rest 0", "1 : 2 = 0, rest 1", "Rezultat: 1101₂"], 2, "La 3 : 2 restul este 1, nu 0."),
        (["10110₂ = 1·2⁴ + 0·2³ + 1·2² + 1·2¹ + 0·2⁰", "= 16 + 0 + 4 + 2 + 0", "= 24₁₀", "Deci 10110₂ = 24₁₀"], 2, "16 + 4 + 2 = 22, nu 24."),
        (["67008 = 6·10⁴ + 7·10³ + 0·10² + 0·10 + 8", "= 60 000 + 7 000 + 0 + 0 + 8", "= 67 080", "Deci descompunerea dă numărul inițial."], 2, "Suma este 67 008, nu 67 080."),
        (["18 : 2 = 9, rest 0", "9 : 2 = 4, rest 1", "4 : 2 = 2, rest 0", "2 : 2 = 1, rest 0", "Resturile citite de sus în jos dau 0100₂"], 4, "Resturile trebuie citite de jos în sus, inclusiv ultimul rest 1: 10010₂."),
    ]
    for index, (steps, error_index, explanation) in enumerate(error_sets, 1):
        questions.append(interactive(
            f"Detectivul conversiilor: apăsați primul pas greșit din rezolvarea {index}.",
            "base_error", {"steps": steps, "error_index": error_index}, explanation,
        ))

    # 14. Adevărat/fals pentru proprietățile esențiale.
    questions.extend([
        true_false("În baza 2 putem folosi numai cifrele 0 și 1.", True, "Sistemul binar are exact două cifre: 0 și 1."),
        true_false("Numărul 111₂ este egal cu 111₁₀.", False, "111₂ = 4 + 2 + 1 = 7₁₀."),
        true_false("Un număr binar care se termină în 0 reprezintă un număr par.", True, "Ultima cifră arată contribuția lui 2⁰; dacă este 0, numărul este par."),
        true_false("Numărul 10001₂ este pătratul unui număr natural.", False, "10001₂ = 17₁₀, iar 17 nu este pătrat perfect."),
    ])

    # 15. Compararea numerelor scrise în baze diferite.
    questions.extend([
        grid("Comparați 10101₂ și 20₁₀.", "10101₂ > 20₁₀", ["10101₂ < 20₁₀", "10101₂ = 20₁₀", "Nu se pot compara"], "10101₂ = 21₁₀."),
        grid("Comparați 11010₂ și 27₁₀.", "11010₂ < 27₁₀", ["11010₂ > 27₁₀", "11010₂ = 27₁₀", "Nu se pot compara"], "11010₂ = 26₁₀."),
        grid("Care este cel mai mare număr?", "100000₂", ["30₁₀", "11111₂", "29₁₀"], "100000₂ = 32, iar 11111₂ = 31."),
        grid("Care este cel mai mic număr?", "1110₂", ["15₁₀", "10000₂", "10001₂"], "1110₂ = 14₁₀."),
        grid("Ce semn completează corect: 101101₂ __ 45₁₀?", "=", ["<", ">", "≠"], "101101₂ = 32 + 8 + 4 + 1 = 45."),
        grid("Ce semn completează corect: 1000001₂ __ 64₁₀?", ">", ["<", "=", "≤"], "1000001₂ = 65₁₀."),
    ])

    # 23. Egalități între baza 10 și baza 2.
    for left_value, left_base, answer_base in [("21", 10, 2), ("11010", 2, 10), ("85", 10, 2), ("11001011", 2, 10)]:
        decimal = int(left_value, left_base)
        answer = binary(decimal) if answer_base == 2 else str(decimal)
        questions.append(interactive(
            f"Completați egalitatea care începe cu {left_value} în baza {left_base}.",
            "base_values", {"mode": "complete_equality", "left_value": left_value, "left_base": left_base, "answer_base": answer_base, "answers": {"value": answer}},
            f"Valoarea lipsă este {answer} în baza {answer_base}.",
        ))

    # 24. Codul secret — exact două exerciții.
    for secret_index, word in enumerate(["FOC", "MAT"], 1):
        items, answers = [], {}
        for index, letter in enumerate(word):
            position = ord(letter) - ord("A") + 1
            items.append({"binary": binary(position), "position": position})
            answers[f"letter:{index}"] = letter
        questions.append(interactive(
            f"Descifrați codul secret {secret_index}, format din {len(word)} litere.",
            "base_values", {"mode": "secret_code", "items": items, "answers": answers},
            f"Codurile indică pozițiile literelor în alfabet și formează cuvântul {word}.",
        ))

    assert len(questions) == 63, len(questions)
    assert len({question["text"] for question in questions}) == len(questions)
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_operatii_sisteme_de_numeratie.json"
    payload = {
        "title": "Scrierea în baza 10. Scrierea în baza 2",
        "description": "Clasa a 5-a · Operații cu numere naturale",
        "difficulty": "medium",
        "questions": build_questions(),
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
