"""Constructori pentru exercițiile interactive ale metodei comparației."""


def _exercise(text, mode, data, explanation, *, true_false=False):
    if not text.strip() or not explanation.strip():
        raise ValueError("Enunțul și explicația sunt obligatorii.")
    return {"text": text, "type": "comparison_method", "format": "true_false" if true_false else "interactive", "points": 10, "explanation": explanation, "interactive": {"mode": mode, **data}}


def two_rows(text, mode, rows, answers, explanation, **extra):
    if mode not in {"balance", "cancel_common", "align_rows", "equalize", "comparison_table"}:
        raise ValueError("Mod de comparație invalid.")
    if len(rows) != 2 or any(not isinstance(row.get("items"), list) or not isinstance(row.get("total"), int) for row in rows):
        raise ValueError("Sunt necesare două situații complete.")
    return _exercise(text, mode, {"rows": rows, "answers": answers, **extra}, explanation)


def choose_method(text, situation, correct, explanation):
    if correct not in {"subtract", "add", "substitute"}:
        raise ValueError("Metodă invalidă.")
    return _exercise(text, "choose_method", {"situation": situation, "answers": {"method": correct}}, explanation)


def substitution(text, source_group, target_group, large_row, result_row, answers, explanation):
    return _exercise(text, "substitution_machine", {"source_group": source_group, "target_group": target_group, "large_row": large_row, "result_row": result_row, "answers": answers}, explanation)


def error_detective(text, steps, error_index, explanation):
    if len(steps) < 3 or not 0 <= error_index < len(steps):
        raise ValueError("Pași invalizi.")
    return _exercise(text, "comparison_error", {"steps": steps, "answers": {"step": error_index}}, explanation)


def animal_race(text, animal_a, animal_b, common_period, lead, answers, explanation):
    return _exercise(text, "animal_race", {"animal_a": animal_a, "animal_b": animal_b, "common_period": common_period, "lead": lead, "answers": answers}, explanation)


def dancers(text, initial_boys, initial_girls, initial_time, target_boys, target_girls, target_time, explanation):
    return _exercise(text, "dancers", {"initial_boys": initial_boys, "initial_girls": initial_girls, "initial_time": initial_time, "target_boys": target_boys, "target_girls": target_girls, "answers": {"boys": target_boys, "girls": target_girls, "time": target_time}}, explanation)


def triple_match(text, triples, explanation):
    if len(triples) < 3:
        raise ValueError("Sunt necesare cel puțin trei triplete.")
    return _exercise(text, "comparison_match", {"triples": triples, "scheme_order": list(range(1, len(triples))) + [0], "answer_order": list(range(2, len(triples))) + [0, 1], "answers": {**{f"scheme:{i}": i for i in range(len(triples))}, **{f"answer:{i}": i for i in range(len(triples))}}}, explanation)


def visual_true_false(text, statement, answer, icon, note, explanation):
    return _exercise(text, "comparison_true_false", {"statement": statement, "icon": icon, "note": note, "answers": {"answer": "true" if answer else "false"}}, explanation, true_false=True)
