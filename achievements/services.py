"""Achievement rule checks and unlocks."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import IntegrityError
from django.db.models import F

from accounts.models import Profile


def _qualifies(user: AbstractUser, achievement) -> bool:
    from battlepass.models import OwnedItem
    from FoculMatematic.models import QuizAttempt as LessonQuizAttempt
    from quizzes.models import QuizAttempt as LegacyQuizAttempt

    try:
        profile = user.profile
    except Profile.DoesNotExist:
        return False

    t = achievement.trigger
    th = achievement.threshold

    if t == achievement.TRIGGER_FIRST_LESSON_QUIZ:
        return LessonQuizAttempt.objects.filter(user=user).exists()

    if t == achievement.TRIGGER_PERFECT_LESSON_QUIZ:
        return LessonQuizAttempt.objects.filter(
            user=user, max_score__gt=0, score=F("max_score")
        ).exists()

    if t == achievement.TRIGGER_LESSON_QUIZ_TOTAL:
        return th > 0 and LessonQuizAttempt.objects.filter(user=user).count() >= th

    if t == achievement.TRIGGER_FIRST_LEGACY_QUIZ:
        return LegacyQuizAttempt.objects.filter(user=user).exists()

    if t == achievement.TRIGGER_LEGACY_QUIZ_TOTAL:
        return th > 0 and LegacyQuizAttempt.objects.filter(user=user).count() >= th

    if t == achievement.TRIGGER_ANY_QUIZ_TOTAL:
        if th <= 0:
            return False
        n = LessonQuizAttempt.objects.filter(user=user).count()
        n += LegacyQuizAttempt.objects.filter(user=user).count()
        return n >= th

    if t == achievement.TRIGGER_LEVEL_AT_LEAST:
        return th > 0 and profile.level >= th

    if t == achievement.TRIGGER_XP_TOTAL:
        return th > 0 and profile.xp >= th

    if t == achievement.TRIGGER_BATTLEPASS_CLAIMS:
        return th > 0 and (
            OwnedItem.objects.filter(
                user=user,
                item_key__startswith="battlepass_tier_",
            ).count()
            >= th
        )

    return False


def sync_achievements(user: AbstractUser) -> list[str]:
    """
    Unlock every achievement the user qualifies for.
    Returns titles of newly unlocked achievements (for flash messages).
    """
    from .models import Achievement, UserAchievement

    if not user.is_authenticated:
        return []

    new_titles: list[str] = []
    existing = set(
        UserAchievement.objects.filter(user=user).values_list(
            "achievement_id",
            flat=True,
        )
    )

    for ach in Achievement.objects.order_by("sort_order", "slug"):
        if ach.id in existing:
            continue
        if not _qualifies(user, ach):
            continue
        try:
            UserAchievement.objects.create(user=user, achievement=ach)
            new_titles.append(ach.title)
        except IntegrityError:
            pass
        existing.add(ach.id)

    return new_titles


def flash_new_achievements(request, user: AbstractUser) -> None:
    """Flash messages for achievements unlocked in this request (e.g. after a quiz)."""
    from django.contrib import messages

    for title in sync_achievements(user):
        messages.success(request, f"Achievement unlocked: {title}")


def progress_hint(user: AbstractUser, achievement) -> tuple[int, int] | None:
    """
    For threshold-based achievements: (current, target), or None if not applicable.
    """
    from FoculMatematic.models import QuizAttempt as LessonQuizAttempt
    from quizzes.models import QuizAttempt as LegacyQuizAttempt

    try:
        profile = user.profile
    except Profile.DoesNotExist:
        return None

    t = achievement.trigger
    th = achievement.threshold

    if t == achievement.TRIGGER_LESSON_QUIZ_TOTAL:
        if th <= 0:
            return None
        cur = LessonQuizAttempt.objects.filter(user=user).count()
        return cur, th
    if t == achievement.TRIGGER_LEGACY_QUIZ_TOTAL:
        if th <= 0:
            return None
        cur = LegacyQuizAttempt.objects.filter(user=user).count()
        return cur, th
    if t == achievement.TRIGGER_ANY_QUIZ_TOTAL:
        if th <= 0:
            return None
        cur = LessonQuizAttempt.objects.filter(user=user).count()
        cur += LegacyQuizAttempt.objects.filter(user=user).count()
        return cur, th
    if t == achievement.TRIGGER_LEVEL_AT_LEAST:
        if th <= 0:
            return None
        return profile.level, th
    if t == achievement.TRIGGER_XP_TOTAL:
        if th <= 0:
            return None
        return profile.xp, th
    if t == achievement.TRIGGER_BATTLEPASS_CLAIMS:
        if th <= 0:
            return None
        from battlepass.models import OwnedItem

        cur = OwnedItem.objects.filter(
            user=user,
            item_key__startswith="battlepass_tier_",
        ).count()
        return cur, th
    return None
