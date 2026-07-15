from django.contrib.auth.models import User
from django.db import models


class Chapter(models.Model):
    class_level = models.IntegerField()
    slug = models.SlugField(max_length=120)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    exam_slug = models.SlugField(max_length=120, blank=True, default="")

    class Meta:
        ordering = ["class_level", "order", "title"]
        unique_together = [("class_level", "slug")]

    def __str__(self):
        return f"Clasa a {self.class_level}-a · {self.title}"


class Quiz(models.Model):
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="topics",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("easy", "Ușor"),
            ("medium", "Mediu"),
            ("hard", "Greu"),
        ],
    )
    source_file = models.CharField(max_length=255, blank=True)
    class_levels = models.JSONField(default=list, blank=True)
    exam_slugs = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["chapter__order", "title"]

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    points = models.IntegerField(default=10)
    explanation = models.TextField(blank=True)

    def __str__(self):
        return self.text[:50]


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class UserQuestionProgress(models.Model):
    TRAINING_UNANSWERED = "unanswered"
    TRAINING_CORRECT = "correct"
    TRAINING_WRONG = "wrong"
    TRAINING_STATUS_CHOICES = [
        (TRAINING_UNANSWERED, "Alb"),
        (TRAINING_CORRECT, "Verde"),
        (TRAINING_WRONG, "Roșu"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="question_progress")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="user_progress")
    xp_awarded = models.BooleanField(default=False)
    training_status = models.CharField(
        max_length=20,
        choices=TRAINING_STATUS_CHOICES,
        default=TRAINING_UNANSWERED,
    )
    seen_in_generated_quiz = models.BooleanField(default=False)
    last_generated_quiz_correct = models.BooleanField(null=True, blank=True)

    class Meta:
        unique_together = [("user", "question")]

    def __str__(self):
        return f"{self.user_id} · Q{self.question_id}"


class GeneratedQuizSession(models.Model):
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_IN_PROGRESS, "În curs"),
        (STATUS_COMPLETED, "Finalizat"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="generated_quiz_sessions")
    topic = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="generated_sessions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS)
    current_index = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Session {self.pk} · {self.topic.title}"


class GeneratedQuizSessionQuestion(models.Model):
    session = models.ForeignKey(
        GeneratedQuizSession,
        on_delete=models.CASCADE,
        related_name="items",
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()
    selected_option = models.ForeignKey(
        AnswerOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_correct = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ["order"]
        unique_together = [("session", "order")]

    def __str__(self):
        return f"Session {self.session_id} · #{self.order}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class QuizAttemptAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt, related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"{self.question_id}: {'✓' if self.is_correct else '✗'}"
