"""Curăță grilele repetitive și adaugă exercițiile interactive de adunare."""

import json
from pathlib import Path


OUTPUT = Path(__file__).resolve().parent.parent / "clasa_5_operatii_adunarea_numerelor_naturale.json"

KEEP_MC_NUMBERS = {
    1, 3, 5, 7,
    9, 12, 13, 15, 16,
    17, 19, 20,
    21, 23, 24,
    27, 28, 29, 30,
    31, 33,
    35, 37, 38,
    39, 40,
    41, 42, 43, 44,
    45, 47,
    49, 50,
    51, 52,
    55, 57, 58,
    61, 62,
}


def interactive_q(text, question_type, interactive, explanation):
    return {
        "text": text,
        "type": question_type,
        "points": 10,
        "explanation": explanation,
        "interactive": interactive,
    }


def carry_columns(addend1: int, addend2: int) -> list[bool]:
    first = str(addend1)
    second = str(addend2).zfill(len(first))
    carries = [False] * len(first)
    carry = 0
    for index in range(len(first) - 1, -1, -1):
        total = int(first[index]) + int(second[index]) + carry
        carry = int(total >= 10)
        if carry and index > 0:
            carries[index - 1] = True
    assert carry == 0, "Exemplele trebuie să păstreze același număr de coloane."
    return carries


def build_interactive_questions():
    questions = []

    column_values = [
        (468, 357),
        (2_384, 4_675),
        (5_726, 1_847),
        (3_408, 2_576),
        (6_157, 2_786),
        (42_315, 35_678),
    ]
    for addend1, addend2 in column_values:
        result = addend1 + addend2
        questions.append(
            interactive_q(
                f"Calculează în coloană suma {addend1:,} + {addend2:,}.".replace(",", " "),
                "column_addition",
                {
                    "addend1": str(addend1),
                    "addend2": str(addend2),
                    "correct_result": str(result),
                    "carry_columns": carry_columns(addend1, addend2),
                },
                f"Suma este {result:,}. Marcăm coloanele în care ajunge un transport.".replace(",", " "),
            )
        )

    missing_values = [
        (357, 245, ["addend1:1", "addend2:1"]),
        (448, 176, ["addend1:2", "result:1"]),
        (2_384, 4_675, ["addend1:1", "addend2:2", "result:2"]),
        (5_726, 1_847, ["addend1:2", "addend2:1", "result:3"]),
        (6_157, 2_786, ["addend2:2", "result:1", "result:3"]),
        (42_315, 35_678, ["addend1:3", "addend2:1", "result:2"]),
    ]
    for addend1, addend2, missing in missing_values:
        result = addend1 + addend2
        rows = {"addend1": str(addend1), "addend2": str(addend2), "result": str(result)}
        masked = dict(rows)
        for key in missing:
            row_name, raw_index = key.split(":")
            index = int(raw_index)
            masked[row_name] = masked[row_name][:index] + "□" + masked[row_name][index + 1:]
        questions.append(
            interactive_q(
                f"Completează adunarea {masked['addend1']} + {masked['addend2']} = {masked['result']}.",
                "missing_digits",
                {
                    "operation": "add",
                    "addend1": str(addend1),
                    "addend2": str(addend2),
                    "result": str(result),
                    "missing": missing,
                },
                f"Adunarea completă este {addend1:,} + {addend2:,} = {result:,}.".replace(",", " "),
            )
        )

    error_values = [
        (468, 357, 815, 1),
        (2_384, 4_675, 7_049, 2),
        (5_726, 1_847, 7_473, 1),
        (3_408, 2_576, 5_994, 2),
        (6_157, 2_786, 8_843, 1),
        (42_315, 35_678, 77_983, 3),
    ]
    for addend1, addend2, shown_result, error_column in error_values:
        correct_result = addend1 + addend2
        questions.append(
            interactive_q(
                f"Un elev a scris {addend1:,} + {addend2:,} = {shown_result:,}. Apasă coloana în care a greșit.".replace(",", " "),
                "error_spotting",
                {
                    "operation": "add",
                    "addend1": str(addend1),
                    "addend2": str(addend2),
                    "shown_result": str(shown_result),
                    "correct_result": str(correct_result),
                    "error_column": error_column,
                },
                f"Suma corectă este {correct_result:,}.".replace(",", " "),
            )
        )

    machine_values = [
        (125, [(775, None), (None, 900), (1_200, None)]),
        (240, [(385, None), (None, 1_000), (2_500, None)]),
        (375, [(625, None), (None, 1_575), (3_000, None)]),
        (1_025, [(2_500, None), (None, 4_000), (5_200, None)]),
        (2_350, [(4_650, None), (None, 10_000), (12_000, None)]),
        (4_075, [(5_925, None), (None, 15_000), (20_000, None)]),
    ]
    for value, raw_rows in machine_values:
        questions.append(
            interactive_q(
                f"Mașina adună {value:,} la fiecare număr introdus. Completează căsuțele.".replace(",", " "),
                "input_output",
                {
                    "operation": "add",
                    "value": value,
                    "rows": [
                        {"input": input_value, "output": output_value}
                        for input_value, output_value in raw_rows
                    ],
                },
                "Pentru ieșire adunăm regula; pentru o intrare lipsă scădem regula din ieșire.",
            )
        )

    assert len(questions) == 24
    return questions


def main():
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    original_mc = [q for q in payload["questions"] if q.get("type", "multiple_choice") == "multiple_choice"]
    if len(original_mc) >= 62:
        selected_texts = {
            question["text"]
            for number, question in enumerate(original_mc, start=1)
            if number in KEEP_MC_NUMBERS
        }
    else:
        selected_texts = {question["text"] for question in original_mc}

    kept_mc = [question for question in original_mc if question["text"] in selected_texts]
    parentheses = [q for q in payload["questions"] if q.get("type") == "parentheses_drag"]
    payload["questions"] = kept_mc + parentheses[:6] + build_interactive_questions()
    assert len(kept_mc) == 41, len(kept_mc)
    assert len(parentheses[:6]) == 6
    assert len(payload["questions"]) == 71
    assert len({q["text"] for q in payload["questions"]}) == len(payload["questions"])
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scrise {len(payload['questions'])} exercitii in {OUTPUT.name}")


if __name__ == "__main__":
    main()
