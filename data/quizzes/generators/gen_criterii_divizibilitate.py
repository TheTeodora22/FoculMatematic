"""Generează lecția despre criteriile de divizibilitate din clasa a V-a."""

import json
from pathlib import Path


def grid(text, correct, wrong, explanation):
    correct = str(correct)
    wrong = [str(value) for value in wrong]
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3
    return {
        "text": text,
        "format": "grid",
        "points": 10,
        "explanation": explanation,
        "options": [
            {"text": wrong[0], "is_correct": False},
            {"text": correct, "is_correct": True},
            {"text": wrong[1], "is_correct": False},
            {"text": wrong[2], "is_correct": False},
        ],
    }


def true_false(text, answer, explanation):
    return {
        "text": text,
        "format": "true_false",
        "points": 10,
        "explanation": explanation,
        "options": [
            {"text": "Adevărat", "is_correct": answer},
            {"text": "Fals", "is_correct": not answer},
        ],
    }


def interactive(text, kind, data, explanation):
    return {
        "text": text,
        "type": kind,
        "format": "interactive",
        "points": 10,
        "interactive": data,
        "explanation": explanation,
    }


def criteria_table(numbers, divisors, label):
    answers = {
        f"{row}:{column}": number % divisor == 0
        for row, divisor in enumerate(divisors)
        for column, number in enumerate(numbers)
    }
    return interactive(
        f"Completează tabelul {label}: apasă fiecare căsuță pentru a alege ✓ sau ×.",
        "criteria_table",
        {"numbers": numbers, "divisors": divisors, "answers": answers},
        "Fiecare răspuns se obține aplicând criteriul corespunzător, fără a efectua împărțirea.",
    )


def select_numbers(divisor, values, label):
    cards = [{"id": str(value), "label": str(value)} for value in values]
    correct = [str(value) for value in values if value % divisor == 0]
    return interactive(
        f"Selectează toate numerele divizibile cu {divisor} din setul {label}.",
        "divisibility_select",
        {"mode": "criteria", "cards": cards, "correct_ids": correct},
        f"Sunt selectate exact numerele care respectă criteriul de divizibilitate cu {divisor}.",
    )


def sort_numbers(divisor, values, label):
    return interactive(
        f"Sortează cartonașele {label} după divizibilitatea cu {divisor}.",
        "divisibility_sort",
        {
            "mode": "two_zones",
            "zones": [
                {"id": "yes", "label": f"Divizibile cu {divisor}"},
                {"id": "no", "label": f"Nedivizibile cu {divisor}"},
            ],
            "cards": [
                {"id": f"n{value}", "label": str(value), "zone": "yes" if value % divisor == 0 else "no"}
                for value in values
            ],
        },
        f"Aplicăm criteriul lui {divisor} fiecărui număr și îl așezăm în zona potrivită.",
    )


def missing_digit(pattern, divisor, label):
    valid = []
    for digit in range(10):
        number = int(pattern.replace("a", str(digit)))
        if number % divisor == 0:
            valid.append(str(digit))
    return interactive(
        f"Selectează toate cifrele care pot înlocui litera a în {pattern}, astfel încât numărul să fie divizibil cu {divisor} ({label}).",
        "divisibility_select",
        {
            "mode": "digits",
            "cards": [{"id": str(digit), "label": str(digit)} for digit in range(10)],
            "correct_ids": valid,
        },
        f"Verificăm pe rând cifrele 0–9 cu criteriul de divizibilitate cu {divisor}. Cifre corecte: {', '.join(valid)}.",
    )


def digit_sum(number, divisor, label):
    total = sum(int(digit) for digit in str(number))
    verdict = "este" if number % divisor == 0 else "nu este"
    return interactive(
        f"Calculează suma cifrelor lui {number} pentru a decide dacă numărul este divizibil cu {divisor} ({label}).",
        "divisibility_values",
        {
            "mode": "digit_sum",
            "number": number,
            "criterion": divisor,
            "fields": [{"key": "sum"}],
            "answers": {"sum": total},
        },
        f"Suma cifrelor este {total}; de aceea {number} {verdict} divizibil cu {divisor}.",
    )


def error_detective(text, steps, error_index, explanation):
    return interactive(
        text,
        "divisibility_error",
        {"steps": steps, "error_index": error_index},
        explanation,
    )


def build_questions():
    questions = []

    # Tabele de criterii: elevul marchează fiecare intersecție cu ✓ sau ×.
    questions.extend([
        criteria_table([10, 36, 40, 135, 300, 978, 2400, 22500], [2, 3, 5, 9, 10], "mixt 1"),
        criteria_table([48, 73, 90, 115, 224, 349, 401, 636], [2, 5, 10], "al ultimei cifre"),
        criteria_table([400, 1010, 3400, 12000, 40910, 1002], [10, 100, 1000], "puterilor lui 10"),
        criteria_table([6498, 741, 9085, 3006, 999, 1242], [3, 9], "al sumei cifrelor"),
        criteria_table([20, 24, 44, 45, 50, 60, 66, 72], [2, 3, 5, 9, 10], "mixt 2"),
        criteria_table([100, 250, 900, 1000, 1200, 4500, 10000], [2, 5, 10, 100, 1000], "cu zerouri la final"),
    ])

    # Selecții rapide de numere.
    selection_sets = [
        (2, [28, 35, 49, 120, 1294, 2375, 5401, 145340], "A"),
        (5, [48, 115, 224, 349, 575, 636, 777, 1002], "B"),
        (10, [20, 44, 50, 60, 81, 96, 120, 135], "C"),
        (100, [400, 1010, 3400, 12000, 40910, 6000, 7205, 22500], "D"),
        (1000, [1000, 2400, 3000, 4500, 12000, 15000, 22005, 10000], "E"),
        (3, [741, 9085, 6498, 1294, 3006, 401, 636, 575], "F"),
        (9, [135, 300, 978, 2400, 22500, 741, 999, 1242], "G"),
        (6, [12, 18, 20, 24, 30, 35, 42, 45, 48], "H: simultan cu 2 și cu 3"),
    ]
    for divisor, values, label in selection_sets:
        if divisor == 6:
            cards = [{"id": str(value), "label": str(value)} for value in values]
            correct = [str(value) for value in values if value % 2 == 0 and value % 3 == 0]
            questions.append(interactive(
                "Selectează numerele care sunt simultan divizibile cu 2 și cu 3 din setul H.",
                "divisibility_select",
                {"mode": "criteria", "cards": cards, "correct_ids": correct},
                "Un număr ales trebuie să aibă ultima cifră pară și suma cifrelor divizibilă cu 3.",
            ))
        else:
            questions.append(select_numbers(divisor, values, label))

    # Sortare în două zone.
    for divisor, values, label in [
        (2, [16, 27, 30, 41, 58, 73, 84, 95], "setul I"),
        (5, [25, 32, 40, 51, 65, 78, 90, 104], "setul J"),
        (10, [70, 81, 120, 135, 240, 308, 990, 1001], "setul K"),
        (3, [111, 205, 318, 421, 504, 617, 729, 802], "setul L"),
        (9, [117, 225, 307, 432, 540, 703, 801, 918], "setul M"),
        (100, [300, 405, 800, 1010, 2700, 3405, 9900, 10001], "setul N"),
    ]:
        questions.append(sort_numbers(divisor, values, label))

    # Cifre lipsă.
    for pattern, divisor, label in [
        ("19a", 2, "ultima cifră pară"),
        ("65a", 2, "ultima cifră pară"),
        ("74a", 5, "ultima cifră 0 sau 5"),
        ("4a2a", 5, "ultima cifră 0 sau 5"),
        ("12a", 10, "ultima cifră 0"),
        ("7a5", 3, "suma cifrelor"),
        ("98a", 3, "suma cifrelor"),
        ("4a8a", 3, "suma cifrelor"),
        ("15a", 9, "suma cifrelor"),
        ("2a9", 9, "suma cifrelor"),
        ("333a", 9, "suma cifrelor"),
        ("45a2", 9, "suma cifrelor"),
    ]:
        questions.append(missing_digit(pattern, divisor, label))

    # Atelierul sumei cifrelor.
    for number, divisor, label in [
        (6498, 9, "atelier A"),
        (741, 3, "atelier B"),
        (9085, 3, "atelier C"),
        (3006, 9, "atelier D"),
        (1294, 3, "atelier E"),
        (2375, 9, "atelier F"),
        (145340, 3, "atelier G"),
        (225035, 9, "atelier H"),
    ]:
        questions.append(digit_sum(number, divisor, label))

    # Detectivul greșelilor.
    questions.extend([
        error_detective(
            "Detectivul greșelilor A: apasă primul pas greșit din verificarea lui 6498.",
            ["6 + 4 + 9 + 8 = 26", "26 nu este divizibil cu 9", "6498 nu este divizibil cu 9"],
            0,
            "Primul pas este greșit: 6 + 4 + 9 + 8 = 27, iar 27 este divizibil cu 9.",
        ),
        error_detective(
            "Detectivul greșelilor B: apasă primul pas greșit din verificarea lui 741.",
            ["7 + 4 + 1 = 12", "12 este divizibil cu 3", "De aceea, 741 este divizibil cu 9"],
            2,
            "Primele două afirmații sunt corecte, dar 12 nu este divizibil cu 9; 741 nu este divizibil cu 9.",
        ),
        error_detective(
            "Detectivul greșelilor C: apasă primul pas greșit din verificarea lui 575.",
            ["Ultima cifră este 5", "575 este divizibil cu 5", "Orice număr divizibil cu 5 este divizibil și cu 10"],
            2,
            "Pentru divizibilitate cu 10, ultima cifră trebuie să fie 0, nu 5.",
        ),
        error_detective(
            "Detectivul greșelilor D: apasă primul pas greșit din verificarea lui 1010.",
            ["Ultimele două cifre sunt 10", "10 conține un zero", "Prin urmare, 1010 este divizibil cu 100"],
            2,
            "Un număr este divizibil cu 100 numai dacă ultimele două cifre sunt ambele 0.",
        ),
    ])

    # Adevărat sau fals, numai unde fixează o confuzie frecventă.
    questions.extend([
        true_false("Dacă ultima cifră a unui număr este 0, numărul este divizibil cu 2, cu 5 și cu 10.", True, "Cifra 0 este pară și îndeplinește criteriile lui 5 și 10."),
        true_false("Orice număr care se termină în 5 este divizibil cu 10.", False, "Pentru 10, ultima cifră trebuie să fie 0."),
        true_false("Dacă suma cifrelor unui număr este 18, numărul este divizibil atât cu 3, cât și cu 9.", True, "18 este divizibil atât cu 3, cât și cu 9."),
        true_false("Numărul 3400 este divizibil cu 1000.", False, "Ultimele trei cifre sunt 400, nu 000."),
        true_false("Un număr divizibil cu 9 este întotdeauna divizibil și cu 3.", True, "Orice sumă de cifre divizibilă cu 9 este și divizibilă cu 3."),
    ])

    # Grile scurte și probleme aplicate.
    questions.extend([
        grid("Care dintre numere este divizibil cu 2?", 1294, [2375, 5401, 225035], "Ultima cifră a lui 1294 este 4, o cifră pară."),
        grid("Care dintre numere este divizibil cu 5, dar nu cu 10?", 575, [120, 636, 1002], "575 se termină în 5, nu în 0."),
        grid("Care număr este divizibil cu 100?", 22500, [22505, 22450, 22005], "Ultimele două cifre ale lui 22500 sunt 00."),
        grid("Care număr este divizibil cu 1000?", 12000, [12400, 12010, 10200], "Ultimele trei cifre ale lui 12000 sunt 000."),
        grid("Care este suma cifrelor numărului 6498?", 27, [26, 28, 29], "6 + 4 + 9 + 8 = 27."),
        grid("Care număr este divizibil cu 9?", 6498, [741, 9085, 1294], "Suma cifrelor lui 6498 este 27, multiplu de 9."),
        grid("Câte cifre pot înlocui a în numărul 15a pentru ca acesta să fie divizibil cu 9?", 1, [2, 3, 5], "1 + 5 + a trebuie să fie multiplu de 9; singura cifră este a = 3."),
        grid("Câte cifre pot înlocui a în numărul 19a pentru ca acesta să fie divizibil cu 2?", 5, [2, 4, 10], "Cifrele posibile sunt 0, 2, 4, 6 și 8."),
        grid("Un stadion are 7374 de locuri. Se pot împărți locurile egal în 9 zone?", "Nu, deoarece suma cifrelor este 21", ["Da, deoarece ultima cifră este pară", "Da, deoarece suma cifrelor este 21", "Nu, deoarece numărul nu se termină în 9"], "Suma cifrelor este 21, iar 21 nu este divizibil cu 9."),
        grid("Care număr poate fi împărțit egal atât în grupe de 2, cât și în grupe de 3?", 42, [35, 45, 49], "42 este par, iar suma cifrelor sale este 6."),
        grid("Ce cifră trebuie pusă la finalul lui 4091 pentru a obține un număr divizibil cu 10?", 0, [2, 5, 9], "Un număr divizibil cu 10 are ultima cifră 0."),
    ])

    assert len(questions) == 60, len(questions)
    assert len({question["text"] for question in questions}) == len(questions)
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_criterii_de_divizibilitate.json"
    payload = {
        "title": "Criterii de divizibilitate",
        "description": "Clasa a 5-a · Criteriile de divizibilitate cu 2, 3, 5, 9, 10 și puterile lui 10",
        "difficulty": "medium",
        "questions": build_questions(),
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
