"""Generează lecția 2: aproximări, comparare, ordonare și axă."""

import json
from pathlib import Path


def iq(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10, "interactive": data, "explanation": explanation}


def grid(text, correct, wrong, explanation):
    correct, wrong = str(correct), [str(value) for value in wrong]
    return {"text": text, "format": "grid", "points": 10, "explanation": explanation, "options": [
        {"text": wrong[0], "is_correct": False}, {"text": correct, "is_correct": True},
        {"text": wrong[1], "is_correct": False}, {"text": wrong[2], "is_correct": False},
    ]}


def decimal_pair(value):
    digits = len(value.split(",")[1])
    numerator = int(value.replace(",", ""))
    return [numerator, 10 ** digits]


def compare(left, right, label):
    lv, rv = float(left.replace(",", ".")), float(right.replace(",", "."))
    relation = "<" if lv < rv else ">" if lv > rv else "="
    return iq(f"Compară {left} și {right} ({label}).", "fraction_compare", {"mode": "symbol", "left": decimal_pair(left), "right": decimal_pair(right), "left_label": left, "right_label": right, "relation": relation}, f"Comparăm mai întâi părțile întregi, apoi zecimalele: {left} {relation} {right}.")


def order(values, direction, label):
    items = [{"label": value, "numerator": decimal_pair(value)[0], "denominator": decimal_pair(value)[1]} for value in values]
    indices = sorted(range(len(values)), key=lambda i: float(values[i].replace(",", ".")), reverse=direction == "desc")
    display = list(reversed(range(len(values))))
    return iq(f"Ordonează fracțiile zecimale {label}.", "fraction_compare", {"mode": "order", "direction": direction, "items": items, "correct_order": indices, "display_order": display}, f"Ordinea corectă este: {', '.join(values[i] for i in indices)}.")


def axis(value, denominator, maximum, label):
    tick = round(float(value.replace(",", ".")) * denominator)
    return iq(f"Reprezintă {value} pe axa numerelor ({label}).", "fraction_axis", {"mode": "place", "target_numerator": tick, "denominator": denominator, "maximum": maximum, "answer_tick": tick, "target_label": value}, f"Împărțim unitatea în {denominator} părți egale și alegem gradația corespunzătoare lui {value}.")


def rounding(value, order, answer, label):
    data = {"mode": "missing", "expression": f"Rotunjește {value} la ordinul {order}.", "fields": [{"key": "missing", "label": "Rezultatul rotunjirii"}], "answers": {"missing": answer}}
    return iq(f"Rotunjire {label}: {value} la ordinul {order}.", "decimal_workbench", data, f"Privim cifra imediat din dreapta ordinului cerut; rezultatul este {answer}.")


def build_questions():
    q = []
    for row in [("1,7", "1,8", "A"), ("23,5", "23,51", "B"), ("304,2", "204,2", "C"), ("15,7", "15,70", "D"), ("0,34", "0,44", "E"), ("0,07", "0,007", "F"), ("3,8", "3,4", "G"), ("5,29", "5,43", "H")]:
        q.append(compare(*row))
    q += [
        order(["7,9", "0,5", "4,25", "0,09", "63,7"], "asc", "A, crescător"),
        order(["2,7", "3,8", "1,7", "0,95", "0,03", "0,45"], "desc", "B, descrescător"),
        order(["0,123", "1,23", "12,3", "0,0123"], "asc", "C, crescător"),
        order(["5,875", "23,4", "5,9876", "0,74"], "desc", "D, descrescător"),
    ]
    q += [axis(*row) for row in [("0,7", 10, 1, "A"), ("1,5", 10, 2, "B"), ("2,3", 10, 3, "C"), ("1,4", 10, 2, "D"), ("3,6", 10, 4, "E"), ("2,8", 10, 3, "F")]]
    q += [rounding(*row) for row in [("23,145", "unităților", "23", "A"), ("13,5", "unităților", "14", "B"), ("423,7", "zecilor", "420", "C"), ("4,279", "zecimilor", "4,3", "D"), ("0,3651", "sutimi", "0,37", "E"), ("8,25346", "miimi", "8,253", "F")]]
    q += [
        grid("Care număr este mai mare?", "306,99", ["306,9", "306,09", "306,099"], "Părțile întregi sunt egale; 99 sutimi sunt mai multe decât 9 zecimi."),
        grid("Care este ordinea crescătoare corectă?", "0,09 < 0,5 < 4,25", ["0,5 < 0,09 < 4,25", "4,25 < 0,5 < 0,09", "0,09 < 4,25 < 0,5"], "Comparăm părțile întregi și apoi cifrele zecimale."),
        grid("Rotunjirea lui 6,782 la sutimi este:", "6,78", ["6,79", "6,8", "6,782"], "Cifra miimilor este 2, deci cifra sutimilor rămâne neschimbată."),
    ]
    assert len(q) == 27
    return q


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_fractii_zecimale_aproximarea_compararea_ordonarea_axa.json"
    payload = {"title": "Aproximări; compararea, ordonarea și reprezentarea pe axa numerelor a unor fracții zecimale cu un număr finit de zecimale", "description": "Clasa a 5-a · Fracții zecimale", "difficulty": "medium", "questions": build_questions()}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
