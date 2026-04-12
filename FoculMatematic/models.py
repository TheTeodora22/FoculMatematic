from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class SchoolClass(models.Model):
    """Clasă școlară (ex. Clasa a 8-a)."""

    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=80, unique=True)
    order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "slug"]
        verbose_name = "Clasă"
        verbose_name_plural = "Clase"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("school_class_detail", kwargs={"slug": self.slug})


class Chapter(models.Model):
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="chapters",
    )
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "slug"]
        verbose_name = "Capitol"
        verbose_name_plural = "Capitole"
        constraints = [
            models.UniqueConstraint(
                fields=["school_class", "slug"],
                name="foculmatematic_chapter_unique_slug_per_class",
            ),
        ]

    def __str__(self):
        return f"{self.school_class.title}: {self.title}"

    def get_absolute_url(self):
        base = reverse("school_class_chapters", kwargs={"slug": self.school_class.slug})
        return f"{base}#capitol-{self.slug}"


class Lesson(models.Model):
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=120,
        unique=True,
        help_text="Unic în tot site-ul (folosit în /lectii/&lt;slug&gt;/).",
    )
    content = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "slug"]
        verbose_name = "Lecție"
        verbose_name_plural = "Lecții"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("lesson_detail", kwargs={"lesson_slug": self.slug})

    @property
    def school_class(self):
        return self.chapter.school_class


class Question(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    text = models.TextField()
    points = models.PositiveSmallIntegerField(default=10)
    order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "pk"]
        verbose_name = "Întrebare (lecție)"
        verbose_name_plural = "Întrebări (lecții)"

    def __str__(self):
        return (self.text[:60] + "…") if len(self.text) > 60 else self.text


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["pk"]
        verbose_name = "Variantă"
        verbose_name_plural = "Variante"

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_quiz_attempts")
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Încercare quiz (lecție)"
        verbose_name_plural = "Încercări quiz (lecții)"

    def __str__(self):
        return f"{self.user} @ {self.lesson.slug} ({self.score}/{self.max_score})"


class Answer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="lesson_answers",
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name="picked_in_answers",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"],
                name="foculmatematic_answer_unique_attempt_question",
            ),
        ]
        verbose_name = "Răspuns"
        verbose_name_plural = "Răspunsuri"

    def __str__(self):
        return f"Q{self.question_id} → C{self.choice_id}"
