from django.conf import settings
from django.db import models


class Achievement(models.Model):
    """Badge unlocked automatically when its rule (trigger + threshold) is met."""

    slug = models.SlugField(max_length=80, unique=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=8,
        default="🏅",
        help_text="Emoji shown as the badge icon.",
    )

    TRIGGER_FIRST_LESSON_QUIZ = "first_lesson_quiz"
    TRIGGER_PERFECT_LESSON_QUIZ = "perfect_lesson_quiz"
    TRIGGER_LESSON_QUIZ_TOTAL = "lesson_quiz_total"
    TRIGGER_FIRST_LEGACY_QUIZ = "first_legacy_quiz"
    TRIGGER_LEGACY_QUIZ_TOTAL = "legacy_quiz_total"
    TRIGGER_ANY_QUIZ_TOTAL = "any_quiz_total"
    TRIGGER_LEVEL_AT_LEAST = "level_at_least"
    TRIGGER_XP_TOTAL = "xp_total"
    TRIGGER_BATTLEPASS_CLAIMS = "battlepass_claims"

    TRIGGER_CHOICES = [
        (TRIGGER_FIRST_LESSON_QUIZ, "First lesson quiz completed"),
        (TRIGGER_PERFECT_LESSON_QUIZ, "Lesson quiz: perfect score"),
        (TRIGGER_LESSON_QUIZ_TOTAL, "Total lesson quizzes completed"),
        (TRIGGER_FIRST_LEGACY_QUIZ, "First quiz from /quizzes/"),
        (TRIGGER_LEGACY_QUIZ_TOTAL, "Total /quizzes/ completions"),
        (TRIGGER_ANY_QUIZ_TOTAL, "Any quizzes (lessons + classic)"),
        (TRIGGER_LEVEL_AT_LEAST, "Player level ≥ threshold"),
        (TRIGGER_XP_TOTAL, "Total XP ≥ threshold"),
        (TRIGGER_BATTLEPASS_CLAIMS, "Battle Pass rewards claimed ≥ threshold"),
    ]

    trigger = models.CharField(max_length=40, choices=TRIGGER_CHOICES)
    threshold = models.PositiveIntegerField(
        default=0,
        help_text="For counters, min level, or XP: target value. Use 0 when not applicable.",
    )
    sort_order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["sort_order", "slug"]
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"

    def __str__(self):
        return self.title


class UserAchievement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="achievements_unlocked",
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name="unlocks",
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-unlocked_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "achievement"],
                name="achievements_userachievement_unique_user_achievement",
            ),
        ]
        verbose_name = "Unlocked achievement"
        verbose_name_plural = "Unlocked achievements"

    def __str__(self):
        return f"{self.user} · {self.achievement}"
