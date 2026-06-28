from django.conf import settings
from django.db import models


class QuizTag(models.Model):
    """Etichete pentru clasă, examen etc.; un chestionar poate avea mai multe tag-uri."""

    KIND_CLASS = "class"
    KIND_EXAM = "exam"
    KIND_CHOICES = [
        (KIND_CLASS, "Clasă"),
        (KIND_EXAM, "Examen"),
    ]

    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=80)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "slug"]

    def __str__(self):
        return self.name


class Quiz(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("easy", "Easy"),
            ("medium", "Medium"),
            ("hard", "Hard"),
        ],
    )
    tags = models.ManyToManyField(
        QuizTag,
        related_name="quizzes",
        blank=True,
    )
    max_xp = models.PositiveIntegerField(
        default=50,
        help_text="XP maxim la finalizare. XP acordat = acest număr × (scor / scor maxim). 0 = fără XP.",
    )

    def __str__(self):
        return self.title


class Question(models.Model):
    """Întrebare reutilizabilă; legătura la chestionare se face prin QuizQuestion."""

    text = models.TextField()
    points = models.IntegerField(default=10)

    def __str__(self):
        return self.text[:50]


class QuizQuestion(models.Model):
    """Legătură many-to-many între Quiz și Question, cu ordine în cadrul chestionarului."""

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="question_links",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="quiz_links",
    )
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["quiz", "question"],
                name="quizzes_quizquestion_unique_quiz_question",
            ),
        ]

    def __str__(self):
        return f"{self.quiz_id}:{self.question_id}"


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
