"""Generează lecția compactă „Compararea puterilor”."""

import json
from pathlib import Path


SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def p(base, exponent):
    return f"{base}{str(exponent).translate(SUP)}"


def q(text, correct, wrong, explanation):
    values = [str(correct), *(str(value) for value in wrong)]
    assert len(values) == 4 and len(set(values)) == 4
    return {"text": text, "type": "multiple_choice", "format": "grid", "points": 10, "explanation": explanation,
            "options": [{"text": values[i], "is_correct": i == 0} for i in [2, 0, 1, 3]]}


def iq(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10,
            "explanation": explanation, "interactive": data}


def build_questions():
    questions = [
        q("Care dintre puterile cu baza 25 este mai mare?", "25²⁷", ["25²⁵", "Sunt egale", "Nu se pot compara"], "La aceeași bază mai mare decât 1, exponentul mai mare dă puterea mai mare."),
        q("Alege numărul mai mic dintre 16¹²³ și 16¹²⁴.", "16¹²³", ["16¹²⁴", "Sunt egale", "16²⁴⁷"], "Bazele sunt egale, iar 123 < 124."),
        q("Care este mai mare: 2⁰¹¹³ sau 2⁰¹¹⁵?", "2⁰¹¹⁵", ["2⁰¹¹³", "Sunt egale", "2²"], "Zerourile din fața exponentului nu schimbă valoarea: 115 > 113."),
        q("Dintre 111⁴ și 111³, care este mai mică?", "111³", ["111⁴", "Sunt egale", "111¹²"], "Pentru aceeași bază, comparăm exponenții."),
        q("Care este mai mică dintre 15²⁷ și 17²⁷?", "15²⁷", ["17²⁷", "Sunt egale", "2²⁷"], "La același exponent nenul, baza mai mică produce puterea mai mică."),
        q("Alege puterea mai mare dintre 24²³ și 23²³.", "24²³", ["23²³", "Sunt egale", "47²³"], "Exponenții sunt egali, deci comparăm bazele."),
        q("Care dintre 2¹⁰¹¹⁴ și 3¹⁰¹¹⁴ este mai mare?", "3¹⁰¹¹⁴", ["2¹⁰¹¹⁴", "Sunt egale", "6¹⁰¹¹⁴"], "Cu același exponent pozitiv, baza 3 este mai mare decât baza 2."),
        q("Alege numărul mai mic dintre 989¹²³ și 987¹²³.", "987¹²³", ["989¹²³", "Sunt egale", "2¹²³"], "Exponenții sunt egali și 987 < 989."),
        q("Care este mai mare după aducerea la baza 5: 5⁹ sau 25⁴?", "5⁹", ["25⁴", "Sunt egale", "5⁴"], "25⁴ = (5²)⁴ = 5⁸, iar 5⁹ > 5⁸."),
        q("Compară 4³³ și 8²¹. Care este mai mare?", "4³³", ["8²¹", "Sunt egale", "2¹²"], "4³³ = 2⁶⁶, iar 8²¹ = 2⁶³; 66 > 63."),
        q("Care este mai mică dintre 2⁴⁶ și 16¹²?", "2⁴⁶", ["16¹²", "Sunt egale", "2²"], "16¹² = (2⁴)¹² = 2⁴⁸, deci 2⁴⁶ este mai mică."),
        q("Compară 125⁴ și 25⁷. Care este mai mare?", "25⁷", ["125⁴", "Sunt egale", "5³"], "125⁴ = 5¹², iar 25⁷ = 5¹⁴."),
        q("Care este mai mare dintre 3⁵ și 5³?", "3⁵", ["5³", "Sunt egale", "8³"], "3⁵ = 243, iar 5³ = 125."),
        q("Alege cel mai mare număr dintre 2⁵, 3³, 5² și 4².", "2⁵", ["3³", "5²", "4²"], "Valorile sunt 32, 27, 25 și 16."),
    ]

    comparisons = [
        ("25²⁷", "25²⁹", "<", "Bazele sunt egale; 27 < 29."),
        ("16¹²⁴", "16¹²⁴", "=", "Expresiile sunt identice."),
        ("21⁵³", "24⁵³", "<", "Exponenții sunt egali, iar 21 < 24."),
        ("9¹⁵", "3²⁹", ">", "9¹⁵ = 3³⁰, iar 3³⁰ > 3²⁹."),
        ("8¹¹", "4¹⁶", "<", "8¹¹ = 2³³, iar 4¹⁶ = 2³²; de fapt 2³³ > 2³²."),
        ("125⁶", "25⁹", "=", "125⁶ = 5¹⁸ și 25⁹ = 5¹⁸."),
        ("2²⁰", "4⁹", ">", "4⁹ = 2¹⁸, iar 20 > 18."),
        ("7⁴", "5⁵", "<", "7⁴ = 2 401, iar 5⁵ = 3 125."),
    ]
    for left, right, relation, explanation in comparisons:
        # Corectăm explicit singura comparație exprimată prin conversie la baza 2.
        if left == "8¹¹": relation = ">"
        questions.append(iq(f"Alege semnul corect între {left} și {right}.", "power_compare",
                            {"left": left, "right": right, "relation": relation}, explanation))

    orders = [
        ("asc", [("2⁴", 16), ("3³", 27), ("5²", 25), ("4³", 64)], [2, 0, 3, 1]),
        ("desc", [("5³", 125), ("2⁷", 128), ("3⁴", 81), ("10²", 100)], [2, 0, 3, 1]),
        ("asc", [("4⁵", 4**5), ("2¹¹", 2**11), ("8³", 8**3), ("16²", 16**2)], [1, 3, 0, 2]),
        ("desc", [("9³", 9**3), ("3⁷", 3**7), ("27³", 27**3), ("81²", 81**2)], [2, 0, 3, 1]),
    ]
    for index, (direction, entries, display_order) in enumerate(orders):
        direction_text = "crescătoare" if direction == "asc" else "descrescătoare"
        questions.append(iq(f"Așază în ordine {direction_text} puterile: " + ", ".join(label for label, _ in entries) + ".",
                            "power_order", {"direction": direction, "items": [{"label": label, "value": value} for label, value in entries], "display_order": display_order},
                            "Comparăm valorile sau aducem puterile la aceeași bază."))

    assert len(questions) == 26
    return questions


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_operatii_compararea_puterilor.json"
    payload = {"title": "Compararea puterilor", "description": "Clasa a 5-a · Operații cu numere naturale",
               "difficulty": "easy", "questions": build_questions()}
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} întrebări în {target}.")


if __name__ == "__main__":
    main()
