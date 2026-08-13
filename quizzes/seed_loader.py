"""
Încarcă capitole și subiecte din data/quizzes/.

După migrate sau reset DB rulezi:
    python manage.py seed_quizzes
"""

import json
import re
from pathlib import Path

from django.conf import settings
from django.db import transaction

from quizzes.lesson_tags import normalize_class_levels, normalize_exam_slugs
from quizzes.models import AnswerOption, Chapter, Question, Quiz

DIFFICULTIES = {"easy", "medium", "hard"}
QUESTION_TYPES = {
    "multiple_choice",
    "parentheses_drag",
    "column_addition",
    "column_multiplication",
    "column_division",
    "column_subtraction",
    "missing_digits",
    "error_spotting",
    "parentheses_target",
    "input_output",
    "division_relation",
    "operation_chain",
    "division_table",
    "numeric_input",
    "factor_builder",
    "factor_error",
    "factor_match",
    "power_builder",
    "power_match",
    "power_table",
    "power_cycle",
    "power_square",
    "power_rule_chain",
    "power_compare",
    "power_order",
    "base_values",
    "base_match",
    "binary_toggle",
    "base_error",
    "unit_reduction",
    "comparison_method",
    "figurative_method",
    "reverse_method",
    "false_hypothesis_method",
    "operation_sequence",
    "operation_workbench",
    "divisibility_values",
    "divisibility_select",
    "divisibility_sort",
    "divisibility_error",
    "criteria_table",
    "prime_workbench",
    "decimal_workbench",
    "fraction_visual",
    "fraction_domino",
    "fraction_compare",
    "fraction_axis",
    "gcd_workbench",
    "fraction_scale",
    "fraction_reduce_path",
    "lcm_workbench",
    "common_denominator",
}
QUESTION_FORMATS = {"grid", "true_false", "interactive"}
CHAPTERS_MANIFEST = "chapters.json"


class SeedValidationError(Exception):
    pass


def quizzes_data_dir() -> Path:
    return Path(settings.BASE_DIR) / "data" / "quizzes"


def _valid_digit_string(value) -> bool:
    return isinstance(value, str) and bool(value) and value.isdigit()


def _expected_borrow_columns(minuend: str, subtrahend: str) -> list[bool]:
    top = [int(digit) for digit in minuend]
    bottom = [int(digit) for digit in subtrahend]
    borrows = [False] * len(top)
    for index in range(len(top) - 1, -1, -1):
        if top[index] >= bottom[index]:
            continue
        lender = index - 1
        while lender >= 0 and top[lender] == 0:
            top[lender] = 9
            borrows[lender] = True
            lender -= 1
        if lender < 0:
            raise ValueError("Scăderea nu este posibilă în numere naturale.")
        top[lender] -= 1
        top[index] += 10
        borrows[index] = True
    return borrows


def _expected_carry_columns(addend1: str, addend2: str) -> list[bool]:
    carries = [False] * len(addend1)
    carry = 0
    for index in range(len(addend1) - 1, -1, -1):
        total = int(addend1[index]) + int(addend2[index]) + carry
        carry = 1 if total >= 10 else 0
        if carry and index > 0:
            carries[index - 1] = True
    return carries


def _parse_expression_tokens(tokens: list[str]) -> tuple[list[int], list[str | None]]:
    values = []
    operators: list[str | None] = []
    for index, raw_token in enumerate(tokens):
        token = raw_token.strip().replace(" ", "")
        if index == 0:
            if not token.isdigit():
                raise ValueError("Primul termen trebuie să fie număr natural.")
            values.append(int(token))
            operators.append(None)
            continue
        match = re.fullmatch(r"([+−\-·×*:])(\d+)", token)
        if not match:
            raise ValueError("Expresia conține o operație neacceptată.")
        symbol = match.group(1)
        operators.append("−" if symbol in {"−", "-"} else "·" if symbol in {"·", "×", "*"} else ":" if symbol == ":" else "+")
        values.append(int(match.group(2)))
    return values, operators


def _evaluate_flat_expression(values: list[int], operators: list[str | None]) -> int:
    reduced_values = list(values)
    reduced_operators = list(operators)
    index = 1
    while index < len(reduced_values):
        operator = reduced_operators[index]
        if operator not in {"·", ":"}:
            index += 1
            continue
        left, right = reduced_values[index - 1], reduced_values[index]
        if operator == ":" and (right == 0 or left % right):
            raise ValueError("Împărțirile din expresie trebuie să fie exacte.")
        result = left * right if operator == "·" else left // right
        reduced_values[index - 1:index + 1] = [result]
        reduced_operators[index - 1:index + 1] = [reduced_operators[index - 1]]
        index = max(1, index - 1)
    result = reduced_values[0]
    for index in range(1, len(reduced_values)):
        result = result + reduced_values[index] if reduced_operators[index] == "+" else result - reduced_values[index]
    return result


def _evaluate_parenthesized_tokens(tokens: list[str], open_index: int, close_index: int) -> int:
    values, operators = _parse_expression_tokens(tokens)

    grouped_operators = [None] + operators[open_index + 1:close_index]
    grouped = _evaluate_flat_expression(values[open_index:close_index], grouped_operators)

    reduced_values = values[:open_index] + [grouped] + values[close_index:]
    reduced_operators = operators[:open_index] + [operators[open_index]] + operators[close_index:]
    return _evaluate_flat_expression(reduced_values, reduced_operators)


def _validate_quiz_payload(data: dict, source: str) -> None:
    if not isinstance(data, dict):
        raise SeedValidationError(f"{source}: rădăcina trebuie să fie un obiect JSON.")

    for field in ("title", "difficulty", "questions"):
        if field not in data:
            raise SeedValidationError(f"{source}: lipsește câmpul '{field}'.")

    if data["difficulty"] not in DIFFICULTIES:
        raise SeedValidationError(
            f"{source}: difficulty trebuie să fie easy, medium sau hard."
        )

    if not isinstance(data["questions"], list):
        raise SeedValidationError(f"{source}: 'questions' trebuie să fie o listă.")

    if not data["questions"]:
        return

    for i, question in enumerate(data["questions"], start=1):
        if not question.get("text"):
            raise SeedValidationError(f"{source}: întrebarea {i} nu are text.")
        question_type = question.get("type", "multiple_choice")
        if question_type not in QUESTION_TYPES:
            raise SeedValidationError(
                f"{source}: întrebarea {i} are un tip necunoscut: {question_type}."
            )
        default_format = "grid" if question_type == "multiple_choice" else "interactive"
        question_format = question.get("format", default_format)
        if question_format not in QUESTION_FORMATS:
            raise SeedValidationError(
                f"{source}: întrebarea {i} are o etichetă necunoscută: {question_format}."
            )
        if question_type == "multiple_choice" and question_format == "interactive":
            raise SeedValidationError(
                f"{source}: întrebarea {i} este grilă, dar are eticheta Interactiv."
            )
        tagged_interactive_true_false = question_type in {"unit_reduction", "comparison_method", "figurative_method", "reverse_method"} and question_format == "true_false"
        if question_type != "multiple_choice" and question_format != "interactive" and not tagged_interactive_true_false:
            raise SeedValidationError(
                f"{source}: întrebarea {i} interactivă trebuie etichetată Interactiv."
            )
        if question_type in {"parentheses_drag", "parentheses_target"}:
            interactive = question.get("interactive", {})
            tokens = interactive.get("tokens")
            open_index = interactive.get("correct_open_index")
            close_index = interactive.get("correct_close_index")
            if not isinstance(tokens, list) or len(tokens) < 3 or not all(
                isinstance(token, str) and token.strip() for token in tokens
            ):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} trebuie să aibă minimum 3 token-uri valide."
                )
            if (
                not isinstance(open_index, int)
                or not isinstance(close_index, int)
                or not 0 <= open_index < close_index <= len(tokens)
            ):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are poziții invalide pentru paranteze."
                )
            if question_type == "parentheses_target":
                target = interactive.get("target")
                try:
                    evaluated = _evaluate_parenthesized_tokens(
                        tokens, open_index, close_index
                    )
                except ValueError as exc:
                    raise SeedValidationError(
                        f"{source}: întrebarea {i}: {exc}"
                    ) from exc
                if not isinstance(target, int) or evaluated != target:
                    raise SeedValidationError(
                        f"{source}: întrebarea {i} nu produce rezultatul-țintă."
                    )
            continue
        if question_type == "column_subtraction":
            interactive = question.get("interactive", {})
            minuend = interactive.get("minuend")
            subtrahend = interactive.get("subtrahend")
            result = interactive.get("correct_result")
            borrows = interactive.get("borrow_columns")
            if not all(_valid_digit_string(value) for value in (minuend, subtrahend, result)):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are date invalide pentru scăderea în coloană."
                )
            if not (len(minuend) == len(subtrahend) == len(result)):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} trebuie să aibă același număr de coloane."
                )
            expected_result = str(int(minuend) - int(subtrahend)).zfill(len(minuend))
            try:
                expected_borrows = _expected_borrow_columns(minuend, subtrahend)
            except ValueError as exc:
                raise SeedValidationError(f"{source}: întrebarea {i}: {exc}") from exc
            if result != expected_result or borrows != expected_borrows:
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are rezultatul sau împrumuturile greșite."
                )
            continue
        if question_type == "column_addition":
            interactive = question.get("interactive", {})
            addend1 = interactive.get("addend1")
            addend2 = interactive.get("addend2")
            result = interactive.get("correct_result")
            carries = interactive.get("carry_columns")
            if not all(_valid_digit_string(value) for value in (addend1, addend2, result)):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are date invalide pentru adunarea în coloană."
                )
            if len(addend1) != len(addend2) or len(result) not in {len(addend1), len(addend1) + 1}:
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are un număr invalid de coloane."
                )
            if int(addend1) + int(addend2) != int(result) or carries != _expected_carry_columns(addend1, addend2):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are rezultatul sau transporturile greșite."
                )
            continue
        if question_type == "column_multiplication":
            interactive = question.get("interactive", {})
            multiplicand = interactive.get("multiplicand")
            multiplier = interactive.get("multiplier")
            result = interactive.get("correct_result")
            carries = interactive.get("carry_columns")
            if not all(_valid_digit_string(value) for value in (multiplicand, multiplier, result)):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are date invalide pentru înmulțirea în coloană."
                )
            if len(multiplier) != 1 or int(multiplier) < 2 or int(multiplicand) * int(multiplier) != int(result):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} nu conține o înmulțire în coloană validă."
                )
            expected_carries = [False] * len(result)
            carry = 0
            offset = len(result) - len(multiplicand)
            for source_index in range(len(multiplicand) - 1, -1, -1):
                total = int(multiplicand[source_index]) * int(multiplier) + carry
                carry = total // 10
                target_index = offset + source_index - 1
                if carry and target_index >= 0:
                    expected_carries[target_index] = True
            if carries != expected_carries:
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are transporturile greșite."
                )
            continue
        if question_type == "column_division":
            interactive = question.get("interactive", {})
            dividend = interactive.get("dividend")
            divisor = interactive.get("divisor")
            quotient = interactive.get("quotient")
            remainder = interactive.get("remainder", dividend % divisor if isinstance(dividend, int) and isinstance(divisor, int) and divisor > 0 else None)
            remainders = interactive.get("remainders")
            if not all(isinstance(value, int) and value >= 0 for value in (dividend, quotient)) or not isinstance(divisor, int) or divisor <= 0:
                raise SeedValidationError(f"{source}: întrebarea {i} are date invalide pentru împărțirea în coloană.")
            if not isinstance(remainder, int) or remainder < 0 or remainder >= divisor or dividend // divisor != quotient or dividend % divisor != remainder:
                raise SeedValidationError(f"{source}: întrebarea {i} are câtul sau restul final greșit.")
            expected_remainders = []
            current = 0
            for digit in str(dividend):
                current = current * 10 + int(digit)
                expected_remainders.append(current % divisor)
                current %= divisor
            if remainders != expected_remainders:
                raise SeedValidationError(f"{source}: întrebarea {i} are resturile intermediare greșite.")
            continue
        if question_type == "missing_digits":
            interactive = question.get("interactive", {})
            operation = interactive.get("operation", "subtract")
            if operation == "add":
                row_names = ("addend1", "addend2", "result")
            elif operation == "multiply":
                row_names = ("factor1", "factor2", "result")
            elif operation == "divide":
                row_names = ("dividend", "divisor", "quotient")
            else:
                row_names = ("minuend", "subtrahend", "result")
            rows = [interactive.get(name) for name in row_names]
            missing = interactive.get("missing")
            if not all(_valid_digit_string(value) for value in rows) or len({len(value) for value in rows}) != 1:
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are rânduri invalide pentru cifre lipsă."
                )
            expected = {
                "add": int(rows[0]) + int(rows[1]),
                "subtract": int(rows[0]) - int(rows[1]),
                "multiply": int(rows[0]) * int(rows[1]),
                "divide": int(rows[0]) // int(rows[1]) if int(rows[1]) and int(rows[0]) % int(rows[1]) == 0 else None,
            }.get(operation)
            if expected is None or expected != int(rows[2]):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} nu conține un calcul corect."
                )
            if not isinstance(missing, list) or not missing or len(set(missing)) != len(missing):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} trebuie să precizeze cifrele lipsă."
                )
            for key in missing:
                allowed_rows = "|".join(row_names)
                match = re.fullmatch(rf"({allowed_rows}):(\d+)", str(key))
                if not match or int(match.group(2)) >= len(rows[0]):
                    raise SeedValidationError(
                        f"{source}: întrebarea {i} are o poziție lipsă invalidă."
                    )
            continue
        if question_type == "error_spotting":
            interactive = question.get("interactive", {})
            operation = interactive.get("operation", "subtract")
            if operation == "add":
                first_name, second_name = "addend1", "addend2"
            elif operation == "multiply":
                first_name, second_name = "factor1", "factor2"
            elif operation == "divide":
                first_name, second_name = "dividend", "divisor"
            else:
                first_name, second_name = "minuend", "subtrahend"
            first = interactive.get(first_name)
            second = interactive.get(second_name)
            shown = interactive.get("shown_result")
            correct = interactive.get("correct_result")
            error_column = interactive.get("error_column")
            values = (first, second, shown, correct)
            if not all(_valid_digit_string(value) for value in values) or len({len(value) for value in values}) != 1:
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are date invalide pentru detectarea greșelii."
                )
            differing = [index for index, pair in enumerate(zip(shown, correct)) if pair[0] != pair[1]]
            expected = {
                "add": int(first) + int(second),
                "subtract": int(first) - int(second),
                "multiply": int(first) * int(second),
                "divide": int(first) // int(second) if int(second) and int(first) % int(second) == 0 else None,
            }.get(operation)
            if expected is None or expected != int(correct) or differing != [error_column]:
                raise SeedValidationError(
                    f"{source}: întrebarea {i} nu are exact coloana greșită declarată."
                )
            continue
        if question_type == "input_output":
            interactive = question.get("interactive", {})
            operation = interactive.get("operation")
            value = interactive.get("value")
            rows = interactive.get("rows")
            if operation not in {"add", "subtract", "multiply", "divide"} or not isinstance(value, int) or value <= 0:
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are o regulă intrare–ieșire invalidă."
                )
            if not isinstance(rows, list) or len(rows) < 2:
                raise SeedValidationError(
                    f"{source}: întrebarea {i} trebuie să aibă minimum două rânduri."
                )
            for row in rows:
                input_value = row.get("input")
                output_value = row.get("output")
                if (input_value is None) == (output_value is None):
                    raise SeedValidationError(
                        f"{source}: întrebarea {i} trebuie să aibă exact o celulă lipsă pe rând."
                    )
                known = output_value if input_value is None else input_value
                if not isinstance(known, int) or known < 0:
                    raise SeedValidationError(
                        f"{source}: întrebarea {i} are o valoare intrare–ieșire invalidă."
                    )
                if operation == "subtract" and input_value is not None and input_value < value:
                    raise SeedValidationError(
                        f"{source}: întrebarea {i} ar produce un rezultat negativ."
                    )
                if operation == "multiply" and input_value is None and output_value % value != 0:
                    raise SeedValidationError(
                        f"{source}: întrebarea {i} nu are o intrare naturală pentru ieșirea dată."
                    )
                if operation == "divide" and input_value is not None and input_value % value != 0:
                    raise SeedValidationError(f"{source}: întrebarea {i} nu are o ieșire naturală.")
            continue
        if question_type == "division_relation":
            interactive = question.get("interactive", {})
            dividend, divisor, quotient = (interactive.get(key) for key in ("dividend", "divisor", "quotient"))
            remainder = interactive.get("remainder", 0)
            if not all(isinstance(value, int) and value >= 0 for value in (dividend, quotient, remainder)) or not isinstance(divisor, int) or divisor <= 0 or remainder >= divisor or dividend != divisor * quotient + remainder or interactive.get("missing") not in {"dividend", "divisor", "quotient", "remainder"}:
                raise SeedValidationError(f"{source}: întrebarea {i} are o relație a împărțirii invalidă.")
            continue
        if question_type == "operation_chain":
            interactive = question.get("interactive", {})
            current = interactive.get("start")
            steps = interactive.get("steps")
            if not isinstance(current, int) or current < 0 or not isinstance(steps, list) or len(steps) < 2:
                raise SeedValidationError(f"{source}: întrebarea {i} are un lanț invalid.")
            for step in steps:
                operation, value, result = step.get("operation"), step.get("value"), step.get("result")
                if not isinstance(value, int) or value <= 0 or not isinstance(result, int) or operation not in {"divide", "multiply", "add", "subtract"}:
                    raise SeedValidationError(f"{source}: întrebarea {i} are un pas invalid în lanț.")
                expected = {"multiply": current * value, "add": current + value, "subtract": current - value}.get(operation)
                if operation == "divide": expected = current // value if current % value == 0 else None
                if expected != result or result < 0:
                    raise SeedValidationError(f"{source}: întrebarea {i} are un rezultat greșit în lanț.")
                current = result
            continue
        if question_type == "division_table":
            rows = question.get("interactive", {}).get("rows")
            if not isinstance(rows, list) or len(rows) < 2:
                raise SeedValidationError(f"{source}: întrebarea {i} are un tabel invalid.")
            for row in rows:
                dividend, divisor, quotient = (row.get(key) for key in ("dividend", "divisor", "quotient"))
                remainder = row.get("remainder", 0)
                if not all(isinstance(value, int) and value >= 0 for value in (dividend, quotient, remainder)) or not isinstance(divisor, int) or divisor <= 0 or remainder >= divisor or dividend != divisor * quotient + remainder or row.get("missing") not in {"dividend", "divisor", "quotient", "remainder"}:
                    raise SeedValidationError(f"{source}: întrebarea {i} are un rând invalid în tabel.")
            continue
        if question_type == "numeric_input":
            interactive = question.get("interactive", {})
            if not isinstance(interactive.get("answer"), int) or interactive.get("answer") < 0:
                raise SeedValidationError(f"{source}: întrebarea {i} nu are un răspuns numeric valid.")
            continue
        if question_type == "factor_builder":
            interactive = question.get("interactive", {})
            common_factor = interactive.get("common_factor")
            inner_terms = interactive.get("inner_terms")
            operators = interactive.get("operators")
            result = interactive.get("result")
            if (
                not isinstance(interactive.get("expression"), str)
                or not interactive["expression"].strip()
                or not isinstance(common_factor, int)
                or common_factor <= 0
                or not isinstance(inner_terms, list)
                or len(inner_terms) < 2
                or not all(isinstance(term, int) and term >= 0 for term in inner_terms)
                or not isinstance(operators, list)
                or len(operators) != len(inner_terms) - 1
                or not all(operator in {"+", "−"} for operator in operators)
            ):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are o factorizare interactivă invalidă."
                )
            inner_value = inner_terms[0]
            for operator, term in zip(operators, inner_terms[1:]):
                inner_value = inner_value + term if operator == "+" else inner_value - term
            if inner_value < 0 or not isinstance(result, int) or common_factor * inner_value != result:
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are rezultatul factorizării greșit."
                )
            continue
        if question_type == "factor_error":
            interactive = question.get("interactive", {})
            steps = interactive.get("steps")
            error_index = interactive.get("error_index")
            if (
                not isinstance(steps, list)
                or len(steps) < 3
                or not all(isinstance(step, str) and step.strip() for step in steps)
                or not isinstance(error_index, int)
                or not 0 <= error_index < len(steps)
            ):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are pași invalizi pentru detectarea greșelii."
                )
            continue
        if question_type == "factor_match":
            interactive = question.get("interactive", {})
            pairs = interactive.get("pairs")
            right_order = interactive.get("right_order")
            if (
                not isinstance(pairs, list)
                or len(pairs) < 3
                or not all(
                    isinstance(pair, dict)
                    and isinstance(pair.get("left"), str)
                    and pair["left"].strip()
                    and isinstance(pair.get("right"), str)
                    and pair["right"].strip()
                    for pair in pairs
                )
                or sorted(right_order or []) != list(range(len(pairs)))
            ):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are perechi interactive invalide."
                )
            continue
        if question_type == "power_builder":
            interactive = question.get("interactive", {})
            mode = interactive.get("mode")
            base = interactive.get("base")
            exponent = interactive.get("exponent")
            value = interactive.get("value")
            factors = interactive.get("factors")
            if (
                mode not in {"compose", "expand", "missing"}
                or not isinstance(base, int)
                or base < 1
                or not isinstance(exponent, int)
                or exponent < 1
                or value != base ** exponent
                or factors != [base] * exponent
            ):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are date invalide pentru construirea puterii."
                )
            if mode == "missing" and interactive.get("missing") not in {"base", "exponent", "value"}:
                raise SeedValidationError(
                    f"{source}: întrebarea {i} nu precizează partea lipsă a puterii."
                )
            continue
        if question_type == "power_match":
            interactive = question.get("interactive", {})
            pairs = interactive.get("pairs")
            right_order = interactive.get("right_order")
            if (
                not isinstance(pairs, list)
                or len(pairs) < 3
                or not all(
                    isinstance(pair, dict)
                    and isinstance(pair.get("left"), str)
                    and pair["left"].strip()
                    and isinstance(pair.get("right"), str)
                    and pair["right"].strip()
                    for pair in pairs
                )
                or sorted(right_order or []) != list(range(len(pairs)))
            ):
                raise SeedValidationError(
                    f"{source}: întrebarea {i} are forme de puteri care nu pot fi potrivite."
                )
            continue
        if question_type == "power_table":
            rows = question.get("interactive", {}).get("rows")
            if not isinstance(rows, list) or len(rows) < 2:
                raise SeedValidationError(f"{source}: întrebarea {i} are un tabel de puteri invalid.")
            for row in rows:
                base, exponent, value = (row.get(key) for key in ("base", "exponent", "value"))
                if (
                    not isinstance(base, int)
                    or base < 1
                    or not isinstance(exponent, int)
                    or exponent < 1
                    or value != base ** exponent
                    or row.get("missing") not in {"base", "exponent", "value"}
                ):
                    raise SeedValidationError(f"{source}: întrebarea {i} are un rând invalid în tabelul puterilor.")
            continue
        if question_type == "power_cycle":
            interactive = question.get("interactive", {})
            base = interactive.get("base")
            exponent = interactive.get("exponent")
            cycle = interactive.get("cycle")
            if (
                not isinstance(base, int)
                or base < 1
                or not isinstance(exponent, int)
                or exponent < 1
                or not isinstance(cycle, list)
                or len(cycle) not in {1, 2, 4}
                or cycle != [pow(base, power, 10) for power in range(1, len(cycle) + 1)]
                or interactive.get("last_digit") != pow(base, exponent, 10)
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are un ciclu al ultimei cifre invalid.")
            continue
        if question_type == "power_square":
            interactive = question.get("interactive", {})
            side = interactive.get("side")
            if not isinstance(side, int) or not 2 <= side <= 12 or interactive.get("value") != side ** 2:
                raise SeedValidationError(f"{source}: întrebarea {i} are un pătrat vizual invalid.")
            continue
        if question_type == "power_rule_chain":
            interactive = question.get("interactive", {})
            stages = interactive.get("stages")
            if (
                not isinstance(interactive.get("expression"), str)
                or not interactive["expression"].strip()
                or not isinstance(stages, list)
                or not 1 <= len(stages) <= 4
                or not all(
                    isinstance(stage, dict)
                    and isinstance(stage.get("label"), str)
                    and stage["label"].strip()
                    and isinstance(stage.get("base"), int)
                    and stage["base"] >= 1
                    and isinstance(stage.get("exponent"), int)
                    and stage["exponent"] >= 0
                    for stage in stages
                )
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are un lanț de puteri invalid.")
            continue
        if question_type == "power_compare":
            interactive = question.get("interactive", {})
            if (
                not isinstance(interactive.get("left"), str)
                or not interactive["left"].strip()
                or not isinstance(interactive.get("right"), str)
                or not interactive["right"].strip()
                or interactive.get("relation") not in {"<", "=", ">"}
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are o comparație invalidă.")
            continue
        if question_type == "power_order":
            interactive = question.get("interactive", {})
            items = interactive.get("items")
            direction = interactive.get("direction")
            display_order = interactive.get("display_order")
            if (
                direction not in {"asc", "desc"}
                or not isinstance(items, list)
                or not 3 <= len(items) <= 6
                or not all(
                    isinstance(item, dict)
                    and isinstance(item.get("label"), str)
                    and item["label"].strip()
                    and isinstance(item.get("value"), int)
                    and item["value"] >= 0
                    for item in items
                )
                or len({item["value"] for item in items}) != len(items)
                or sorted(display_order or []) != list(range(len(items)))
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are o ordonare de puteri invalidă.")
            continue
        if question_type == "base_values":
            interactive = question.get("interactive", {})
            mode = interactive.get("mode")
            answers = interactive.get("answers")
            if mode not in {"division_ladder", "decompose", "compose", "place_table", "missing_digits", "complete_equality", "secret_code"} or not isinstance(answers, dict) or not answers or not all(isinstance(key, str) and isinstance(value, (str, int)) for key, value in answers.items()):
                raise SeedValidationError(f"{source}: întrebarea {i} are câmpuri invalide pentru scrierea într-o bază.")
            if mode == "division_ladder":
                rows = interactive.get("rows")
                if not isinstance(rows, list) or len(rows) < 2 or any(row.get("quotient") != row.get("dividend") // 2 or row.get("remainder") != row.get("dividend") % 2 for row in rows):
                    raise SeedValidationError(f"{source}: întrebarea {i} are o scară a împărțirilor la 2 invalidă.")
            elif mode == "decompose":
                base, number, terms = interactive.get("base"), interactive.get("number"), interactive.get("terms")
                if base not in {2, 10} or not isinstance(number, str) or not isinstance(terms, list) or int(number, base) != sum(term.get("digit", -1) * (base ** term.get("exponent", -1)) for term in terms):
                    raise SeedValidationError(f"{source}: întrebarea {i} are o descompunere invalidă.")
            elif mode == "compose":
                base, answer, terms = interactive.get("base"), str(answers.get("number", "")), interactive.get("terms")
                if base not in {2, 10} or not answer or not isinstance(terms, list) or int(answer, base) != sum(term.get("value", -1) for term in terms):
                    raise SeedValidationError(f"{source}: întrebarea {i} are o compunere invalidă.")
            elif mode == "place_table":
                base, rows = interactive.get("base"), interactive.get("rows")
                if base not in {2, 10} or not isinstance(rows, list) or len(rows) < 2 or any(row.get("contribution") != row.get("digit") * (base ** row.get("exponent")) for row in rows):
                    raise SeedValidationError(f"{source}: întrebarea {i} are un tabel pozițional invalid.")
            elif mode == "missing_digits":
                base, digits = interactive.get("base"), interactive.get("digits")
                if base not in {2, 10} or not isinstance(digits, list) or not digits or any(not isinstance(digit, int) or not 0 <= digit < base for digit in digits):
                    raise SeedValidationError(f"{source}: întrebarea {i} are cifre lipsă invalide.")
            elif mode == "complete_equality":
                left_value, left_base, answer_base = interactive.get("left_value"), interactive.get("left_base"), interactive.get("answer_base")
                answer = str(answers.get("value", ""))
                if left_base not in {2, 10} or answer_base not in {2, 10} or int(str(left_value), left_base) != int(answer, answer_base):
                    raise SeedValidationError(f"{source}: întrebarea {i} are o egalitate între baze invalidă.")
            elif mode == "secret_code":
                items = interactive.get("items")
                if not isinstance(items, list) or len(items) < 3 or any(int(item.get("binary", ""), 2) != item.get("position") or not 1 <= item.get("position", 0) <= 26 for item in items):
                    raise SeedValidationError(f"{source}: întrebarea {i} are un cod secret invalid.")
            continue
        if question_type == "base_match":
            interactive = question.get("interactive", {})
            pairs, right_order = interactive.get("pairs"), interactive.get("right_order")
            if not isinstance(pairs, list) or len(pairs) < 3 or any(not isinstance(pair.get("left"), str) or not isinstance(pair.get("right"), str) for pair in pairs) or sorted(right_order or []) != list(range(len(pairs))):
                raise SeedValidationError(f"{source}: întrebarea {i} are reprezentări care nu pot fi potrivite.")
            continue
        if question_type == "binary_toggle":
            interactive = question.get("interactive", {})
            binary, decimal = interactive.get("binary"), interactive.get("decimal")
            if not isinstance(binary, str) or not binary or set(binary) - {"0", "1"} or not isinstance(decimal, int) or int(binary, 2) != decimal:
                raise SeedValidationError(f"{source}: întrebarea {i} are un număr binar invalid.")
            continue
        if question_type == "base_error":
            interactive = question.get("interactive", {})
            steps, error_index = interactive.get("steps"), interactive.get("error_index")
            if not isinstance(steps, list) or len(steps) < 3 or not all(isinstance(step, str) and step.strip() for step in steps) or not isinstance(error_index, int) or not 0 <= error_index < len(steps):
                raise SeedValidationError(f"{source}: întrebarea {i} are pași invalizi pentru detectarea erorii de conversie.")
            continue
        if question_type == "unit_reduction":
            interactive = question.get("interactive", {})
            mode = interactive.get("mode")
            answers = interactive.get("answers")
            allowed_modes = {
                "visual_scale", "unit_path", "balance", "basket", "faucets",
                "dependency_direction", "unit_table", "operation_drop", "timeline",
                "problem_builder", "speed_simulator", "triple_match", "visual_true_false",
            }
            if mode not in allowed_modes or not isinstance(answers, dict) or not answers or not all(isinstance(key, str) and isinstance(value, (str, int)) for key, value in answers.items()):
                raise SeedValidationError(f"{source}: întrebarea {i} are un exercițiu invalid pentru reducerea la unitate.")
            if mode in {"visual_scale", "balance"}:
                initial_quantity = interactive.get("initial_quantity")
                initial_value = interactive.get("initial_value")
                target_quantity = interactive.get("target_quantity")
                target_value = interactive.get("target_value")
                relation = interactive.get("relation", "direct")
                if not all(isinstance(value, int) and value > 0 for value in (initial_quantity, initial_value, target_quantity, target_value)) or relation not in {"direct", "inverse"}:
                    raise SeedValidationError(f"{source}: întrebarea {i} are mărimi invalide.")
                expected = initial_value * target_quantity == target_value * initial_quantity if relation == "direct" else initial_quantity * initial_value == target_quantity * target_value
                if not expected:
                    raise SeedValidationError(f"{source}: întrebarea {i} nu păstrează relația dintre mărimi.")
            elif mode in {"unit_path", "operation_drop"}:
                nodes = interactive.get("values", interactive.get("nodes"))
                operations = [answers.get(f"operation:{index}") for index in range(len(nodes or []) - 1)]
                if not isinstance(nodes, list) or len(nodes) < 3 or any(not isinstance(operation, str) or not operation for operation in operations):
                    raise SeedValidationError(f"{source}: întrebarea {i} are un drum prin unitate invalid.")
            elif mode == "basket":
                unit_price, target_quantity = interactive.get("unit_price"), interactive.get("target_quantity")
                if not all(isinstance(value, int) and value > 0 for value in (unit_price, target_quantity)) or answers.get("total") != unit_price * target_quantity:
                    raise SeedValidationError(f"{source}: întrebarea {i} are un coș invalid.")
            elif mode == "faucets":
                initial_count, initial_time, target_count, target_time = (interactive.get(key) for key in ("initial_count", "initial_time", "target_count", "target_time"))
                if not all(isinstance(value, int) and value > 0 for value in (initial_count, initial_time, target_count, target_time)) or initial_count * initial_time != target_count * target_time:
                    raise SeedValidationError(f"{source}: întrebarea {i} are robinete incompatibile.")
            elif mode == "dependency_direction":
                if answers.get("relation") not in {"direct", "inverse"}:
                    raise SeedValidationError(f"{source}: întrebarea {i} nu are sensul dependenței precizat.")
            elif mode == "unit_table":
                columns, rows = interactive.get("columns"), interactive.get("rows")
                if not isinstance(columns, list) or len(columns) < 2 or not isinstance(rows, list) or len(rows) < 2 or any(row.get("missing") not in columns for row in rows):
                    raise SeedValidationError(f"{source}: întrebarea {i} are un tabel prin unitate invalid.")
            elif mode in {"timeline", "speed_simulator"}:
                target = interactive.get("target_time")
                if not isinstance(target, int) or target <= 0 or answers.get("time") != target:
                    raise SeedValidationError(f"{source}: întrebarea {i} are o bandă de timp invalidă.")
                if mode == "speed_simulator" and interactive.get("speed") * target != interactive.get("target_distance"):
                    raise SeedValidationError(f"{source}: întrebarea {i} are un simulator de viteză invalid.")
            elif mode == "problem_builder":
                groups = interactive.get("groups")
                if not isinstance(groups, list) or len(groups) != 3 or any(not isinstance(group.get("choices"), list) or len(group["choices"]) < 2 for group in groups):
                    raise SeedValidationError(f"{source}: întrebarea {i} nu poate construi problema.")
            elif mode == "triple_match":
                triples = interactive.get("triples")
                scheme_order, answer_order = interactive.get("scheme_order"), interactive.get("answer_order")
                valid_order = list(range(len(triples or [])))
                if not isinstance(triples, list) or len(triples) < 3 or any(set(triple) != {"problem", "scheme", "answer"} for triple in triples) or sorted(scheme_order or []) != valid_order or sorted(answer_order or []) != valid_order:
                    raise SeedValidationError(f"{source}: întrebarea {i} are triplete incomplete.")
            elif mode == "visual_true_false" and answers.get("answer") not in {"true", "false"}:
                raise SeedValidationError(f"{source}: întrebarea {i} nu are valoare de adevăr validă.")
            continue
        if question_type == "comparison_method":
            interactive = question.get("interactive", {})
            mode, answers = interactive.get("mode"), interactive.get("answers")
            allowed = {"balance", "cancel_common", "align_rows", "equalize", "choose_method", "comparison_table", "substitution_machine", "comparison_error", "animal_race", "dancers", "comparison_match", "comparison_true_false"}
            if mode not in allowed or not isinstance(answers, dict) or not answers or not all(isinstance(k, str) and isinstance(v, (str, int)) for k, v in answers.items()):
                raise SeedValidationError(f"{source}: întrebarea {i} are un exercițiu invalid pentru metoda comparației.")
            if mode in {"balance", "cancel_common", "align_rows", "equalize", "comparison_table"}:
                rows = interactive.get("rows")
                if not isinstance(rows, list) or len(rows) != 2 or any(not isinstance(row.get("items"), list) or not isinstance(row.get("total"), int) for row in rows):
                    raise SeedValidationError(f"{source}: întrebarea {i} trebuie să aibă două situații de comparat.")
            elif mode == "choose_method" and answers.get("method") not in {"subtract", "add", "substitute"}:
                raise SeedValidationError(f"{source}: întrebarea {i} nu are o metodă validă.")
            elif mode == "substitution_machine" and not all(isinstance(interactive.get(key), dict) for key in ("source_group", "target_group", "large_row", "result_row")):
                raise SeedValidationError(f"{source}: întrebarea {i} nu are o substituție completă.")
            elif mode == "comparison_error":
                steps = interactive.get("steps")
                if not isinstance(steps, list) or len(steps) < 3 or answers.get("step") not in range(len(steps)):
                    raise SeedValidationError(f"{source}: întrebarea {i} are pași invalizi.")
            elif mode == "animal_race" and not all(isinstance(interactive.get(key), dict) for key in ("animal_a", "animal_b")):
                raise SeedValidationError(f"{source}: întrebarea {i} are o cursă invalidă.")
            elif mode == "dancers" and not all(isinstance(interactive.get(key), int) and interactive.get(key) > 0 for key in ("initial_boys", "initial_girls", "initial_time", "target_boys", "target_girls")):
                raise SeedValidationError(f"{source}: întrebarea {i} are dansatori invalizi.")
            elif mode == "comparison_match":
                triples = interactive.get("triples")
                if not isinstance(triples, list) or len(triples) < 3 or any(set(t) != {"problem", "scheme", "answer"} for t in triples):
                    raise SeedValidationError(f"{source}: întrebarea {i} are potriviri incomplete.")
            elif mode == "comparison_true_false" and answers.get("answer") not in {"true", "false"}:
                raise SeedValidationError(f"{source}: întrebarea {i} nu are o valoare de adevăr validă.")
            continue
        if question_type == "figurative_method":
            interactive = question.get("interactive", {})
            mode, answers = interactive.get("mode"), interactive.get("answers")
            allowed = {"choose_scheme", "build_segments", "divide_segments", "order_steps", "animate_difference", "repair_scheme", "figurative_true_false", "remainder_slider", "no_solution", "benches", "equivalent_schemes", "full_puzzle"}
            if mode not in allowed or not isinstance(answers, dict) or not answers:
                raise SeedValidationError(f"{source}: întrebarea {i} are un exercițiu figurativ invalid.")
            schemes = interactive.get("schemes", [])
            if mode in {"choose_scheme", "equivalent_schemes"} and (not isinstance(schemes, list) or len(schemes) < 3):
                raise SeedValidationError(f"{source}: întrebarea {i} nu are suficiente desene.")
            if mode in {"build_segments", "divide_segments", "animate_difference", "repair_scheme", "remainder_slider", "full_puzzle"} and not isinstance(interactive.get("scheme"), dict):
                raise SeedValidationError(f"{source}: întrebarea {i} nu are schema grafică.")
            if mode == "order_steps" and len(interactive.get("steps", [])) < 3:
                raise SeedValidationError(f"{source}: întrebarea {i} nu are pași suficienți.")
            if mode == "figurative_true_false" and answers.get("answer") not in {"true", "false"}:
                raise SeedValidationError(f"{source}: întrebarea {i} nu are valoare de adevăr validă.")
            continue
        if question_type == "reverse_method":
            interactive = question.get("interactive", {})
            mode, answers = interactive.get("mode"), interactive.get("answers")
            allowed = {"build_reverse_path", "drag_inverse_ops", "reverse_arrows", "pair_inverse", "order_reverse", "reverse_error", "repair_chain", "time_machine", "start_slider", "candies", "water_transfer", "reverse_table", "choose_story", "full_reverse_puzzle", "round_trip"}
            if mode not in allowed or not isinstance(answers, dict) or not answers:
                raise SeedValidationError(f"{source}: întrebarea {i} are un exercițiu invalid pentru mersul invers.")
            if mode in {"build_reverse_path", "drag_inverse_ops", "reverse_arrows", "order_reverse", "reverse_error", "repair_chain", "time_machine", "start_slider", "full_reverse_puzzle", "round_trip"}:
                operations = interactive.get("operations")
                if not isinstance(operations, list) or not operations or any(not isinstance(op, dict) or set(op) != {"op", "value"} for op in operations):
                    raise SeedValidationError(f"{source}: întrebarea {i} nu are un lanț de operații valid.")
            if mode == "pair_inverse" and len(interactive.get("pairs", [])) < 3:
                raise SeedValidationError(f"{source}: întrebarea {i} nu are suficiente perechi inverse.")
            if mode in {"candies", "water_transfer", "reverse_table"} and not isinstance(interactive.get("stages"), list):
                raise SeedValidationError(f"{source}: întrebarea {i} nu are etapele problemei.")
            if mode == "choose_story" and len(interactive.get("stories", [])) < 3:
                raise SeedValidationError(f"{source}: întrebarea {i} nu are suficiente enunțuri.")
            continue
        if question_type == "false_hypothesis_method":
            interactive = question.get("interactive", {})
            mode, answers = interactive.get("mode"), interactive.get("answers")
            allowed = {"choose_hypothesis", "all_same_simulator", "mismatch_meter", "replacement_count", "heads_legs", "score_cards", "containers", "money_notes", "bees_flowers", "shares", "vases", "hypothesis_error", "hypothesis_table", "full_hypothesis_puzzle", "hypothesis_verify"}
            if mode not in allowed or not isinstance(answers, dict) or not answers:
                raise SeedValidationError(f"{source}: întrebarea {i} are un exercițiu invalid pentru falsa ipoteză.")
            scenario = interactive.get("scenario")
            if not isinstance(scenario, dict) or not all(isinstance(scenario.get(key), int) for key in ("count", "low", "high", "total")):
                raise SeedValidationError(f"{source}: întrebarea {i} nu are date numerice complete.")
            expected_total = scenario["count"] * scenario["low"] + answers.get("high_count", 0) * (scenario["high"] - scenario["low"])
            if "high_count" in answers and expected_total != scenario["total"]:
                raise SeedValidationError(f"{source}: întrebarea {i} are o soluție incompatibilă cu datele.")
            continue
        if question_type == "operation_sequence":
            interactive = question.get("interactive", {})
            steps = interactive.get("steps")
            display_order = interactive.get("display_order")
            correct_order = interactive.get("correct_order")
            if (
                not isinstance(interactive.get("expression"), str)
                or not interactive["expression"].strip()
                or not isinstance(steps, list)
                or not 2 <= len(steps) <= 7
                or not all(isinstance(step, str) and step.strip() for step in steps)
                or sorted(display_order or []) != list(range(len(steps)))
                or sorted(correct_order or []) != list(range(len(steps)))
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are o ordine de operații invalidă.")
            continue
        if question_type == "operation_workbench":
            interactive = question.get("interactive", {})
            stages = interactive.get("stages")
            if (
                not isinstance(interactive.get("expression"), str)
                or not interactive["expression"].strip()
                or not isinstance(stages, list)
                or not 1 <= len(stages) <= 6
                or not all(
                    isinstance(stage, dict)
                    and isinstance(stage.get("expression"), str)
                    and stage["expression"].strip()
                    and isinstance(stage.get("answer"), int)
                    and stage["answer"] >= 0
                    for stage in stages
                )
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are etape de calcul invalide.")
            continue
        if question_type == "fraction_visual":
            interactive = question.get("interactive", {})
            mode = interactive.get("mode")
            answers = interactive.get("answers")
            allowed_modes = {"color", "read", "construct", "repair", "equivalent", "percent", "mixed_to_fraction", "fraction_to_mixed"}
            if mode not in allowed_modes or not isinstance(answers, dict) or not answers:
                raise SeedValidationError(f"{source}: întrebarea {i} are un exercițiu vizual cu fracții invalid.")
            numerator = interactive.get("numerator", interactive.get("base_numerator", 0))
            denominator = interactive.get("denominator", interactive.get("base_denominator", 1))
            if not all(isinstance(value, int) for value in (numerator, denominator)) or numerator < 0 or denominator <= 0 or denominator > 100:
                raise SeedValidationError(f"{source}: întrebarea {i} are o fracție invalidă.")
            if mode in {"color", "read"} and numerator > denominator:
                raise SeedValidationError(f"{source}: întrebarea {i} nu poate reprezenta desenul într-un singur întreg.")
            if mode == "color" and interactive.get("shape") not in {"bar", "circle", "grid"}:
                raise SeedValidationError(f"{source}: întrebarea {i} are o formă vizuală necunoscută.")
            if mode == "repair" and interactive.get("editable") not in {"numerator", "denominator"}:
                raise SeedValidationError(f"{source}: întrebarea {i} nu precizează partea reparabilă.")
            if mode == "equivalent":
                factor = interactive.get("factor")
                if not isinstance(factor, int) or factor < 2 or answers.get("numerator") != numerator * factor or answers.get("denominator") != denominator * factor:
                    raise SeedValidationError(f"{source}: întrebarea {i} are o fracție echivalentă greșită.")
            if mode == "percent":
                if numerator * 100 % denominator or answers.get("percent") != numerator * 100 // denominator or answers.get("hundredths") != numerator * 100 // denominator:
                    raise SeedValidationError(f"{source}: întrebarea {i} are un procent greșit.")
            if mode == "mixed_to_fraction":
                whole = interactive.get("whole")
                if not isinstance(whole, int) or whole < 1 or answers.get("result") != whole * denominator + numerator:
                    raise SeedValidationError(f"{source}: întrebarea {i} introduce greșit întregii în fracție.")
            if mode == "fraction_to_mixed":
                if numerator < denominator or answers.get("whole") != numerator // denominator or answers.get("remainder") != numerator % denominator:
                    raise SeedValidationError(f"{source}: întrebarea {i} scoate greșit întregii din fracție.")
            continue
        if question_type == "fraction_domino":
            interactive = question.get("interactive", {})
            tiles = interactive.get("tiles")
            correct_order = interactive.get("correct_order")
            display_order = interactive.get("display_order")
            if (
                not isinstance(tiles, list)
                or not 3 <= len(tiles) <= 6
                or not all(isinstance(tile, dict) and isinstance(tile.get("left"), str) and tile["left"].strip() and isinstance(tile.get("right"), str) and tile["right"].strip() for tile in tiles)
                or sorted(correct_order or []) != list(range(len(tiles)))
                or sorted(display_order or []) != list(range(len(tiles)))
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are un domino de fracții invalid.")
            continue
        if question_type == "fraction_compare":
            interactive = question.get("interactive", {})
            mode = interactive.get("mode")
            if mode in {"symbol", "visual"}:
                fractions = [interactive.get("left"), interactive.get("right")]
                if (
                    interactive.get("relation") not in {"<", "=", ">"}
                    or not all(isinstance(value, list) and len(value) == 2 and all(isinstance(number, int) and number > 0 for number in value) for value in fractions)
                ):
                    raise SeedValidationError(f"{source}: întrebarea {i} are o comparație de fracții invalidă.")
            elif mode == "order":
                items = interactive.get("items")
                if (
                    interactive.get("direction") not in {"asc", "desc"}
                    or not isinstance(items, list) or not 3 <= len(items) <= 6
                    or any(not isinstance(item, dict) or not isinstance(item.get("label"), str) or not isinstance(item.get("numerator"), int) or not isinstance(item.get("denominator"), int) or item["denominator"] <= 0 for item in items)
                    or sorted(interactive.get("correct_order", [])) != list(range(len(items)))
                    or sorted(interactive.get("display_order", [])) != list(range(len(items)))
                ):
                    raise SeedValidationError(f"{source}: întrebarea {i} are o ordonare de fracții invalidă.")
            else:
                raise SeedValidationError(f"{source}: întrebarea {i} are un mod de comparare necunoscut.")
            continue
        if question_type == "fraction_axis":
            interactive = question.get("interactive", {})
            denominator = interactive.get("denominator")
            maximum = interactive.get("maximum")
            answer_tick = interactive.get("answer_tick")
            if (
                interactive.get("mode") not in {"place", "read"}
                or not isinstance(denominator, int) or not 2 <= denominator <= 24
                or not isinstance(maximum, int) or not 1 <= maximum <= 4
                or not isinstance(answer_tick, int) or not 0 <= answer_tick <= denominator * maximum
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are o axă a fracțiilor invalidă.")
            continue
        if question_type == "gcd_workbench":
            interactive = question.get("interactive", {})
            answers = interactive.get("answers")
            if (
                interactive.get("mode") not in {"table", "select", "packing"}
                or not isinstance(interactive.get("a"), int) or interactive["a"] <= 0
                or not isinstance(interactive.get("b"), int) or interactive["b"] <= 0
                or not isinstance(answers, dict) or not answers
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are un atelier c.m.m.d.c. invalid.")
            continue
        if question_type == "fraction_scale":
            interactive = question.get("interactive", {})
            answers = interactive.get("answers")
            if (
                interactive.get("mode") not in {"amplify", "simplify", "missing_factor", "restore"}
                or not isinstance(interactive.get("numerator"), int) or interactive["numerator"] <= 0
                or not isinstance(interactive.get("denominator"), int) or interactive["denominator"] <= 0
                or not isinstance(answers, dict) or not answers
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are o scalare de fracție invalidă.")
            continue
        if question_type == "fraction_reduce_path":
            interactive = question.get("interactive", {})
            steps = interactive.get("steps")
            if (
                not isinstance(interactive.get("numerator"), int) or interactive["numerator"] <= 0
                or not isinstance(interactive.get("denominator"), int) or interactive["denominator"] <= 0
                or not isinstance(steps, list) or not steps
                or any(not isinstance(step, dict) or not all(isinstance(step.get(key), int) and step[key] > 0 for key in ("factor", "numerator", "denominator")) for step in steps)
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are un traseu de simplificare invalid.")
            continue
        if question_type == "lcm_workbench":
            interactive = question.get("interactive", {})
            answers = interactive.get("answers")
            if (
                interactive.get("mode") not in {"lists", "select", "sync"}
                or not isinstance(interactive.get("a"), int) or interactive["a"] <= 0
                or not isinstance(interactive.get("b"), int) or interactive["b"] <= 0
                or not isinstance(answers, dict) or not answers
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are un atelier c.m.m.m.c. invalid.")
            continue
        if question_type == "common_denominator":
            interactive = question.get("interactive", {})
            left, right, answers = interactive.get("left"), interactive.get("right"), interactive.get("answers")
            if (
                interactive.get("mode") not in {"build", "compare", "order"}
                or not all(isinstance(value, list) and len(value) == 2 and all(isinstance(number, int) and number > 0 for number in value) for value in (left, right))
                or not isinstance(answers, dict) or not answers
            ):
                raise SeedValidationError(f"{source}: întrebarea {i} are o aducere la numitor comun invalidă.")
            continue
        if question_type == "divisibility_values":
            interactive = question.get("interactive", {})
            mode, answers = interactive.get("mode"), interactive.get("answers")
            allowed_modes = {"relation", "factor_pairs", "divisor_list", "greatest_common", "sequence", "dual_sequence", "timeline", "first_common", "digit_sum"}
            if mode not in allowed_modes or not isinstance(answers, dict) or not answers or not all(isinstance(key, str) and isinstance(value, (str, int)) for key, value in answers.items()):
                raise SeedValidationError(f"{source}: întrebarea {i} are valori invalide pentru divizibilitate.")
            fields = interactive.get("fields")
            if not isinstance(fields, list) or not fields or any(not isinstance(field, dict) or not isinstance(field.get("key"), str) or field["key"] not in answers for field in fields):
                raise SeedValidationError(f"{source}: întrebarea {i} nu declară corect toate câmpurile.")
            if mode == "relation":
                a, b, c = (interactive.get(key) for key in ("a", "b", "c"))
                if not all(isinstance(value, int) and value > 0 for value in (a, b, c)) or a != b * c:
                    raise SeedValidationError(f"{source}: întrebarea {i} nu are o relație a = b · c corectă.")
            elif mode == "factor_pairs":
                number, pairs = interactive.get("number"), interactive.get("pairs")
                if not isinstance(number, int) or number <= 0 or not isinstance(pairs, list) or not pairs or any(len(pair) != 2 or pair[0] * pair[1] != number for pair in pairs):
                    raise SeedValidationError(f"{source}: întrebarea {i} are perechi de factori invalide.")
            elif mode == "divisor_list":
                number = interactive.get("number")
                expected = ",".join(str(value) for value in range(1, number + 1) if number % value == 0)
                if answers.get("list") != expected:
                    raise SeedValidationError(f"{source}: întrebarea {i} nu are lista completă a divizorilor.")
            elif mode == "greatest_common":
                a, b = interactive.get("a"), interactive.get("b")
                common = [value for value in range(1, min(a, b) + 1) if a % value == 0 and b % value == 0]
                if answers.get("greatest") != max(common):
                    raise SeedValidationError(f"{source}: întrebarea {i} are cel mai mare divizor comun greșit.")
            elif mode in {"sequence", "dual_sequence"}:
                if not isinstance(interactive.get("rows"), list) or not interactive["rows"]:
                    raise SeedValidationError(f"{source}: întrebarea {i} nu are șiruri de multipli.")
            elif mode in {"timeline", "first_common"}:
                a, b = interactive.get("a"), interactive.get("b")
                first = next(value for value in range(max(a, b), a * b + 1) if value % a == 0 and value % b == 0)
                key = "moments" if mode == "timeline" else "first"
                expected = ",".join(str(first * factor) for factor in range(1, interactive.get("count", 1) + 1)) if mode == "timeline" else first
                if answers.get(key) != expected:
                    raise SeedValidationError(f"{source}: întrebarea {i} are multiplii comuni greșiți.")
            elif mode == "digit_sum":
                number = interactive.get("number")
                if not isinstance(number, int) or number < 0 or answers.get("sum") != sum(int(digit) for digit in str(number)):
                    raise SeedValidationError(f"{source}: întrebarea {i} are suma cifrelor greșită.")
            continue
        if question_type == "divisibility_select":
            interactive = question.get("interactive", {})
            cards, correct_ids = interactive.get("cards"), interactive.get("correct_ids")
            if interactive.get("mode") not in {"role", "divisors", "multiples", "bingo", "digits", "criteria"} or not isinstance(cards, list) or len(cards) < 4 or any(not isinstance(card.get("id"), str) or not isinstance(card.get("label"), str) for card in cards) or len({card["id"] for card in cards}) != len(cards) or not isinstance(correct_ids, list) or not correct_ids or not set(correct_ids) <= {card["id"] for card in cards}:
                raise SeedValidationError(f"{source}: întrebarea {i} are cartonașe de selectare invalide.")
            continue
        if question_type == "divisibility_sort":
            interactive = question.get("interactive", {})
            cards, zones = interactive.get("cards"), interactive.get("zones")
            zone_ids = {zone.get("id") for zone in zones or []}
            if interactive.get("mode") not in {"two_zones", "venn"} or not isinstance(zones, list) or len(zones) not in {2, 3} or None in zone_ids or not isinstance(cards, list) or len(cards) < 4 or any(not isinstance(card.get("id"), str) or card.get("zone") not in zone_ids for card in cards):
                raise SeedValidationError(f"{source}: întrebarea {i} are zone de sortare invalide.")
            continue
        if question_type == "divisibility_error":
            interactive = question.get("interactive", {})
            steps, error_index = interactive.get("steps"), interactive.get("error_index")
            if not isinstance(steps, list) or len(steps) < 3 or not all(isinstance(step, str) and step.strip() for step in steps) or not isinstance(error_index, int) or not 0 <= error_index < len(steps):
                raise SeedValidationError(f"{source}: întrebarea {i} are pași invalizi pentru detectarea erorii de divizibilitate.")
            continue
        if question_type == "criteria_table":
            interactive = question.get("interactive", {})
            numbers, divisors, answers = interactive.get("numbers"), interactive.get("divisors"), interactive.get("answers")
            if not isinstance(numbers, list) or len(numbers) < 3 or not all(isinstance(value, int) and value >= 0 for value in numbers) or not isinstance(divisors, list) or not divisors or not all(divisor in {2, 3, 5, 9, 10, 100, 1000} for divisor in divisors) or not isinstance(answers, dict):
                raise SeedValidationError(f"{source}: întrebarea {i} are un tabel de criterii invalid.")
            expected = {f"{row}:{column}": numbers[column] % divisor == 0 for row, divisor in enumerate(divisors) for column in range(len(numbers))}
            if answers != expected:
                raise SeedValidationError(f"{source}: întrebarea {i} are bife greșite în tabelul criteriilor.")
            continue
        if question_type == "prime_workbench":
            interactive = question.get("interactive", {})
            mode = interactive.get("mode")
            answers = interactive.get("answers")
            allowed_modes = {"trial", "factor_product", "prime_pair", "prime_equation", "escape_code", "perfect_number"}
            if mode not in allowed_modes or not isinstance(answers, dict) or not answers:
                raise SeedValidationError(f"{source}: întrebarea {i} are un atelier de numere prime invalid.")
            if mode == "trial":
                tests = interactive.get("tests")
                if not isinstance(interactive.get("number"), int) or not isinstance(tests, list) or not tests or any(not isinstance(row.get("divisor"), int) or not isinstance(row.get("remainder"), int) for row in tests):
                    raise SeedValidationError(f"{source}: întrebarea {i} are împărțiri de verificare invalide.")
            elif mode == "factor_product":
                cards = interactive.get("cards")
                if not isinstance(interactive.get("target"), int) or not isinstance(cards, list) or len(cards) < 3 or not isinstance(interactive.get("slot_count"), int):
                    raise SeedValidationError(f"{source}: întrebarea {i} are factori primi invalizi.")
            elif mode in {"prime_pair", "prime_equation"}:
                if not isinstance(interactive.get("fields"), list) or len(interactive["fields"]) < 2:
                    raise SeedValidationError(f"{source}: întrebarea {i} nu are toate câmpurile necesare.")
            elif mode == "escape_code":
                if not isinstance(interactive.get("clues"), list) or len(interactive["clues"]) < 3:
                    raise SeedValidationError(f"{source}: întrebarea {i} nu are un cod complet.")
            elif mode == "perfect_number":
                if not isinstance(interactive.get("number"), int) or not isinstance(interactive.get("candidates"), list):
                    raise SeedValidationError(f"{source}: întrebarea {i} are date invalide despre numărul perfect.")
            continue
        if question_type == "decimal_workbench":
            interactive = question.get("interactive", {})
            mode, answers = interactive.get("mode"), interactive.get("answers")
            allowed_modes = {"comma", "conversion", "build_fraction", "place_value", "words", "decompose", "amplify", "missing", "natural_n", "denominator", "zeros", "vessel"}
            if mode not in allowed_modes or not isinstance(answers, dict) or not answers:
                raise SeedValidationError(f"{source}: întrebarea {i} are un atelier zecimal invalid.")
            fields = interactive.get("fields", [])
            if not isinstance(fields, list) or any(not isinstance(field, dict) or field.get("key") not in answers for field in fields):
                raise SeedValidationError(f"{source}: întrebarea {i} are câmpuri zecimale invalide.")
            if mode == "comma" and (not isinstance(interactive.get("digits"), str) or not isinstance(interactive.get("places"), int)):
                raise SeedValidationError(f"{source}: întrebarea {i} nu declară poziția virgulei.")
            if mode == "place_value" and not isinstance(interactive.get("columns"), list):
                raise SeedValidationError(f"{source}: întrebarea {i} nu are tabel pozițional.")
            if mode == "vessel" and (not isinstance(interactive.get("segments"), int) or not isinstance(interactive.get("filled"), int)):
                raise SeedValidationError(f"{source}: întrebarea {i} are un vas gradat invalid.")
            continue
        options = question.get("options", [])
        if len(options) < 2:
            raise SeedValidationError(
                f"{source}: întrebarea {i} trebuie să aibă minim 2 opțiuni."
            )
        correct = [o for o in options if o.get("is_correct")]
        if len(correct) != 1:
            raise SeedValidationError(
                f"{source}: întrebarea {i} trebuie să aibă exact o opțiune corectă."
            )
        if question_format == "true_false":
            normalized = {str(option.get("text", "")).strip().lower() for option in options}
            if len(options) != 2 or normalized != {"adevărat", "fals"}:
                raise SeedValidationError(
                    f"{source}: întrebarea {i} Adevărat sau fals trebuie să aibă exact opțiunile Adevărat și Fals."
                )
        for j, opt in enumerate(options, start=1):
            if not opt.get("text"):
                raise SeedValidationError(
                    f"{source}: întrebarea {i}, opțiunea {j} nu are text."
                )


def _validate_chapters_manifest(data: list, source: str) -> None:
    if not isinstance(data, list):
        raise SeedValidationError(f"{source}: manifestul trebuie să fie o listă.")
    for i, chapter in enumerate(data, start=1):
        for field in ("class_level", "slug", "title", "topics"):
            if field not in chapter:
                raise SeedValidationError(f"{source}: capitolul {i} lipsește '{field}'.")
        if not isinstance(chapter["topics"], list):
            raise SeedValidationError(f"{source}: capitolul {i} — topics trebuie listă.")


def _sync_options(question: Question, options_data: list) -> None:
    seen_texts = set()
    for opt in options_data:
        text = opt["text"].strip()
        seen_texts.add(text)
        option, created = AnswerOption.objects.get_or_create(
            question=question,
            text=text,
            defaults={"is_correct": bool(opt.get("is_correct"))},
        )
        if not created and option.is_correct != bool(opt.get("is_correct")):
            option.is_correct = bool(opt.get("is_correct"))
            option.save(update_fields=["is_correct"])

    question.options.exclude(text__in=seen_texts).delete()


def _sync_question(quiz: Quiz, question_data: dict) -> Question:
    text = question_data["text"].strip()
    points = int(question_data.get("points", 10))
    explanation = question_data.get("explanation", "").strip()
    question_type = question_data.get("type", Question.TYPE_MULTIPLE_CHOICE)
    interactive_data = question_data.get("interactive", {})
    format_tag = question_data.get(
        "format",
        Question.FORMAT_GRID
        if question_type == Question.TYPE_MULTIPLE_CHOICE
        else Question.FORMAT_INTERACTIVE,
    )
    question, created = Question.objects.get_or_create(
        quiz=quiz,
        text=text,
        defaults={
            "points": points,
            "explanation": explanation,
            "question_type": question_type,
            "interactive_data": interactive_data,
            "format_tag": format_tag,
        },
    )
    updated_fields = []
    if not created and question.points != points:
        question.points = points
        updated_fields.append("points")
    if not created and question.explanation != explanation:
        question.explanation = explanation
        updated_fields.append("explanation")
    if not created and question.question_type != question_type:
        question.question_type = question_type
        updated_fields.append("question_type")
    if not created and question.interactive_data != interactive_data:
        question.interactive_data = interactive_data
        updated_fields.append("interactive_data")
    if not created and question.format_tag != format_tag:
        question.format_tag = format_tag
        updated_fields.append("format_tag")
    if updated_fields:
        question.save(update_fields=updated_fields)
    _sync_options(question, question_data.get("options", []))
    return question


def sync_quiz_from_dict(
    data: dict,
    *,
    chapter: Chapter | None = None,
    source_file: str = "",
    order: int = 0,
) -> tuple[Quiz, bool]:
    title = data["title"].strip()
    class_levels = normalize_class_levels(data, chapter)
    exam_slugs = normalize_exam_slugs(data, chapter)
    defaults = {
        "title": title,
        "description": data.get("description", ""),
        "difficulty": data["difficulty"],
        "chapter": chapter,
        "class_levels": class_levels,
        "exam_slugs": exam_slugs,
        "order": order,
    }
    if source_file:
        quiz, created = Quiz.objects.update_or_create(
            source_file=source_file,
            defaults=defaults,
        )
    else:
        quiz, created = Quiz.objects.get_or_create(title=title, defaults=defaults)

    seen_question_texts = set()
    for question_data in data["questions"]:
        question = _sync_question(quiz, question_data)
        seen_question_texts.add(question.text)

    quiz.questions.exclude(text__in=seen_question_texts).delete()
    return quiz, created


@transaction.atomic
def load_chapters_manifest(
    data_dir: Path | None = None,
) -> dict[str, tuple[Chapter, int]]:
    directory = data_dir or quizzes_data_dir()
    manifest_path = directory / CHAPTERS_MANIFEST
    if not manifest_path.exists():
        return {}

    with manifest_path.open(encoding="utf-8") as f:
        data = json.load(f)
    _validate_chapters_manifest(data, CHAPTERS_MANIFEST)

    file_to_chapter: dict[str, tuple[Chapter, int]] = {}
    for chapter_data in data:
        chapter, _ = Chapter.objects.update_or_create(
            class_level=int(chapter_data["class_level"]),
            slug=chapter_data["slug"].strip(),
            defaults={
                "title": chapter_data["title"].strip(),
                "order": int(chapter_data.get("order", 0)),
                "exam_slug": chapter_data.get("exam_slug", "").strip(),
            },
        )
        for topic_order, filename in enumerate(chapter_data["topics"], start=1):
            file_to_chapter[filename] = (chapter, topic_order)

    return file_to_chapter


@transaction.atomic
def load_quiz_file(
    path: Path,
    chapter: Chapter | None = None,
    order: int = 0,
) -> tuple[Quiz, bool]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    _validate_quiz_payload(data, path.name)
    return sync_quiz_from_dict(
        data,
        chapter=chapter,
        source_file=path.name,
        order=order,
    )


@transaction.atomic
def load_all_quizzes(
    data_dir: Path | None = None,
    only_file: str | None = None,
) -> list[tuple[Quiz, bool, str]]:
    directory = data_dir or quizzes_data_dir()
    if not directory.exists():
        return []

    file_to_chapter = load_chapters_manifest(directory)
    if only_file:
        paths = [directory / only_file]
    else:
        if file_to_chapter:
            paths = [directory / name for name in sorted(file_to_chapter.keys())]
        else:
            paths = sorted(
                p for p in directory.glob("*.json") if p.name != CHAPTERS_MANIFEST
            )

    results = []
    for path in paths:
        if not path.exists():
            continue
        if path.name.startswith("_") or path.name == CHAPTERS_MANIFEST:
            continue
        chapter_info = file_to_chapter.get(path.name)
        chapter, topic_order = chapter_info if chapter_info else (None, 0)
        quiz, created = load_quiz_file(path, chapter=chapter, order=topic_order)
        results.append((quiz, created, path.name))
    return results
