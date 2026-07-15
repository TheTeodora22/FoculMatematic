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
    return [q for q in questions if q.options.exists()]


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
