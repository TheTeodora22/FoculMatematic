"""Generează prima lecție despre fracțiile zecimale pentru clasa a V-a."""

import json
from pathlib import Path


def iq(text, kind, data, explanation):
    return {"text": text, "type": kind, "format": "interactive", "points": 10, "interactive": data, "explanation": explanation}


def grid(text, correct, wrong, explanation):
    correct, wrong = str(correct), [str(value) for value in wrong]
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3
    return {"text": text, "format": "grid", "points": 10, "explanation": explanation, "options": [
        {"text": wrong[0], "is_correct": False}, {"text": correct, "is_correct": True},
        {"text": wrong[1], "is_correct": False}, {"text": wrong[2], "is_correct": False},
    ]}


def fields(answers, labels=None):
    labels = labels or {}
    return [{"key": key, "label": labels.get(key, key)} for key in answers]


def comma(digits, places, decimal, label):
    position = len(digits) - places
    return iq(f"Mută virgula {label}: scrie {digits}/{10 ** places} ca fracție zecimală.", "decimal_workbench", {"mode": "comma", "digits": digits, "places": places, "answers": {"position": position}}, f"Numitorul are {places} zerouri, deci virgula se așază cu {places} cifre de la dreapta: {decimal}.")


def ordinary_to_decimal(numerator, denominator, decimal, label):
    answers = {"decimal": decimal}
    return iq(f"Transformă fracția {numerator}/{denominator} în fracție zecimală ({label}).", "decimal_workbench", {"mode": "conversion", "source": f"{numerator}/{denominator}", "target_kind": "decimal", "fields": fields(answers), "answers": answers}, f"Numitorul {denominator} stabilește numărul cifrelor de după virgulă: rezultatul este {decimal}.")


def decimal_to_ordinary(decimal, numerator, denominator, label, build=False):
    answers = {"numerator": numerator, "denominator": denominator}
    return iq(f"Construiește fracția ordinară pentru {decimal} ({label}).", "decimal_workbench", {"mode": "build_fraction" if build else "conversion", "source": decimal, "decimal": decimal, "target_kind": "fraction", "fields": fields(answers), "answers": answers}, f"Eliminăm virgula pentru numărător și folosim {denominator} la numitor: {numerator}/{denominator}.")


def matching(pairs, label):
    return iq(f"Potrivește reprezentările echivalente ({label}).", "factor_match", {"pairs": [{"left": left, "right": right} for left, right in pairs], "right_order": list(reversed(range(len(pairs))))}, "Fiecare fracție cu numitor 10, 100 sau 1 000 se scrie zecimal numărând pozițiile după virgulă.")


def place_value(decimal, digits, label):
    column_defs = [("units", "Unități"), ("tenths", "Zecimi"), ("hundredths", "Sutimi"), ("thousandths", "Miimi")]
    answers = {key: value for (key, _), value in zip(column_defs, digits)}
    return iq(f"Completează tabelul pozițional pentru {decimal} ({label}).", "decimal_workbench", {"mode": "place_value", "decimal": decimal, "columns": [{"key": key, "label": title} for key, title in column_defs], "fields": fields(answers), "answers": answers}, f"În {decimal}, cifrele se citesc pe coloane de la unități spre zecimi, sutimi și miimi.")


def words(text, decimal, label):
    answers = {"decimal": decimal}
    return iq(f"Scrie cu cifre enunțul {label}.", "decimal_workbench", {"mode": "words", "words": text, "fields": fields(answers), "answers": answers}, f"Scrierea corectă este {decimal}.")


def decompose(decimal, values, label, construct=False):
    answers = {f"part:{index}": value for index, value in enumerate(values)}
    verb = "Construiește" if construct else "Completează"
    return iq(f"{verb} descompunerea pe ordine a numărului {decimal} ({label}).", "decimal_workbench", {"mode": "decompose", "decimal": decimal, "parts": values, "fields": fields(answers), "answers": answers}, f"{decimal} = {values[0]} + " + " + ".join(f"{value}/{10 ** index}" for index, value in enumerate(values[1:], 1)) + ".")


def amplify(numerator, denominator, factor, decimal, label):
    target = denominator * factor
    answers = {"factor": factor, "new_numerator": numerator * factor, "decimal": decimal}
    return iq(f"Amplifică și transformă fracția {numerator}/{denominator} ({label}).", "decimal_workbench", {"mode": "amplify", "numerator": numerator, "denominator": denominator, "target_denominator": target, "fields": fields(answers), "answers": answers}, f"Amplificăm cu {factor}: {numerator}/{denominator} = {numerator * factor}/{target} = {decimal}.")


def simple_fields(mode, text, expression, answers, explanation):
    labels = {key: ("Numărul natural n" if key == "n" else "Numitorul" if key == "denominator" else "Valoarea lipsă") for key in answers}
    return iq(text, "decimal_workbench", {"mode": mode, "expression": expression, "fields": fields(answers, labels), "answers": answers}, explanation)


def zero_chain(start, forms, label):
    answers = {f"form:{index}": value for index, value in enumerate(forms)}
    return iq(f"Completează lanțul de forme echivalente ({label}).", "decimal_workbench", {"mode": "zeros", "start": start, "fields": fields(answers, {key: f"Forma {index + 2}" for index, key in enumerate(answers)}), "answers": answers}, "Zerourile adăugate după ultima cifră zecimală nu schimbă valoarea numărului.")


def select_equivalent(target, cards, correct, label):
    return iq(f"Selectează toate formele echivalente cu {target} ({label}).", "divisibility_select", {"mode": "criteria", "cards": [{"id": str(index), "label": card} for index, card in enumerate(cards)], "correct_ids": [str(index) for index in correct]}, "Formele selectate reprezintă aceeași valoare, chiar dacă au un număr diferit de zerouri sau altă reprezentare fracționară.")


def sort_families(families, label):
    zones = [{"id": f"z{index}", "label": family[0]} for index, family in enumerate(families)]
    cards = []
    for index, (_, representations) in enumerate(families):
        cards.extend({"id": f"z{index}c{card_index}", "label": value, "zone": f"z{index}"} for card_index, value in enumerate(representations))
    return iq(f"Sortează reprezentările pe familii echivalente ({label}).", "divisibility_sort", {"mode": "two_zones", "zones": zones, "cards": cards}, "Fiecare zonă reunește fracția zecimală și fracțiile ordinare cu aceeași valoare.")


def axis(numerator, denominator, maximum, decimal, label):
    return iq(f"Așază {decimal} pe axa numerelor ({label}).", "fraction_axis", {"mode": "place", "target_numerator": numerator, "denominator": denominator, "maximum": maximum, "answer_tick": numerator}, f"{decimal} = {numerator}/{denominator}, deci punctul se află la gradația {numerator} din {denominator * maximum}.")


def vessel(filled, decimal, label):
    answers = {"filled": filled}
    return iq(f"Umple vasul gradat până la {decimal} ({label}).", "decimal_workbench", {"mode": "vessel", "segments": 10, "filled": filled, "target_label": decimal, "answers": answers}, f"Vasul are 10 părți egale; {filled} părți reprezintă {filled}/10 = {decimal}.")


def build_questions():
    q = []
    q += [comma("325", 1, "32,5", "A"), comma("9", 2, "0,09", "B"), comma("7", 3, "0,007", "C")]
    q += [ordinary_to_decimal(*row) for row in [(78, 10, "7,8", "A"), (37, 100, "0,37", "B"), (4567, 1000, "4,567", "C"), (7, 10000, "0,0007", "D")]]
    q += [decimal_to_ordinary(*row) for row in [("0,5", 5, 10, "A", False), ("4,35", 435, 100, "B", False), ("0,123", 123, 1000, "C", False)]]
    q += [decimal_to_ordinary(*row) for row in [("0,53", 53, 100, "A", True), ("6,584", 6584, 1000, "B", True)]]
    q += [
        matching([("7/10", "0,7"), ("23/100", "0,23"), ("9/1000", "0,009")], "A"),
    ]
    q += [place_value(*row) for row in [("47,392", [7, 3, 9, 2], "A"), ("5,234", [5, 2, 3, 4], "B")]]
    q += [words(*row) for row in [("trei zecimi", "0,3", "A"), ("doi întregi și șapte sutimi", "2,07", "B")]]
    q += [decompose(*row) for row in [("6,584", [6, 5, 8, 4], "A", False), ("47,392", [47, 3, 9, 2], "B", False)]]
    q += [decompose(*row) for row in [("2,34", [2, 3, 4], "A", True), ("12,075", [12, 0, 7, 5], "B", True)]]
    q += [amplify(*row) for row in [(3, 25, 4, "0,12", "A"), (4, 125, 8, "0,032", "B"), (21, 4, 25, "5,25", "C")]]
    q += [
        simple_fields("missing", "Completează valoarea lipsă A.", "□/100 = 0,43", {"missing": 43}, "43/100 = 0,43."),
        simple_fields("missing", "Completează valoarea lipsă B.", "4,□5 = 435/100", {"missing": 3}, "435/100 = 4,35."),
        simple_fields("natural_n", "Determină numărul natural n (A).", "6,37 = n/100", {"n": 637}, "Eliminăm virgula: n = 637."),
        simple_fields("natural_n", "Determină numărul natural n (B).", "4,187 = n/1000", {"n": 4187}, "Sunt trei zecimale, deci n = 4187."),
        simple_fields("denominator", "Completează numitorul potrivit A.", "0,37 = 37/□", {"denominator": 100}, "Două zecimale înseamnă numitorul 100."),
        simple_fields("denominator", "Completează numitorul potrivit B.", "4,007 = 4007/□", {"denominator": 1000}, "Trei zecimale înseamnă numitorul 1000."),
    ]
    q += [zero_chain(*row) for row in [("0,3", ["0,30", "0,300"], "A"), ("4,5", ["4,50", "4,500"], "B")]]
    q += [
        select_equivalent("0,3", ["3/10", "0,30", "30/100", "3/100", "0,03"], [0, 1, 2], "A"),
        select_equivalent("2,34", ["234/100", "2,340", "2340/1000", "23,4", "234/1000"], [0, 1, 2], "B"),
    ]
    q += [
        sort_families([("0,2", ["2/10", "20/100"]), ("0,4", ["4/10", "40/100"])], "A"),
        sort_families([("0,03", ["3/100", "30/1000"]), ("0,3", ["3/10", "300/1000"])], "B"),
    ]
    q += [vessel(*row) for row in [(3, "0,3", "A"), (7, "0,7", "B")]]
    q += [
        grid("Scrierea zecimală a fracției 128/100 este:", "1,28", ["12,8", "0,128", "0,0128"], "Numitorul 100 cere două cifre după virgulă."),
        grid("Fracția ordinară corespunzătoare lui 11,08 este:", "1108/100", ["11/8", "118/10", "1108/10"], "Eliminăm virgula și folosim numitorul 100."),
    ]
    assert len(q) == 40, len(q)
    assert len({item["text"] for item in q}) == 40
    return q


def main():
    output = Path(__file__).resolve().parent.parent / "clasa_5_fractii_zecimale.json"
    payload = {"title": "Fracții zecimale; scrierea fracțiilor ordinare cu numitorul puteri ale lui 10 sub formă de fracții zecimale; transformarea unei fracții zecimale cu un număr finit de zecimale nenule în fracție ordinară", "description": "Clasa a 5-a · Fracții zecimale", "difficulty": "medium", "questions": build_questions()}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exerciții în {output.name}")


if __name__ == "__main__":
    main()
