"""Generează lecția despre împărțirea numerelor naturale cu rezultat zecimal."""

import json
from pathlib import Path


TITLE = "Împărțirea a două numere naturale cu rezultat fracție zecimală; aplicație: media aritmetică a două sau mai multe numere naturale; transformarea unei fracții ordinare într-o fracție zecimală; periodicitate"


def iq(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10, "interactive": data, "explanation": explanation}


def remainders(digits, divisor):
    current, values = 0, []
    for digit in digits:
        current = current * 10 + int(digit)
        values.append(current % divisor)
        current %= divisor
    return values


def column(dividend, divisor, quotient, calculation_digits, label, continuing=False):
    values = remainders(calculation_digits, divisor)
    extra = len(calculation_digits) - len(str(dividend))
    labels = [f"Rest după cifra {index + 1}" for index in range(len(str(dividend)))]
    labels += [f"Rest după coborârea zeroului {index + 1}" for index in range(extra)]
    labels[-1] = "Rest după ultima cifră folosită"
    instruction = "Adaugă zerouri după virgulă și continuă împărțirea până la numărul de zecimale cerut." if continuing else "Completează câtul zecimal și resturile intermediare. Adaugă zerouri după virgulă până când restul devine 0."
    return iq(
        f"{'Continuă cu zerouri' if continuing else 'Împarte în coloană'}: {dividend} : {divisor} ({label}).",
        "column_division",
        {"dividend": dividend, "divisor": divisor, "quotient": quotient, "remainder": values[-1], "remainders": values, "calculation_digits": calculation_digits, "step_labels": labels, "instruction": instruction},
        f"Urmărim resturile și coborâm {extra} {'zerouri' if extra != 1 else 'zero'} după virgulă. Câtul cerut este {quotient}.",
    )


def decimal(text, mode, data, answers, explanation):
    data = {"mode": mode, **data, "answers": answers}
    return iq(text, "decimal_workbench", data, explanation)


def missing(text, expression, answer, explanation):
    return decimal(text, "missing", {"expression": expression, "fields": [{"key": "missing", "label": "Răspuns"}]}, {"missing": answer}, explanation)


def detective(label, steps, error_index, explanation):
    return iq(f"Detectivul greșelilor {label}: apasă primul pas greșit.", "divisibility_error", {"steps": steps, "error_index": error_index}, explanation)


def classification(label, items):
    categories = [
        {"value": "finita", "label": "Finită"},
        {"value": "simpla", "label": "Periodică simplă"},
        {"value": "mixta", "label": "Periodică mixtă"},
    ]
    answers = {f"class:{item['id']}": item["answer"] for item in items}
    return decimal(
        f"Clasifică fracțiile din seria {label}.", "classification",
        {"items": [{"id": item["id"], "label": item["label"]} for item in items], "categories": categories}, answers,
        "După simplificare: numai factorii 2 și 5 în numitor dau o fracție zecimală finită; fără 2 și 5 obținem periodică simplă; combinația lor cu alți factori dă periodică mixtă.",
    )


def period_select(label, display, choices, answer):
    return decimal(f"Marchează perioada numărului {label}.", "period_select", {"display": display, "choices": choices}, {"period": answer}, f"Grupul care se repetă este {answer}; acesta este perioada.")


def period_notation(label, display, prefix, answer):
    return decimal(f"Scrie cu paranteze numărul {display} ({label}).", "period_notation", {"prefix": prefix}, {"period": answer}, f"Perioada este {answer}, deci o scriem o singură dată între paranteze.")


def average(label, known, target, answer, minimum, maximum, step="1"):
    initial = str(minimum).replace(".", ",")
    return decimal(
        f"Echilibrează media din seria {label}.", "average_balance",
        {"known_values": [str(value).replace(".", ",") for value in known], "target": str(target).replace(".", ","), "initial": initial, "min": minimum, "max": maximum, "step": step},
        {"missing": str(answer).replace(".", ",")},
        f"Suma tuturor numerelor trebuie să fie media înmulțită cu numărul termenilor. Numărul lipsă este {str(answer).replace('.', ',')}.",
    )


def build_questions():
    questions = []

    for row in [
        (23, 5, "4,6", "230", "A"), (85, 4, "21,25", "8500", "B"),
        (14, 20, "0,7", "140", "C"), (7, 25, "0,28", "700", "D"),
        (59, 50, "1,18", "5900", "E"), (472, 10, "47,2", "4720", "F"),
    ]:
        questions.append(column(*row))

    for row in [
        (37, 15, "2,4", "370", "A", True), (25, 9, "2,777", "25000", "B", True),
        (311, 12, "25,91", "31100", "C", True), (329, 3, "109,666", "329000", "D", True),
    ]:
        questions.append(column(*row))

    for label, digits, position, answer in [
        ("A", "24", 1, "2,4"), ("B", "007", 1, "0,07"),
        ("C", "0015", 1, "0,015"), ("D", "234", 2, "23,4"),
    ]:
        questions.append(decimal(
            f"Mută virgula după împărțirea din seria {label}.", "comma",
            {"digits": digits, "places": len(digits) - position}, {"position": str(position)},
            f"Poziția corectă produce numărul {answer}.",
        ))

    questions += [
        detective("A", ["23 : 5", "23 : 5 = 4, rest 3", "Coborâm un zero: 30 : 5 = 6", "Rezultatul este 46"], 3, "După partea întreagă se scrie virgula; rezultatul este 4,6."),
        detective("B", ["85 : 4", "8 : 4 = 2", "5 : 4 = 1, rest 0", "Câtul este 21,25"], 2, "După 8 : 4, la coborârea lui 5 obținem 1 și rest 1, nu rest 0."),
        detective("C", ["1/3 = 1 : 3", "Adăugăm un zero și obținem 10 : 3 = 3, rest 1", "Același rest reapare", "Fracția este zecimală finită"], 3, "Reapariția aceluiași rest arată că fracția este periodică: 0,(3)."),
        detective("D", ["Media numerelor 4, 5, 11 și 13", "Suma este 33", "Sunt 4 numere", "Media este 33 : 3 = 11"], 3, "Suma se împarte la 4, deci media este 8,25."),
    ]

    questions += [
        classification("A", [{"id":"a","label":"3/4","answer":"finita"},{"id":"b","label":"8/9","answer":"simpla"},{"id":"c","label":"5/6","answer":"mixta"}]),
        classification("B", [{"id":"a","label":"17/29","answer":"simpla"},{"id":"b","label":"44/30","answer":"mixta"},{"id":"c","label":"76/25","answer":"finita"}]),
        classification("C", [{"id":"a","label":"43/625","answer":"finita"},{"id":"b","label":"239/17","answer":"simpla"},{"id":"c","label":"701/20","answer":"finita"}]),
        classification("D", [{"id":"a","label":"37/15","answer":"mixta"},{"id":"b","label":"403/600","answer":"mixta"},{"id":"c","label":"9/125","answer":"finita"}]),
        classification("E", [{"id":"a","label":"1/12","answer":"mixta"},{"id":"b","label":"4/9","answer":"simpla"},{"id":"c","label":"25/75","answer":"simpla"}]),
    ]

    questions += [
        period_select("0,333333…", "0,333333…", ["3", "33", "333"], "3"),
        period_select("4,636363…", "4,636363…", ["6", "63", "363"], "63"),
        period_select("5,833333…", "5,833333…", ["8", "3", "83"], "3"),
        period_select("0,3090909…", "0,3090909…", ["3", "09", "309"], "09"),
    ]

    questions += [
        period_notation("A", "0,333333…", "0,", "3"),
        period_notation("B", "4,636363…", "4,", "63"),
        period_notation("C", "5,833333…", "5,8", "3"),
        period_notation("D", "0,3090909…", "0,3", "09"),
    ]

    questions += [
        average("A", [12], 15, 18, 1, 30),
        average("B", [8, 9], 8, 7, 1, 15),
        average("C", [6, 8, 5, 10], 8, 11, 1, 15),
        average("D", [2.4], 4.5, 6.6, 0, 10, "0.1"),
    ]

    questions += [
        missing("O bomboană costă 5 lei, iar 10 bomboane identice costă la fel. Care este prețul unei bomboane?", "5 : 10 = □ lei", "0,5", "Prețul este 0,5 lei."),
        missing("100 de rezerve de stilou costă 30 de lei. Cât costă o rezervă?", "30 : 100 = □ lei", "0,3", "O rezervă costă 0,3 lei."),
        missing("Radu are mediile 9 și 10 în cele două semestre. Care este media anuală?", "(9 + 10) : 2 = □", "9,5", "Suma este 19, iar 19 : 2 = 9,5."),
        missing("Media a două numere este 21,35, iar unul este 18,3. Determină celălalt număr.", "2 × 21,35 − 18,3 = □", "24,4", "Suma celor două numere este 42,7; numărul lipsă este 24,4."),
        missing("Media a trei numere este 7,14. Care este suma lor?", "3 × 7,14 = □", "21,42", "Suma este media înmulțită cu 3: 21,42."),
        missing("Clara are notele 8, 9 și 7 la istorie. Care este media?", "(8 + 9 + 7) : 3 = □", "8", "Suma notelor este 24, iar 24 : 3 = 8."),
        missing("Un traseu de 21 km este împărțit egal în 4 etape. Câți kilometri are fiecare etapă?", "21 : 4 = □ km", "5,25", "Fiecare etapă are 5,25 km."),
    ]

    assert len(questions) == 42, len(questions)
    return questions


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_fractii_zecimale_impartirea_numerelor_naturale.json"
    payload = {"title": TITLE, "description": "Clasa a 5-a · Fracții zecimale", "difficulty": "medium", "questions": build_questions()}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
