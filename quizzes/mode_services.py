import random

from django.db import transaction
from django.db.models import Prefetch

from accounts.services import award_quiz_xp
from accounts.utils import get_or_create_profile
from battlepass.services import grant_tier_rewards

from .models import (
    AnswerOption,
    GeneratedQuizSession,
    GeneratedQuizSessionQuestion,
    Question,
    Quiz,
    UserQuestionProgress,
)


class TopicModeError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def _valid_questions_for_topic(topic: Quiz) -> list[Question]:
    questions = list(
        topic.questions.prefetch_related("options").order_by("id")
    )
    return [
        q
        for q in questions
        if q.question_type == Question.TYPE_MULTIPLE_CHOICE and q.options.exists()
    ]


def _get_progress_map(user, question_ids: list[int]) -> dict[int, UserQuestionProgress]:
    if not question_ids:
        return {}
    existing = UserQuestionProgress.objects.filter(
        user=user, question_id__in=question_ids
    )
    return {p.question_id: p for p in existing}


def pick_questions_for_generated_quiz(user, topic: Quiz, count: int = 10) -> list[Question]:
    pool = _valid_questions_for_topic(topic)
    if not pool:
        return []

    target = min(count, len(pool))
    progress_map = _get_progress_map(user, [q.id for q in pool])

    group_a = []
    group_b = []
    group_c = []
    for question in pool:
        progress = progress_map.get(question.id)
        if progress is None or not progress.seen_in_generated_quiz:
            group_a.append(question)
        elif progress.last_generated_quiz_correct is False:
            group_b.append(question)
        else:
            group_c.append(question)

    random.shuffle(group_a)
    random.shuffle(group_b)
    random.shuffle(group_c)

    ordered = group_a + group_b + group_c
    return ordered[:target]


def get_in_progress_session(user, topic: Quiz):
    return (
        GeneratedQuizSession.objects.filter(
            user=user,
            topic=topic,
            status=GeneratedQuizSession.STATUS_IN_PROGRESS,
        )
        .prefetch_related(
            Prefetch(
                "items",
                queryset=GeneratedQuizSessionQuestion.objects.select_related(
                    "question", "selected_option"
                ).prefetch_related("question__options").order_by("order"),
            )
        )
        .first()
    )


@transaction.atomic
def start_or_resume_generated_session(user, topic: Quiz) -> GeneratedQuizSession:
    existing = get_in_progress_session(user, topic)
    if existing:
        return existing

    selected = pick_questions_for_generated_quiz(user, topic)
    if not selected:
        raise TopicModeError("Acest subiect nu are întrebări disponibile.")

    session = GeneratedQuizSession.objects.create(user=user, topic=topic)
    GeneratedQuizSessionQuestion.objects.bulk_create(
        [
            GeneratedQuizSessionQuestion(
                session=session,
                question=question,
                order=index,
            )
            for index, question in enumerate(selected)
        ]
    )
    return get_in_progress_session(user, topic)


def get_session_item(session: GeneratedQuizSession, index: int):
    return session.items.filter(order=index).select_related("question").first()


def submit_generated_answer(
    session: GeneratedQuizSession,
    item: GeneratedQuizSessionQuestion,
    option_id: int,
) -> bool:
    if item.selected_option_id is not None:
        raise TopicModeError("Ai răspuns deja la această întrebare.")

    option = AnswerOption.objects.filter(
        pk=option_id, question_id=item.question_id
    ).first()
    if option is None:
        raise TopicModeError("Răspuns invalid.")

    is_correct = option.is_correct
    item.selected_option = option
    item.is_correct = is_correct
    item.save(update_fields=["selected_option", "is_correct"])

    progress, _ = UserQuestionProgress.objects.get_or_create(
        user=session.user,
        question=item.question,
    )
    progress.seen_in_generated_quiz = True
    progress.last_generated_quiz_correct = is_correct
    progress.save(update_fields=["seen_in_generated_quiz", "last_generated_quiz_correct"])

    if item.order >= session.current_index:
        session.current_index = min(item.order + 1, session.items.count())
        session.save(update_fields=["current_index", "updated_at"])

    return is_correct


def session_is_complete(session: GeneratedQuizSession) -> bool:
    return not session.items.filter(selected_option__isnull=True).exists()


@transaction.atomic
def complete_generated_session(session: GeneratedQuizSession) -> dict:
    if session.status == GeneratedQuizSession.STATUS_COMPLETED:
        raise TopicModeError("Sesiunea este deja finalizată.")
    if not session_is_complete(session):
        raise TopicModeError("Răspunde la toate întrebările înainte de finalizare.")

    xp_gained = 0
    for item in session.items.select_related("question").filter(is_correct=True):
        progress, _ = UserQuestionProgress.objects.get_or_create(
            user=session.user,
            question=item.question,
        )
        if not progress.xp_awarded:
            xp_gained += item.question.points
            progress.xp_awarded = True
            progress.save(update_fields=["xp_awarded"])

    profile = get_or_create_profile(session.user)
    leveled_up = False
    new_rewards = []
    new_level = profile.level
    if xp_gained > 0:
        _, leveled_up = award_quiz_xp(profile, xp_gained)
        new_level = profile.level
        if leveled_up:
            new_rewards = grant_tier_rewards(session.user, profile.level)

    session.status = GeneratedQuizSession.STATUS_COMPLETED
    session.save(update_fields=["status", "updated_at"])

    correct_count = session.items.filter(is_correct=True).count()
    total_count = session.items.count()
    return {
        "session": session,
        "correct_count": correct_count,
        "total_count": total_count,
        "xp_gained": xp_gained,
        "leveled_up": leveled_up,
        "new_level": new_level if leveled_up else None,
        "new_rewards": new_rewards,
    }


def get_training_questions(topic: Quiz) -> list[Question]:
    return list(
        topic.questions.prefetch_related("options").order_by("id")
    )


def get_training_states(user, topic: Quiz) -> list[dict]:
    questions = get_training_questions(topic)
    progress_map = _get_progress_map(user, [q.id for q in questions])
    states = []
    for question in questions:
        progress = progress_map.get(question.id)
        status = (
            progress.training_status
            if progress
            else UserQuestionProgress.TRAINING_UNANSWERED
        )
        states.append({"question": question, "status": status})
    return states


def submit_training_answer(user, question: Question, option_id: int) -> dict:
    if question.question_type != Question.TYPE_MULTIPLE_CHOICE:
        raise TopicModeError("Acest exercițiu nu folosește variante de răspuns.")
    option = AnswerOption.objects.filter(pk=option_id, question=question).first()
    if option is None:
        raise TopicModeError("Răspuns invalid.")

    is_correct = option.is_correct
    progress, _ = UserQuestionProgress.objects.get_or_create(
        user=user,
        question=question,
    )
    progress.training_status = (
        UserQuestionProgress.TRAINING_CORRECT
        if is_correct
        else UserQuestionProgress.TRAINING_WRONG
    )
    progress.save(update_fields=["training_status"])

    return {
        "is_correct": is_correct,
        "explanation": question.explanation if is_correct else "",
        "status": progress.training_status,
        "selected_option_id": option.id,
    }


def submit_parentheses_answer(
    user,
    question: Question,
    open_index: int,
    close_index: int,
) -> dict:
    if question.question_type not in {
        Question.TYPE_PARENTHESES_DRAG,
        Question.TYPE_PARENTHESES_TARGET,
    }:
        raise TopicModeError("Acest exercițiu nu folosește paranteze interactive.")

    data = question.interactive_data or {}
    tokens = data.get("tokens", [])
    if not 0 <= open_index < close_index <= len(tokens):
        raise TopicModeError("Pozițiile parantezelor sunt invalide.")

    is_correct = (
        open_index == data.get("correct_open_index")
        and close_index == data.get("correct_close_index")
    )
    return _save_interactive_result(
        user,
        question,
        is_correct,
        open_index=open_index,
        close_index=close_index,
    )


def _save_interactive_result(user, question: Question, is_correct: bool, **response) -> dict:
    progress, _ = UserQuestionProgress.objects.get_or_create(
        user=user,
        question=question,
    )
    progress.training_status = (
        UserQuestionProgress.TRAINING_CORRECT
        if is_correct
        else UserQuestionProgress.TRAINING_WRONG
    )
    progress.save(update_fields=["training_status"])

    return {
        "is_correct": is_correct,
        "explanation": question.explanation if is_correct else "",
        "status": progress.training_status,
        **response,
    }


def submit_column_subtraction_answer(
    user,
    question: Question,
    result_digits: str,
    borrow_columns: list[bool],
) -> dict:
    if question.question_type not in {
        Question.TYPE_COLUMN_SUBTRACTION,
        Question.TYPE_COLUMN_ADDITION,
        Question.TYPE_COLUMN_MULTIPLICATION,
    }:
        raise TopicModeError("Acest exercițiu nu este un calcul în coloană.")
    data = question.interactive_data or {}
    if not isinstance(result_digits, str) or not result_digits.isdigit():
        raise TopicModeError("Completează toate cifrele rezultatului.")
    if not isinstance(borrow_columns, list) or not all(
        isinstance(value, bool) for value in borrow_columns
    ):
        raise TopicModeError("Marcajele de împrumut sunt invalide.")
    marker_key = "borrow_columns" if question.question_type == Question.TYPE_COLUMN_SUBTRACTION else "carry_columns"
    is_correct = result_digits == data.get("correct_result") and borrow_columns == data.get(marker_key)
    return _save_interactive_result(user, question, is_correct)


def submit_missing_digits_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_MISSING_DIGITS:
        raise TopicModeError("Acest exercițiu nu conține cifre lipsă.")
    if not isinstance(values, dict):
        raise TopicModeError("Cifrele completate sunt invalide.")
    data = question.interactive_data or {}
    expected = {}
    for key in data.get("missing", []):
        row_name, raw_index = key.split(":", 1)
        expected[key] = data[row_name][int(raw_index)]
    normalized = {str(key): str(value) for key, value in values.items()}
    is_correct = normalized == expected
    return _save_interactive_result(user, question, is_correct)


def submit_error_spotting_answer(
    user,
    question: Question,
    selected_column: int,
) -> dict:
    if question.question_type != Question.TYPE_ERROR_SPOTTING:
        raise TopicModeError("Acest exercițiu nu este de tip detectarea greșelii.")
    data = question.interactive_data or {}
    width = len(data.get("correct_result", ""))
    if not 0 <= selected_column < width:
        raise TopicModeError("Coloana aleasă este invalidă.")
    is_correct = selected_column == data.get("error_column")
    return _save_interactive_result(
        user, question, is_correct, selected_column=selected_column
    )


def submit_input_output_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_INPUT_OUTPUT:
        raise TopicModeError("Acest exercițiu nu este o mașină intrare–ieșire.")
    if not isinstance(values, dict):
        raise TopicModeError("Valorile completate sunt invalide.")
    data = question.interactive_data or {}
    amount = data.get("value")
    operation = data.get("operation", "subtract")
    expected = {}
    for index, row in enumerate(data.get("rows", [])):
        if row.get("input") is None:
            if operation == "multiply":
                expected[f"{index}:input"] = str(row["output"] // amount)
            elif operation == "divide":
                expected[f"{index}:input"] = str(row["output"] * amount)
            else:
                expected[f"{index}:input"] = str(
                    row["output"] - amount if operation == "add" else row["output"] + amount
                )
        else:
            if operation == "multiply":
                expected[f"{index}:output"] = str(row["input"] * amount)
            elif operation == "divide":
                expected[f"{index}:output"] = str(row["input"] // amount)
            else:
                expected[f"{index}:output"] = str(
                    row["input"] + amount if operation == "add" else row["input"] - amount
                )
    normalized = {str(key): str(value).strip() for key, value in values.items()}
    is_correct = normalized == expected
    return _save_interactive_result(user, question, is_correct)


def submit_column_division_answer(user, question: Question, quotient: str, remainders: list) -> dict:
    if question.question_type != Question.TYPE_COLUMN_DIVISION:
        raise TopicModeError("Acest exercițiu nu este o împărțire în coloană.")
    data = question.interactive_data or {}
    normalized_remainders = [str(value).strip() for value in remainders] if isinstance(remainders, list) else []
    expected_remainders = [str(value) for value in data.get("remainders", [])]
    is_correct = str(quotient).strip() == str(data.get("quotient")) and normalized_remainders == expected_remainders
    return _save_interactive_result(user, question, is_correct)


def submit_division_relation_answer(user, question: Question, value: str) -> dict:
    if question.question_type != Question.TYPE_DIVISION_RELATION:
        raise TopicModeError("Acest exercițiu nu este o relație a împărțirii.")
    data = question.interactive_data or {}
    is_correct = str(value).strip() == str(data.get(data.get("missing")))
    return _save_interactive_result(user, question, is_correct)


def submit_operation_chain_answer(user, question: Question, values: list) -> dict:
    if question.question_type != Question.TYPE_OPERATION_CHAIN:
        raise TopicModeError("Acest exercițiu nu este un lanț de operații.")
    expected = [str(step.get("result")) for step in (question.interactive_data or {}).get("steps", [])]
    normalized = [str(value).strip() for value in values] if isinstance(values, list) else []
    return _save_interactive_result(user, question, normalized == expected)


def submit_division_table_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_DIVISION_TABLE:
        raise TopicModeError("Acest exercițiu nu este un tabel al împărțirii.")
    expected = {}
    for index, row in enumerate((question.interactive_data or {}).get("rows", [])):
        missing = row.get("missing")
        expected[f"{index}:{missing}"] = str(row.get(missing))
    normalized = {str(key): str(value).strip() for key, value in values.items()} if isinstance(values, dict) else {}
    return _save_interactive_result(user, question, normalized == expected)


def submit_numeric_input_answer(user, question: Question, value: str) -> dict:
    if question.question_type != Question.TYPE_NUMERIC_INPUT:
        raise TopicModeError("Acest exercițiu nu folosește un răspuns numeric.")
    is_correct = str(value).strip() == str((question.interactive_data or {}).get("answer"))
    return _save_interactive_result(user, question, is_correct)


def submit_factor_builder_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_FACTOR_BUILDER:
        raise TopicModeError("Acest exercițiu nu construiește o factorizare.")
    if not isinstance(values, dict):
        raise TopicModeError("Valorile completate sunt invalide.")
    data = question.interactive_data or {}
    expected = {"factor": str(data.get("common_factor")), "result": str(data.get("result"))}
    expected.update(
        {f"inner:{index}": str(term) for index, term in enumerate(data.get("inner_terms", []))}
    )
    normalized = {str(key): str(value).strip() for key, value in values.items()}
    return _save_interactive_result(user, question, normalized == expected)


def submit_factor_error_answer(user, question: Question, selected_step: int) -> dict:
    if question.question_type != Question.TYPE_FACTOR_ERROR:
        raise TopicModeError("Acest exercițiu nu cere detectarea unui pas greșit.")
    steps = (question.interactive_data or {}).get("steps", [])
    if not 0 <= selected_step < len(steps):
        raise TopicModeError("Pasul ales este invalid.")
    return _save_interactive_result(
        user,
        question,
        selected_step == question.interactive_data.get("error_index"),
        selected_step=selected_step,
    )


def submit_factor_match_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_FACTOR_MATCH:
        raise TopicModeError("Acest exercițiu nu conține perechi de expresii.")
    if not isinstance(values, dict):
        raise TopicModeError("Perechile alese sunt invalide.")
    pair_count = len((question.interactive_data or {}).get("pairs", []))
    expected = {str(index): str(index) for index in range(pair_count)}
    normalized = {str(key): str(value) for key, value in values.items()}
    return _save_interactive_result(user, question, normalized == expected)


def submit_power_values_answer(user, question: Question, values: dict) -> dict:
    allowed_types = {
        Question.TYPE_POWER_BUILDER,
        Question.TYPE_POWER_TABLE,
        Question.TYPE_POWER_CYCLE,
        Question.TYPE_POWER_SQUARE,
    }
    if question.question_type not in allowed_types:
        raise TopicModeError("Acest exercițiu nu folosește câmpuri pentru puteri.")
    if not isinstance(values, dict):
        raise TopicModeError("Valorile completate sunt invalide.")

    data = question.interactive_data or {}
    if question.question_type == Question.TYPE_POWER_BUILDER:
        mode = data.get("mode")
        if mode == "compose":
            expected = {"base": str(data.get("base")), "exponent": str(data.get("exponent"))}
        elif mode == "expand":
            expected = {
                f"factor:{index}": str(factor)
                for index, factor in enumerate(data.get("factors", []))
            }
        else:
            missing = data.get("missing")
            expected = {str(missing): str(data.get(missing))}
    elif question.question_type == Question.TYPE_POWER_TABLE:
        expected = {
            f"{index}:{row['missing']}": str(row[row["missing"]])
            for index, row in enumerate(data.get("rows", []))
        }
    elif question.question_type == Question.TYPE_POWER_CYCLE:
        expected = {
            **{f"cycle:{index}": str(digit) for index, digit in enumerate(data.get("cycle", []))},
            "last_digit": str(data.get("last_digit")),
        }
    else:
        expected = {"base": str(data.get("side")), "exponent": "2", "value": str(data.get("value"))}

    normalized = {str(key): str(value).strip() for key, value in values.items()}
    return _save_interactive_result(user, question, normalized == expected)


def submit_power_match_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_POWER_MATCH:
        raise TopicModeError("Acest exercițiu nu conține forme echivalente ale puterilor.")
    if not isinstance(values, dict):
        raise TopicModeError("Perechile alese sunt invalide.")
    pair_count = len((question.interactive_data or {}).get("pairs", []))
    expected = {str(index): str(index) for index in range(pair_count)}
    normalized = {str(key): str(value) for key, value in values.items()}
    return _save_interactive_result(user, question, normalized == expected)


def submit_power_rule_chain_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_POWER_RULE_CHAIN:
        raise TopicModeError("Acest exercițiu nu conține un lanț de reguli pentru puteri.")
    if not isinstance(values, dict):
        raise TopicModeError("Exponenții completați sunt invalizi.")
    stages = (question.interactive_data or {}).get("stages", [])
    expected = {f"stage:{index}": str(stage["exponent"]) for index, stage in enumerate(stages)}
    normalized = {str(key): str(value).strip() for key, value in values.items()}
    return _save_interactive_result(user, question, normalized == expected)


def submit_power_compare_answer(user, question: Question, relation: str) -> dict:
    if question.question_type != Question.TYPE_POWER_COMPARE:
        raise TopicModeError("Acest exercițiu nu compară două puteri.")
    if relation not in {"<", "=", ">"}:
        raise TopicModeError("Semnul ales este invalid.")
    return _save_interactive_result(
        user,
        question,
        relation == (question.interactive_data or {}).get("relation"),
        selected_relation=relation,
    )


def submit_power_order_answer(user, question: Question, order: list) -> dict:
    if question.question_type != Question.TYPE_POWER_ORDER:
        raise TopicModeError("Acest exercițiu nu cere ordonarea puterilor.")
    data = question.interactive_data or {}
    items = data.get("items", [])
    if not isinstance(order, list) or sorted(order) != list(range(len(items))):
        raise TopicModeError("Ordinea trimisă este invalidă.")
    reverse = data.get("direction") == "desc"
    expected = sorted(range(len(items)), key=lambda index: items[index]["value"], reverse=reverse)
    return _save_interactive_result(user, question, order == expected)


def submit_base_values_answer(user, question: Question, values: dict) -> dict:
    if question.question_type not in {Question.TYPE_BASE_VALUES, Question.TYPE_BINARY_TOGGLE}:
        raise TopicModeError("Acest exercițiu nu folosește câmpuri pentru sisteme de numerație.")
    if not isinstance(values, dict):
        raise TopicModeError("Valorile completate sunt invalide.")
    data = question.interactive_data or {}
    expected = data.get("answers", {}) if question.question_type == Question.TYPE_BASE_VALUES else {"bits": data.get("binary")}
    normalized = {str(key): str(value).strip().upper() for key, value in values.items()}
    normalized_expected = {str(key): str(value).strip().upper() for key, value in expected.items()}
    return _save_interactive_result(user, question, normalized == normalized_expected)


def submit_base_match_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_BASE_MATCH:
        raise TopicModeError("Acest exercițiu nu conține reprezentări de potrivit.")
    if not isinstance(values, dict):
        raise TopicModeError("Perechile alese sunt invalide.")
    pair_count = len((question.interactive_data or {}).get("pairs", []))
    expected = {str(index): str(index) for index in range(pair_count)}
    normalized = {str(key): str(value) for key, value in values.items()}
    return _save_interactive_result(user, question, normalized == expected)


def submit_base_error_answer(user, question: Question, selected_step: int) -> dict:
    if question.question_type != Question.TYPE_BASE_ERROR:
        raise TopicModeError("Acest exercițiu nu cere detectarea unei erori de conversie.")
    steps = (question.interactive_data or {}).get("steps", [])
    if not 0 <= selected_step < len(steps):
        raise TopicModeError("Pasul ales este invalid.")
    return _save_interactive_result(
        user,
        question,
        selected_step == question.interactive_data.get("error_index"),
        selected_step=selected_step,
    )


def submit_unit_reduction_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_UNIT_REDUCTION:
        raise TopicModeError("Acest exercițiu nu folosește metoda reducerii la unitate.")
    if not isinstance(values, dict):
        raise TopicModeError("Valorile completate sunt invalide.")
    expected = (question.interactive_data or {}).get("answers", {})
    normalized = {str(key): str(value).strip() for key, value in values.items()}
    normalized_expected = {str(key): str(value).strip() for key, value in expected.items()}
    return _save_interactive_result(user, question, normalized == normalized_expected)


def submit_comparison_method_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_COMPARISON_METHOD:
        raise TopicModeError("Acest exercițiu nu folosește metoda comparației.")
    if not isinstance(values, dict):
        raise TopicModeError("Valorile completate sunt invalide.")
    expected = (question.interactive_data or {}).get("answers", {})
    normalized = {str(k): str(v).strip() for k, v in values.items()}
    normalized_expected = {str(k): str(v).strip() for k, v in expected.items()}
    return _save_interactive_result(user, question, normalized == normalized_expected)


def submit_figurative_method_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_FIGURATIVE_METHOD:
        raise TopicModeError("Acest exercițiu nu folosește metoda figurativă.")
    if not isinstance(values, dict):
        raise TopicModeError("Valorile completate sunt invalide.")
    expected = (question.interactive_data or {}).get("answers", {})
    normalized = {str(k): str(v).strip() for k, v in values.items()}
    normalized_expected = {str(k): str(v).strip() for k, v in expected.items()}
    return _save_interactive_result(user, question, normalized == normalized_expected)


def submit_reverse_method_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_REVERSE_METHOD:
        raise TopicModeError("Acest exercițiu nu folosește metoda mersului invers.")
    if not isinstance(values, dict):
        raise TopicModeError("Valorile completate sunt invalide.")
    expected = (question.interactive_data or {}).get("answers", {})
    normalized = {str(k): str(v).strip() for k, v in values.items()}
    normalized_expected = {str(k): str(v).strip() for k, v in expected.items()}
    return _save_interactive_result(user, question, normalized == normalized_expected)


def submit_false_hypothesis_method_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_FALSE_HYPOTHESIS_METHOD:
        raise TopicModeError("Acest exercițiu nu folosește metoda falsei ipoteze.")
    if not isinstance(values, dict):
        raise TopicModeError("Valorile completate sunt invalide.")
    expected = (question.interactive_data or {}).get("answers", {})
    normalized = {str(k): str(v).strip() for k, v in values.items()}
    normalized_expected = {str(k): str(v).strip() for k, v in expected.items()}
    return _save_interactive_result(user, question, normalized == normalized_expected)


def submit_operation_sequence_answer(user, question: Question, order: list) -> dict:
    if question.question_type != Question.TYPE_OPERATION_SEQUENCE:
        raise TopicModeError("Acest exercițiu nu construiește ordinea operațiilor.")
    steps = (question.interactive_data or {}).get("steps", [])
    if not isinstance(order, list) or sorted(order) != list(range(len(steps))):
        raise TopicModeError("Ordinea trimisă este invalidă.")
    expected = (question.interactive_data or {}).get("correct_order", [])
    return _save_interactive_result(user, question, order == expected)


def submit_operation_workbench_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_OPERATION_WORKBENCH:
        raise TopicModeError("Acest exercițiu nu conține etape de calcul.")
    if not isinstance(values, dict):
        raise TopicModeError("Rezultatele completate sunt invalide.")
    stages = (question.interactive_data or {}).get("stages", [])
    expected = {f"stage:{index}": str(stage["answer"]) for index, stage in enumerate(stages)}
    normalized = {str(key): str(value).strip() for key, value in values.items()}
    return _save_interactive_result(user, question, normalized == expected)


def submit_divisibility_values_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_DIVISIBILITY_VALUES:
        raise TopicModeError("Acest exercițiu nu completează divizori sau multipli.")
    if not isinstance(values, dict):
        raise TopicModeError("Valorile completate sunt invalide.")
    expected = (question.interactive_data or {}).get("answers", {})
    normalized = {str(key): str(value).strip().replace(" ", "") for key, value in values.items()}
    normalized_expected = {str(key): str(value).strip().replace(" ", "") for key, value in expected.items()}
    return _save_interactive_result(user, question, normalized == normalized_expected)


def submit_divisibility_select_answer(user, question: Question, selected_ids: list) -> dict:
    if question.question_type != Question.TYPE_DIVISIBILITY_SELECT:
        raise TopicModeError("Acest exercițiu nu cere selectarea unor numere.")
    if not isinstance(selected_ids, list):
        raise TopicModeError("Selecția trimisă este invalidă.")
    expected = sorted((question.interactive_data or {}).get("correct_ids", []))
    normalized = sorted({str(value) for value in selected_ids})
    return _save_interactive_result(user, question, normalized == expected)


def submit_divisibility_sort_answer(user, question: Question, placements: dict) -> dict:
    if question.question_type != Question.TYPE_DIVISIBILITY_SORT:
        raise TopicModeError("Acest exercițiu nu cere sortarea numerelor.")
    if not isinstance(placements, dict):
        raise TopicModeError("Sortarea trimisă este invalidă.")
    expected = {str(card["id"]): str(card["zone"]) for card in (question.interactive_data or {}).get("cards", [])}
    normalized = {str(key): str(value) for key, value in placements.items()}
    return _save_interactive_result(user, question, normalized == expected)


def submit_divisibility_error_answer(user, question: Question, selected_step: int) -> dict:
    if question.question_type != Question.TYPE_DIVISIBILITY_ERROR:
        raise TopicModeError("Acest exercițiu nu cere detectarea unei erori de divizibilitate.")
    steps = (question.interactive_data or {}).get("steps", [])
    if not 0 <= selected_step < len(steps):
        raise TopicModeError("Pasul ales este invalid.")
    return _save_interactive_result(
        user,
        question,
        selected_step == question.interactive_data.get("error_index"),
        selected_step=selected_step,
    )


def submit_criteria_table_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_CRITERIA_TABLE:
        raise TopicModeError("Acest exercițiu nu este un tabel al criteriilor de divizibilitate.")
    if not isinstance(values, dict):
        raise TopicModeError("Bifele trimise sunt invalide.")
    expected = {str(key): str(value).lower() for key, value in (question.interactive_data or {}).get("answers", {}).items()}
    normalized = {str(key): str(value).lower() for key, value in values.items()}
    return _save_interactive_result(user, question, normalized == expected)


def submit_prime_workbench_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_PRIME_WORKBENCH:
        raise TopicModeError("Acest exercițiu nu aparține atelierului numerelor prime.")
    if not isinstance(values, dict):
        raise TopicModeError("Răspunsurile trimise sunt invalide.")
    data = question.interactive_data or {}
    if data.get("mode") == "prime_pair":
        try:
            left, right = int(values.get("left", "")), int(values.get("right", ""))
        except (TypeError, ValueError):
            raise TopicModeError("Completează ambele numere prime.")
        def is_prime_number(number):
            return number >= 2 and all(number % divisor for divisor in range(2, int(number ** 0.5) + 1))
        operator, target = data.get("operator"), data.get("target")
        result = left + right if operator == "+" else left - right if operator == "−" else left * right
        return _save_interactive_result(user, question, is_prime_number(left) and is_prime_number(right) and result == target)
    expected = {
        str(key): str(value).strip().lower()
        for key, value in data.get("answers", {}).items()
    }
    normalized = {str(key): str(value).strip().lower() for key, value in values.items()}
    return _save_interactive_result(user, question, normalized == expected)


def submit_decimal_workbench_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_DECIMAL_WORKBENCH:
        raise TopicModeError("Acest exercițiu nu aparține atelierului fracțiilor zecimale.")
    if not isinstance(values, dict):
        raise TopicModeError("Răspunsurile trimise sunt invalide.")
    expected = {
        str(key): str(value).strip().replace(".", ",").replace(" ", "").lower()
        for key, value in (question.interactive_data or {}).get("answers", {}).items()
    }
    normalized = {
        str(key): str(value).strip().replace(".", ",").replace(" ", "").lower()
        for key, value in values.items()
    }
    return _save_interactive_result(user, question, normalized == expected)


def submit_fraction_visual_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_FRACTION_VISUAL:
        raise TopicModeError("Acest exercițiu nu conține o reprezentare de fracție.")
    if not isinstance(values, dict):
        raise TopicModeError("Răspunsul trimis este invalid.")
    expected = (question.interactive_data or {}).get("answers", {})
    normalized = {str(key): str(value).strip() for key, value in values.items()}
    normalized_expected = {str(key): str(value).strip() for key, value in expected.items()}
    return _save_interactive_result(user, question, normalized == normalized_expected)


def submit_fraction_domino_answer(user, question: Question, order: list) -> dict:
    if question.question_type != Question.TYPE_FRACTION_DOMINO:
        raise TopicModeError("Acest exercițiu nu este un domino cu fracții.")
    tiles = (question.interactive_data or {}).get("tiles", [])
    if not isinstance(order, list) or sorted(order) != list(range(len(tiles))):
        raise TopicModeError("Ordinea pieselor este invalidă.")
    expected = (question.interactive_data or {}).get("correct_order", [])
    return _save_interactive_result(user, question, order == expected)


def submit_fraction_compare_answer(user, question: Question, relation: str, order: list) -> dict:
    if question.question_type != Question.TYPE_FRACTION_COMPARE:
        raise TopicModeError("Acest exercițiu nu compară fracții.")
    data = question.interactive_data or {}
    if data.get("mode") == "order":
        items = data.get("items", [])
        if not isinstance(order, list) or sorted(order) != list(range(len(items))):
            raise TopicModeError("Ordinea fracțiilor este invalidă.")
        return _save_interactive_result(user, question, order == data.get("correct_order", []))
    if relation not in {"<", "=", ">"}:
        raise TopicModeError("Semnul ales este invalid.")
    return _save_interactive_result(user, question, relation == data.get("relation"))


def submit_fraction_axis_answer(user, question: Question, selected_tick: int) -> dict:
    if question.question_type != Question.TYPE_FRACTION_AXIS:
        raise TopicModeError("Acest exercițiu nu folosește axa numerelor.")
    total_ticks = (question.interactive_data or {}).get("denominator", 1) * (question.interactive_data or {}).get("maximum", 1)
    if not isinstance(selected_tick, int) or not 0 <= selected_tick <= total_ticks:
        raise TopicModeError("Punctul ales pe axă este invalid.")
    return _save_interactive_result(user, question, selected_tick == question.interactive_data.get("answer_tick"))


def _submit_expected_values(user, question: Question, expected_type: str, values: dict) -> dict:
    if question.question_type != expected_type:
        raise TopicModeError("Tipul exercițiului trimis este invalid.")
    if not isinstance(values, dict):
        raise TopicModeError("Valorile completate sunt invalide.")
    expected = (question.interactive_data or {}).get("answers", {})
    normalized = {str(key): str(value).strip().replace(" ", "") for key, value in values.items()}
    normalized_expected = {str(key): str(value).strip().replace(" ", "") for key, value in expected.items()}
    return _save_interactive_result(user, question, normalized == normalized_expected)


def submit_gcd_workbench_answer(user, question: Question, values: dict) -> dict:
    return _submit_expected_values(user, question, Question.TYPE_GCD_WORKBENCH, values)


def submit_fraction_scale_answer(user, question: Question, values: dict) -> dict:
    return _submit_expected_values(user, question, Question.TYPE_FRACTION_SCALE, values)


def submit_fraction_reduce_path_answer(user, question: Question, values: dict) -> dict:
    if question.question_type != Question.TYPE_FRACTION_REDUCE_PATH:
        raise TopicModeError("Acest exercițiu nu conține un traseu de simplificare.")
    if not isinstance(values, dict):
        raise TopicModeError("Etapele completate sunt invalide.")
    expected = {}
    for index, step in enumerate((question.interactive_data or {}).get("steps", [])):
        for key in ("factor", "numerator", "denominator"):
            expected[f"{index}:{key}"] = str(step[key])
    normalized = {str(key): str(value).strip() for key, value in values.items()}
    return _save_interactive_result(user, question, normalized == expected)


def submit_lcm_workbench_answer(user, question: Question, values: dict) -> dict:
    return _submit_expected_values(user, question, Question.TYPE_LCM_WORKBENCH, values)


def submit_common_denominator_answer(user, question: Question, values: dict) -> dict:
    return _submit_expected_values(user, question, Question.TYPE_COMMON_DENOMINATOR, values)


def reset_training_progress(user, topic: Quiz) -> int:
    question_ids = list(topic.questions.values_list("id", flat=True))
    updated = UserQuestionProgress.objects.filter(
        user=user,
        question_id__in=question_ids,
    ).update(training_status=UserQuestionProgress.TRAINING_UNANSWERED)
    return updated


def build_training_payload(
    user,
    topic: Quiz,
    current_index: int,
    submit_url: str,
) -> dict:
    questions = get_training_questions(topic)
    progress_map = _get_progress_map(user, [q.id for q in questions])
    payload_questions = []

    for question in questions:
        progress = progress_map.get(question.id)
        status = (
            progress.training_status
            if progress
            else UserQuestionProgress.TRAINING_UNANSWERED
        )
        options = list(question.options.all())
        correct_option = next((o for o in options if o.is_correct), None)
        payload_questions.append(
            {
                "id": question.id,
                "text": question.text,
                "explanation": question.explanation,
                "type": question.question_type,
                "format": question.format_tag,
                "interactive": question.interactive_data,
                "correctOptionId": correct_option.id if correct_option else None,
                "status": status,
                "options": [{"id": o.id, "text": o.text} for o in options],
            }
        )

    return {
        "topicId": topic.pk,
        "submitUrl": submit_url,
        "currentIndex": current_index,
        "questions": payload_questions,
    }
