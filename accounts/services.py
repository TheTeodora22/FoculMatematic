XP_PER_LEVEL = 100


def level_for_xp(xp: int) -> int:
    return 1 + xp // XP_PER_LEVEL


def xp_progress(profile) -> dict:
    """XP în nivelul curent și XP necesar pentru următorul nivel."""
    xp_in_level = profile.xp % XP_PER_LEVEL
    return {
        "xp_in_level": xp_in_level,
        "xp_needed": XP_PER_LEVEL,
        "xp_to_next": XP_PER_LEVEL - xp_in_level,
        "next_level": profile.level + 1,
    }


def get_recent_quiz_activities(user, limit: int = 5) -> list[dict]:
    from django.db.models import Count, Q
    from django.urls import reverse

    from quizzes.models import GeneratedQuizSession, QuizAttempt

    activities: list[dict] = []

    for attempt in (
        QuizAttempt.objects.filter(user=user)
        .select_related("quiz")
        .order_by("-created_at")[:limit]
    ):
        activities.append(
            {
                "kind": "classic",
                "title": attempt.quiz.title,
                "score": attempt.score,
                "max_score": attempt.max_score,
                "when": attempt.created_at,
                "result_url": reverse(
                    "quiz_result",
                    kwargs={"pk": attempt.quiz_id, "attempt_id": attempt.pk},
                ),
            }
        )

    for session in (
        GeneratedQuizSession.objects.filter(
            user=user,
            status=GeneratedQuizSession.STATUS_COMPLETED,
        )
        .select_related("topic")
        .annotate(
            correct_count=Count("items", filter=Q(items__is_correct=True)),
            total_count=Count("items"),
        )
        .order_by("-updated_at")[:limit]
    ):
        activities.append(
            {
                "kind": "generated",
                "title": session.topic.title,
                "score": session.correct_count,
                "max_score": session.total_count,
                "when": session.updated_at,
                "result_url": reverse(
                    "generated_quiz_result",
                    kwargs={"pk": session.topic_id},
                ),
            }
        )

    activities.sort(key=lambda item: item["when"], reverse=True)
    return activities[:limit]


def award_quiz_xp(profile, score: int) -> tuple[int, bool]:
    """Acordă XP egal cu punctajul quiz-ului. Returnează (xp_câștigat, level_up)."""
    if score <= 0:
        return 0, False

    old_level = profile.level
    profile.xp += score
    profile.level = level_for_xp(profile.xp)
    profile.save(update_fields=["xp", "level"])
    return score, profile.level > old_level


def get_quiz_stats(user) -> dict:
    from django.db.models import Count, Q, Sum

    from quizzes.models import GeneratedQuizSession, QuizAttempt

    quizzes_count = QuizAttempt.objects.filter(user=user).count()
    quizzes_count += GeneratedQuizSession.objects.filter(
        user=user,
        status=GeneratedQuizSession.STATUS_COMPLETED,
    ).count()

    total_correct = 0
    total_answered = 0

    for attempt in QuizAttempt.objects.filter(user=user):
        total_correct += attempt.score
        total_answered += attempt.max_score

    session_stats = (
        GeneratedQuizSession.objects.filter(
            user=user,
            status=GeneratedQuizSession.STATUS_COMPLETED,
        )
        .annotate(
            correct_count=Count("items", filter=Q(items__is_correct=True)),
            total_count=Count("items"),
        )
        .aggregate(
            correct=Sum("correct_count"),
            total=Sum("total_count"),
        )
    )
    total_correct += session_stats["correct"] or 0
    total_answered += session_stats["total"] or 0

    correct_rate = None
    if total_answered > 0:
        correct_rate = round(total_correct / total_answered * 100)

    return {
        "quizzes_count": quizzes_count,
        "correct_rate": correct_rate,
    }


def get_battlepass_preview(user) -> dict | None:
    from battlepass.services import get_battlepass_progress

    progress = get_battlepass_progress(user)
    season = progress["season"]
    profile = progress["profile"]

    if season is None:
        return None

    for item in progress["tiers"]:
        if not item["unlocked"]:
            tier = item["tier"]
            return {
                "reward_name": tier.reward_name,
                "level_req": tier.level_req,
                "levels_remaining": max(0, tier.level_req - profile.level),
                "xp_to_next_level": xp_progress(profile)["xp_to_next"],
            }

    return {
        "all_unlocked": True,
        "season_name": season.name,
    }


def get_profile_dashboard(user) -> dict:
    from django.urls import reverse

    from accounts.avatars import get_avatar_static_path
    from accounts.utils import get_or_create_profile

    profile = get_or_create_profile(user)
    quiz_stats = get_quiz_stats(user)

    return {
        "profile": profile,
        "xp_progress": xp_progress(profile),
        "recent_activities": get_recent_quiz_activities(user),
        "avatar_path": get_avatar_static_path(profile.avatar),
        "class_url": reverse("class_chapters", args=[profile.clasa]),
        "battlepass_preview": get_battlepass_preview(user),
        **quiz_stats,
    }
