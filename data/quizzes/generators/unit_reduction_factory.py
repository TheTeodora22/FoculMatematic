"""Constructori siguri pentru exercițiile despre metoda reducerii la unitate.

Acest modul nu scrie lecția în baza de date. Generatorul lecției îl va importa
și va furniza ulterior enunțurile și valorile concrete.
"""

from fractions import Fraction


DIRECT = "direct"
INVERSE = "inverse"


def _exercise(text, mode, data, explanation, *, true_false=False):
    if not text.strip() or not explanation.strip():
        raise ValueError("Enunțul și explicația sunt obligatorii.")
    return {
        "text": text,
        "type": "unit_reduction",
        "format": "true_false" if true_false else "interactive",
        "points": 10,
        "explanation": explanation,
        "interactive": {"mode": mode, **data},
    }


def _related_value(initial_quantity, initial_value, target_quantity, relation):
    if min(initial_quantity, initial_value, target_quantity) <= 0:
        raise ValueError("Valorile trebuie să fie pozitive.")
    if relation == DIRECT:
        result = Fraction(initial_value * target_quantity, initial_quantity)
    elif relation == INVERSE:
        result = Fraction(initial_value * initial_quantity, target_quantity)
    else:
        raise ValueError("Relația trebuie să fie directă sau inversă.")
    if result.denominator != 1:
        raise ValueError("Exercițiul trebuie să aibă un rezultat natural.")
    return result.numerator


def visual_scale(text, initial_quantity, initial_value, target_quantity, unit, icon, explanation):
    target_value = _related_value(initial_quantity, initial_value, target_quantity, DIRECT)
    return _exercise(text, "visual_scale", {
        "initial_quantity": initial_quantity, "initial_value": initial_value,
        "target_quantity": target_quantity, "target_value": target_value,
        "unit": unit, "icon": icon, "answers": {"quantity": target_quantity, "value": target_value},
    }, explanation)


def unit_path(text, initial_quantity, initial_value, target_quantity, unit, explanation):
    target_value = _related_value(initial_quantity, initial_value, target_quantity, DIRECT)
    if initial_value % initial_quantity:
        raise ValueError("Valoarea unei unități trebuie să fie naturală.")
    return _exercise(text, "unit_path", {
        "values": [initial_quantity, 1, target_quantity],
        "paired_values": [initial_value, initial_value // initial_quantity, target_value],
        "unit": unit,
        "operation_choices": [f": {initial_quantity}", f"× {target_quantity}", f"× {initial_quantity}", f": {target_quantity}"],
        "answers": {"operation:0": f": {initial_quantity}", "operation:1": f"× {target_quantity}"},
    }, explanation)


def balance(text, initial_quantity, initial_value, target_quantity, relation, labels, explanation):
    target_value = _related_value(initial_quantity, initial_value, target_quantity, relation)
    return _exercise(text, "balance", {
        "initial_quantity": initial_quantity, "initial_value": initial_value,
        "target_quantity": target_quantity, "target_value": target_value,
        "relation": relation, "labels": labels,
        "answers": {"quantity": target_quantity, "value": target_value},
    }, explanation)


def basket(text, unit_price, target_quantity, icon, currency, explanation):
    if min(unit_price, target_quantity) <= 0:
        raise ValueError("Prețul și cantitatea trebuie să fie pozitive.")
    return _exercise(text, "basket", {
        "unit_price": unit_price, "target_quantity": target_quantity,
        "icon": icon, "currency": currency,
        "answers": {"count": target_quantity, "total": unit_price * target_quantity},
    }, explanation)


def faucets(text, initial_count, initial_time, target_count, icon, explanation):
    target_time = _related_value(initial_count, initial_time, target_count, INVERSE)
    return _exercise(text, "faucets", {
        "initial_count": initial_count, "initial_time": initial_time,
        "target_count": target_count, "target_time": target_time, "icon": icon,
        "answers": {"count": target_count, "time": target_time},
    }, explanation)


def dependency_direction(text, first_change, second_change, relation, explanation):
    if relation not in {DIRECT, INVERSE}:
        raise ValueError("Relația trebuie să fie directă sau inversă.")
    return _exercise(text, "dependency_direction", {
        "first_change": first_change, "second_change": second_change,
        "answers": {"relation": relation},
    }, explanation)


def unit_table(text, rows, columns, explanation):
    answers = {}
    for index, row in enumerate(rows):
        missing = row.get("missing")
        if missing not in columns or missing not in row:
            raise ValueError("Fiecare rând trebuie să aibă o celulă lipsă validă.")
        answers[f"{index}:{missing}"] = row[missing]
    return _exercise(text, "unit_table", {"columns": columns, "rows": rows, "answers": answers}, explanation)


def operation_drop(text, nodes, correct_operations, distractors, explanation):
    if len(nodes) < 3 or len(correct_operations) != len(nodes) - 1:
        raise ValueError("Drumul trebuie să aibă câte o operație între noduri.")
    raw_choices = list(dict.fromkeys([*correct_operations, *distractors]))
    choices = raw_choices[1::2] + raw_choices[::2]
    return _exercise(text, "operation_drop", {
        "nodes": nodes, "operation_choices": choices,
        "answers": {f"operation:{index}": operation for index, operation in enumerate(correct_operations)},
    }, explanation)


def timeline(text, minimum, maximum, step, target_time, initial_label, target_label, explanation):
    if not minimum <= target_time <= maximum or step <= 0:
        raise ValueError("Poziția corectă trebuie să fie pe banda timpului.")
    return _exercise(text, "timeline", {
        "minimum": minimum, "maximum": maximum, "step": step,
        "target_time": target_time, "initial_label": initial_label, "target_label": target_label,
        "answers": {"time": target_time},
    }, explanation)


def problem_builder(text, contexts, questions, relations, correct_indices, explanation):
    if len(correct_indices) != 3 or any(index < 0 for index in correct_indices):
        raise ValueError("Sunt necesare trei alegeri corecte.")
    return _exercise(text, "problem_builder", {
        "groups": [
            {"label": "Context", "choices": contexts},
            {"label": "Întrebare", "choices": questions},
            {"label": "Legătură", "choices": relations},
        ],
        "answers": {f"choice:{index}": choice for index, choice in enumerate(correct_indices)},
    }, explanation)


def speed_simulator(text, speed, target_distance, maximum_time, icon, explanation):
    if min(speed, target_distance, maximum_time) <= 0 or target_distance % speed:
        raise ValueError("Distanța trebuie să fie un multiplu natural al vitezei.")
    target_time = target_distance // speed
    if target_time > maximum_time:
        raise ValueError("Timpul corect depășește simulatorul.")
    return _exercise(text, "speed_simulator", {
        "speed": speed, "target_distance": target_distance, "maximum_time": maximum_time,
        "target_time": target_time, "icon": icon, "answers": {"time": target_time},
    }, explanation)


def triple_match(text, triples, explanation):
    if len(triples) < 3 or any(set(triple) != {"problem", "scheme", "answer"} for triple in triples):
        raise ValueError("Sunt necesare cel puțin trei triplete complete.")
    return _exercise(text, "triple_match", {
        "triples": triples,
        "scheme_order": list(range(1, len(triples))) + [0],
        "answer_order": list(range(2, len(triples))) + [0, 1],
        "answers": {
            **{f"scheme:{index}": index for index in range(len(triples))},
            **{f"answer:{index}": index for index in range(len(triples))},
        },
    }, explanation)


def visual_true_false(text, statement, is_true, icon, visual_note, explanation):
    return _exercise(text, "visual_true_false", {
        "statement": statement, "icon": icon, "visual_note": visual_note,
        "answers": {"answer": "true" if is_true else "false"},
    }, explanation, true_false=True)
