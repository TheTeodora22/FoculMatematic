from django.db.models import Count, Prefetch, Q
from django.urls import reverse

from .models import (
    Chapter,
    GeneratedQuizSession,
    GeneratedQuizSessionQuestion,
    Question,
    Quiz,
    UserQuestionProgress,
)


def _percent(done: int, total: int) -> int:
    if total <= 0:
        return 0
    return round(done / total * 100)


def _topic_training_counts(user, topic_ids: list[int]) -> dict[int, dict]:
    if not topic_ids:
        return {}

    rows = (
        UserQuestionProgress.objects.filter(
            user=user,
            question__quiz_id__in=topic_ids,
        )
        .values("question__quiz_id")
        .annotate(
            correct=Count(
                "id",
                filter=Q(training_status=UserQuestionProgress.TRAINING_CORRECT),
            ),
            wrong=Count(
                "id",
                filter=Q(training_status=UserQuestionProgress.TRAINING_WRONG),
            ),
            touched=Count("id"),
        )
    )
    return {
        row["question__quiz_id"]: {
            "correct": row["correct"],
            "wrong": row["wrong"],
            "touched": row["touched"],
        }
        for row in rows
    }


def _topic_question_counts(topic_ids: list[int]) -> dict[int, int]:
    if not topic_ids:
        return {}
    return dict(
        Question.objects.filter(quiz_id__in=topic_ids)
        .values("quiz_id")
        .annotate(total=Count("id"))
        .values_list("quiz_id", "total")
    )


def _in_progress_sessions(user, topic_ids: list[int]) -> dict[int, GeneratedQuizSession]:
    if not topic_ids:
        return {}
    sessions = (
        GeneratedQuizSession.objects.filter(
            user=user,
            topic_id__in=topic_ids,
            status=GeneratedQuizSession.STATUS_IN_PROGRESS,
        )
        .annotate(
            answered_count=Count("items", filter=Q(items__selected_option__isnull=False)),
            total_count=Count("items"),
        )
        .order_by("-updated_at")
    )
    latest_by_topic = {}
    for session in sessions:
        latest_by_topic.setdefault(session.topic_id, session)
    return latest_by_topic


def get_topic_learning_state(user, topic: Quiz) -> dict:
    topic_ids = [topic.pk]
    counts = _topic_question_counts(topic_ids).get(topic.pk, 0)
    training = _topic_training_counts(user, topic_ids).get(
        topic.pk,
        {"correct": 0, "wrong": 0, "touched": 0},
    )
    in_progress = _in_progress_sessions(user, topic_ids).get(topic.pk)
    unanswered = max(0, counts - training["correct"] - training["wrong"])

    last_completed = (
        GeneratedQuizSession.objects.filter(
            user=user,
            topic=topic,
            status=GeneratedQuizSession.STATUS_COMPLETED,
        )
        .annotate(
            correct_count=Count("items", filter=Q(items__is_correct=True)),
            total_count=Count("items"),
        )
        .order_by("-updated_at")
        .first()
    )

    next_action = {
        "label": "Incepe antrenarea",
        "url": reverse("training", args=[topic.pk]),
        "kind": "training",
    }
    if in_progress:
        next_action = {
            "label": "Continua chestionarul",
            "url": reverse("generated_quiz", args=[topic.pk]),
            "kind": "resume",
        }
    elif training["wrong"] > 0:
        next_action = {
            "label": "Reia greselile",
            "url": reverse("training", args=[topic.pk]),
            "kind": "review",
        }
    elif counts and training["correct"] >= counts:
        next_action = {
            "label": "Genereaza test de verificare",
            "url": reverse("generated_quiz", args=[topic.pk]),
            "kind": "quiz",
        }

    return {
        "question_count": counts,
        "training_correct": training["correct"],
        "training_wrong": training["wrong"],
        "training_unanswered": unanswered,
        "training_percent": _percent(training["correct"], counts),
        "in_progress": in_progress,
        "last_completed": last_completed,
        "next_action": next_action,
    }


def get_topics_learning_states(user, topics) -> list[dict]:
    topics = list(topics)
    topic_ids = [topic.pk for topic in topics]
    question_counts = _topic_question_counts(topic_ids)
    training_counts = _topic_training_counts(user, topic_ids)
    sessions = _in_progress_sessions(user, topic_ids)

    states = []
    for topic in topics:
        total = question_counts.get(topic.pk, 0)
        training = training_counts.get(
            topic.pk,
            {"correct": 0, "wrong": 0, "touched": 0},
        )
        unanswered = max(0, total - training["correct"] - training["wrong"])
        in_progress = sessions.get(topic.pk)
        states.append(
            {
                "topic": topic,
                "question_count": total,
                "training_correct": training["correct"],
                "training_wrong": training["wrong"],
                "training_unanswered": unanswered,
                "training_percent": _percent(training["correct"], total),
                "in_progress": in_progress,
                "next_action_url": (
                    reverse("generated_quiz", args=[topic.pk])
                    if in_progress
                    else reverse("topic_detail", args=[topic.pk])
                ),
                "next_action_label": (
                    "Continua" if in_progress else "Deschide lectia"
                ),
            }
        )
    return states


def get_chapter_learning_states(user, chapters) -> list[dict]:
    chapters = list(chapters)
    states = []
    for chapter in chapters:
        topic_states = get_topics_learning_states(
            user,
            chapter.topics.order_by("order", "title"),
        )
        total_questions = sum(item["question_count"] for item in topic_states)
        correct = sum(item["training_correct"] for item in topic_states)
        wrong = sum(item["training_wrong"] for item in topic_states)
        states.append(
            {
                "chapter": chapter,
                "topic_count": len(topic_states),
                "question_count": total_questions,
                "training_correct": correct,
                "training_wrong": wrong,
                "training_percent": _percent(correct, total_questions),
                "in_progress_count": sum(1 for item in topic_states if item["in_progress"]),
            }
        )
    return states


def get_mistake_review_items(user, limit: int = 5) -> list[dict]:
    progress_items = (
        UserQuestionProgress.objects.filter(user=user)
        .filter(
            Q(training_status=UserQuestionProgress.TRAINING_WRONG)
            | Q(last_generated_quiz_correct=False)
        )
        .select_related("question", "question__quiz", "question__quiz__chapter")
        .order_by("-id")[:limit]
    )

    items = []
    seen_question_ids = set()
    for progress in progress_items:
        question = progress.question
        seen_question_ids.add(question.pk)
        items.append(
            {
                "question": question,
                "topic": question.quiz,
                "chapter": question.quiz.chapter,
                "reason": (
                    "Antrenare"
                    if progress.training_status == UserQuestionProgress.TRAINING_WRONG
                    else "Chestionar generat"
                ),
                "url": reverse("training", args=[question.quiz_id]),
            }
        )

    if len(items) >= limit:
        return items

    wrong_generated = (
        GeneratedQuizSessionQuestion.objects.filter(
            session__user=user,
            is_correct=False,
        )
        .exclude(question_id__in=seen_question_ids)
        .select_related("question", "question__quiz", "question__quiz__chapter")
        .order_by("-session__updated_at")[: limit - len(items)]
    )
    for item in wrong_generated:
        items.append(
            {
                "question": item.question,
                "topic": item.question.quiz,
                "chapter": item.question.quiz.chapter,
                "reason": "Chestionar generat",
                "url": reverse("training", args=[item.question.quiz_id]),
            }
        )
    return items


def get_next_learning_step(user) -> dict | None:
    from accounts.utils import get_or_create_profile

    profile = get_or_create_profile(user)

    in_progress = (
        GeneratedQuizSession.objects.filter(
            user=user,
            status=GeneratedQuizSession.STATUS_IN_PROGRESS,
            topic__chapter__class_level=profile.clasa,
        )
        .select_related("topic", "topic__chapter")
        .order_by("-updated_at")
        .first()
    )
    if in_progress:
        return {
            "title": in_progress.topic.title,
            "subtitle": "Ai un chestionar inceput.",
            "url": reverse("generated_quiz", args=[in_progress.topic_id]),
            "action": "Continua",
            "kind": "resume",
        }

    review_items = get_mistake_review_items(user, limit=1)
    if review_items:
        item = review_items[0]
        return {
            "title": item["topic"].title,
            "subtitle": "Ai greseli bune de reluat.",
            "url": item["url"],
            "action": "Reia greselile",
            "kind": "review",
        }

    topics = (
        Quiz.objects.filter(chapter__class_level=profile.clasa, chapter__exam_slug="")
        .select_related("chapter")
        .prefetch_related(Prefetch("questions", queryset=Question.objects.only("id")))
        .order_by("chapter__order", "order", "title")
    )
    for topic in topics:
        state = get_topic_learning_state(user, topic)
        if state["question_count"] and state["training_correct"] < state["question_count"]:
            return {
                "title": topic.title,
                "subtitle": f"{state['training_percent']}% antrenare finalizata.",
                "url": reverse("training", args=[topic.pk]),
                "action": "Continua antrenarea",
                "kind": "training",
            }

    first_chapter = (
        Chapter.objects.filter(class_level=profile.clasa, exam_slug="")
        .order_by("order", "title")
        .first()
    )
    if first_chapter:
        return {
            "title": f"Clasa a {profile.clasa}-a",
            "subtitle": "Ai parcurs tot ce avem marcat in antrenare.",
            "url": reverse("class_chapters", args=[profile.clasa]),
            "action": "Alege un capitol",
            "kind": "complete",
        }
    return None
