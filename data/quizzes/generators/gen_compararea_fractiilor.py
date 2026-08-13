"""Generează lecția despre compararea fracțiilor și axa numerelor."""

import json
from pathlib import Path


def grid(text, correct, wrong, explanation):
    values = [str(correct), *(str(value) for value in wrong)]
    assert len(values) == 4 and len(set(values)) == 4
    order = [2, 0, 3, 1]
    return {"text": text, "type": "multiple_choice", "format": "grid", "points": 10,
            "explanation": explanation,
            "options": [{"text": values[index], "is_correct": index == 0} for index in order]}


def true_false(text, answer, explanation):
    return {"text": text, "type": "multiple_choice", "format": "true_false", "points": 10,
            "explanation": explanation,
            "options": [{"text": value, "is_correct": value == answer} for value in ("Adevărat", "Fals")]}


def interactive(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10,
            "explanation": explanation, "interactive": data}


def relation(left, right):
    a, b = left
    c, d = right
    return "<" if a * d < c * b else ">" if a * d > c * b else "="


def comparison(text, left, right, explanation, mode="symbol", shape="bar"):
    return interactive(text, "fraction_compare", {
        "mode": mode, "left": list(left), "right": list(right),
        "relation": relation(left, right), "shape": shape,
    }, explanation)


def ordering(text, entries, direction, display_order, explanation):
    reverse = direction == "desc"
    correct = sorted(range(len(entries)), key=lambda index: entries[index][0] / entries[index][1], reverse=reverse)
    return interactive(text, "fraction_compare", {
        "mode": "order", "direction": direction,
        "items": [{"label": f"{n}/{d}", "numerator": n, "denominator": d} for n, d in entries],
        "correct_order": correct, "display_order": display_order,
    }, explanation)


def axis(text, numerator, denominator, maximum, explanation):
    return interactive(text, "fraction_axis", {
        "mode": "place", "target_numerator": numerator, "denominator": denominator,
        "maximum": maximum, "answer_tick": numerator,
    }, explanation)


def build_questions():
    questions = [
        grid("Care este fracția mai mare dintre 3/8 și 5/8?", "5/8", ["3/8", "Sunt egale", "8/5"], "Au același numitor; fracția cu numărătorul mai mare este mai mare."),
        grid("Alege fracția mai mică dintre 7/12 și 11/12.", "7/12", ["11/12", "12/7", "Sunt egale"], "Numitorii sunt egali și 7 < 11."),
        grid("Care este mai mare: 4/9 sau 4/13?", "4/9", ["4/13", "Sunt egale", "13/4"], "La același numărător, numitorul mai mic dă fracția mai mare."),
        grid("Alege fracția mai mică dintre 5/6 și 5/8.", "5/8", ["5/6", "Sunt egale", "8/5"], "La același numărător, împărțirea în mai multe părți produce părți mai mici."),
        grid("Ioana a parcurs 20/50 din pistă, iar Horia 30/50. Cine a parcurs mai mult?", "Horia", ["Ioana", "Au parcurs la fel", "Nu se poate afla"], "Fracțiile au același numitor și 30 > 20."),
        grid("Din două panglici egale, Ana folosește 3/7, iar Mara 3/10. Cine folosește o parte mai mare?", "Ana", ["Mara", "Folosesc părți egale", "Nu se poate compara"], "La același numărător, 3/7 > 3/10 deoarece 7 < 10."),
        grid("Pe o axă împărțită în sferturi, ce coordonată are a treia gradație după 0?", "3/4", ["1/4", "4/3", "3/5"], "Fiecare gradație valorează 1/4; a treia este 3/4."),
        grid("Unde se află 7/5 pe axa numerelor?", "Între 1 și 2", ["Între 0 și 1", "Exact în 1", "După 2"], "5/5 = 1 și 10/5 = 2, iar 5 < 7 < 10."),
        grid("Care fracție se află exact în punctul 1?", "9/9", ["8/9", "10/9", "1/9"], "O fracție echiunitară are numărătorul egal cu numitorul."),
        grid("Alege ordinea crescătoare corectă.", "2/9, 5/9, 8/9", ["8/9, 5/9, 2/9", "5/9, 2/9, 8/9", "2/9, 8/9, 5/9"], "La același numitor ordonăm numărătorii."),
        true_false("Dintre două fracții cu același numitor, este mai mare cea cu numărătorul mai mare.", "Adevărat", "Aceasta este regula comparației fracțiilor cu același numitor."),
        true_false("Dintre două fracții cu același numărător, este mai mare cea cu numitorul mai mare.", "Fals", "La același numărător, fracția cu numitorul mai mic este mai mare."),
        true_false("Fracția 6/6 se reprezintă în punctul 1 pe axa numerelor.", "Adevărat", "6/6 reprezintă un întreg."),
        true_false("Fracția 9/7 se află între 0 și 1.", "Fals", "9/7 > 1, deci se află după punctul 1."),
    ]

    symbol_data = [
        ((7, 13), (10, 13), "Numitorii sunt egali; comparăm 7 și 10."),
        ((15, 22), (9, 22), "Numitorii sunt egali; 15 > 9."),
        ((6, 11), (6, 17), "Numărătorii sunt egali; 11 < 17, deci 6/11 este mai mare."),
        ((8, 15), (8, 12), "Numărătorii sunt egali; numitorul 12 este mai mic."),
        ((12, 19), (12, 19), "Fracțiile sunt identice."),
        ((24, 50), (30, 50), "Au același numitor și 24 < 30."),
    ]
    for left, right, explanation in symbol_data:
        questions.append(comparison(f"Alege semnul corect între {left[0]}/{left[1]} și {right[0]}/{right[1]}.", left, right, explanation))

    visual_data = [
        ((3, 8), (5, 8), "circle", "Discurile au același număr de părți; 3 părți colorate sunt mai puține decât 5."),
        ((4, 7), (6, 7), "bar", "Benzile au același numitor și 4 < 6."),
        ((3, 5), (3, 8), "circle", "Sunt luate câte 3 părți, dar cincimile sunt mai mari decât optimile."),
        ((2, 6), (2, 9), "grid", "La același numărător, numitorul mai mic dă fracția mai mare."),
    ]
    for left, right, shape, explanation in visual_data:
        questions.append(comparison(f"Privește reprezentările fracțiilor {left[0]}/{left[1]} și {right[0]}/{right[1]}, apoi alege semnul corect.", left, right, explanation, "visual", shape))

    questions.extend([
        ordering("Așază în ordine crescătoare fracțiile cu numitorul 7.", [(2,7),(6,7),(4,7),(1,7)], "asc", [2,0,3,1], "Numitorul este comun, deci ordonăm numărătorii: 1 < 2 < 4 < 6."),
        ordering("Așază în ordine descrescătoare fracțiile cu numitorul 9.", [(3,9),(8,9),(5,9),(7,9)], "desc", [0,3,1,2], "Numitorul este comun, deci ordonăm descrescător numărătorii."),
        ordering("Așază în ordine crescătoare fracțiile cu numărătorul 4.", [(4,5),(4,11),(4,7),(4,9)], "asc", [2,0,3,1], "La același numărător, fracția este mai mică atunci când numitorul este mai mare."),
        ordering("Așază în ordine descrescătoare fracțiile cu numărătorul 5.", [(5,6),(5,12),(5,8),(5,10)], "desc", [1,3,0,2], "La același numărător, ordinea fracțiilor este inversă ordinii numitorilor."),
    ])

    axis_data = [
        (3, 4, 1, "A treia gradație de câte 1/4 este 3/4."),
        (7, 5, 2, "După 5/5 = 1 mai avansăm două cincimi."),
        (11, 6, 2, "Punctul 1 este 6/6, iar a unsprezecea gradație este 11/6."),
        (5, 8, 1, "Numărăm cinci gradații de câte 1/8 de la origine."),
        (13, 9, 2, "Punctul 1 este 9/9; 13/9 se află la patru gradații după el."),
        (17, 10, 2, "17/10 înseamnă un întreg și șapte zecimi."),
        (20, 12, 2, "20/12 se află la a douăzecea gradație când unitatea este împărțită în 12 părți."),
        (5, 3, 2, "5/3 este între 1 = 3/3 și 2 = 6/3."),
    ]
    for numerator, denominator, maximum, explanation in axis_data:
        questions.append(axis(f"Marchează fracția {numerator}/{denominator} pe axa numerelor.", numerator, denominator, maximum, explanation))

    assert len(questions) == 36
    return questions


def main():
    target = Path(__file__).resolve().parents[1] / "clasa_5_fractii_ordinare_compararea_si_reprezentarea_pe_axa.json"
    payload = {
        "title": "Compararea fracțiilor cu același numitor/numărător. Reprezentarea fracțiilor ordinare pe axa numerelor",
        "description": "Clasa a 5-a · Fracții ordinare", "difficulty": "easy",
        "questions": build_questions(),
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Am scris {len(payload['questions'])} întrebări în {target}.")


if __name__ == "__main__":
    main()
