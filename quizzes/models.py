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
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["chapter__order", "order", "title"]

    def __str__(self):
        return self.title


class Question(models.Model):
    FORMAT_GRID = "grid"
    FORMAT_TRUE_FALSE = "true_false"
    FORMAT_INTERACTIVE = "interactive"
    FORMAT_CHOICES = [
        (FORMAT_GRID, "Grilă"),
        (FORMAT_TRUE_FALSE, "Adevărat sau fals"),
        (FORMAT_INTERACTIVE, "Interactiv"),
    ]
    TYPE_MULTIPLE_CHOICE = "multiple_choice"
    TYPE_PARENTHESES_DRAG = "parentheses_drag"
    TYPE_COLUMN_ADDITION = "column_addition"
    TYPE_COLUMN_MULTIPLICATION = "column_multiplication"
    TYPE_COLUMN_DIVISION = "column_division"
    TYPE_COLUMN_SUBTRACTION = "column_subtraction"
    TYPE_MISSING_DIGITS = "missing_digits"
    TYPE_ERROR_SPOTTING = "error_spotting"
    TYPE_PARENTHESES_TARGET = "parentheses_target"
    TYPE_INPUT_OUTPUT = "input_output"
    TYPE_DIVISION_RELATION = "division_relation"
    TYPE_OPERATION_CHAIN = "operation_chain"
    TYPE_DIVISION_TABLE = "division_table"
    TYPE_NUMERIC_INPUT = "numeric_input"
    TYPE_FACTOR_BUILDER = "factor_builder"
    TYPE_FACTOR_ERROR = "factor_error"
    TYPE_FACTOR_MATCH = "factor_match"
    TYPE_POWER_BUILDER = "power_builder"
    TYPE_POWER_MATCH = "power_match"
    TYPE_POWER_TABLE = "power_table"
    TYPE_POWER_CYCLE = "power_cycle"
    TYPE_POWER_SQUARE = "power_square"
    TYPE_POWER_RULE_CHAIN = "power_rule_chain"
    TYPE_POWER_COMPARE = "power_compare"
    TYPE_POWER_ORDER = "power_order"
    TYPE_BASE_VALUES = "base_values"
    TYPE_BASE_MATCH = "base_match"
    TYPE_BINARY_TOGGLE = "binary_toggle"
    TYPE_BASE_ERROR = "base_error"
    TYPE_UNIT_REDUCTION = "unit_reduction"
    TYPE_COMPARISON_METHOD = "comparison_method"
    TYPE_FIGURATIVE_METHOD = "figurative_method"
    TYPE_REVERSE_METHOD = "reverse_method"
    TYPE_FALSE_HYPOTHESIS_METHOD = "false_hypothesis_method"
    TYPE_OPERATION_SEQUENCE = "operation_sequence"
    TYPE_OPERATION_WORKBENCH = "operation_workbench"
    TYPE_DIVISIBILITY_VALUES = "divisibility_values"
    TYPE_DIVISIBILITY_SELECT = "divisibility_select"
    TYPE_DIVISIBILITY_SORT = "divisibility_sort"
    TYPE_DIVISIBILITY_ERROR = "divisibility_error"
    TYPE_CRITERIA_TABLE = "criteria_table"
    TYPE_PRIME_WORKBENCH = "prime_workbench"
    TYPE_DECIMAL_WORKBENCH = "decimal_workbench"
    TYPE_FRACTION_VISUAL = "fraction_visual"
    TYPE_FRACTION_DOMINO = "fraction_domino"
    TYPE_FRACTION_COMPARE = "fraction_compare"
    TYPE_FRACTION_AXIS = "fraction_axis"
    TYPE_GCD_WORKBENCH = "gcd_workbench"
    TYPE_FRACTION_SCALE = "fraction_scale"
    TYPE_FRACTION_REDUCE_PATH = "fraction_reduce_path"
    TYPE_LCM_WORKBENCH = "lcm_workbench"
    TYPE_COMMON_DENOMINATOR = "common_denominator"
    TYPE_CHOICES = [
        (TYPE_MULTIPLE_CHOICE, "Grilă"),
        (TYPE_PARENTHESES_DRAG, "Plasează parantezele"),
        (TYPE_COLUMN_ADDITION, "Adunare în coloană"),
        (TYPE_COLUMN_MULTIPLICATION, "Înmulțire în coloană"),
        (TYPE_COLUMN_DIVISION, "Împărțire în coloană"),
        (TYPE_COLUMN_SUBTRACTION, "Scădere în coloană"),
        (TYPE_MISSING_DIGITS, "Completează cifrele lipsă"),
        (TYPE_ERROR_SPOTTING, "Detectează greșeala"),
        (TYPE_PARENTHESES_TARGET, "Paranteze pentru rezultat-țintă"),
        (TYPE_INPUT_OUTPUT, "Mașină intrare–ieșire"),
        (TYPE_DIVISION_RELATION, "Relația împărțirii"),
        (TYPE_OPERATION_CHAIN, "Lanț de operații"),
        (TYPE_DIVISION_TABLE, "Tabelul împărțirii"),
        (TYPE_NUMERIC_INPUT, "Răspuns numeric"),
        (TYPE_FACTOR_BUILDER, "Construiește factorizarea"),
        (TYPE_FACTOR_ERROR, "Detectează pasul greșit"),
        (TYPE_FACTOR_MATCH, "Potrivește forme echivalente"),
        (TYPE_POWER_BUILDER, "Construiește sau desfă puterea"),
        (TYPE_POWER_MATCH, "Potrivește formele unei puteri"),
        (TYPE_POWER_TABLE, "Completează tabelul puterilor"),
        (TYPE_POWER_CYCLE, "Ciclul ultimei cifre"),
        (TYPE_POWER_SQUARE, "Reprezentarea pătratului"),
        (TYPE_POWER_RULE_CHAIN, "Lanț de reguli pentru puteri"),
        (TYPE_POWER_COMPARE, "Compară două puteri"),
        (TYPE_POWER_ORDER, "Ordonează puteri"),
        (TYPE_BASE_VALUES, "Completează scrierea într-o bază"),
        (TYPE_BASE_MATCH, "Potrivește reprezentări în baze"),
        (TYPE_BINARY_TOGGLE, "Construiește numărul binar"),
        (TYPE_BASE_ERROR, "Detectează eroarea de conversie"),
        (TYPE_UNIT_REDUCTION, "Metoda reducerii la unitate"),
        (TYPE_COMPARISON_METHOD, "Metoda comparației"),
        (TYPE_FIGURATIVE_METHOD, "Metoda figurativă"),
        (TYPE_REVERSE_METHOD, "Metoda mersului invers"),
        (TYPE_FALSE_HYPOTHESIS_METHOD, "Metoda falsei ipoteze"),
        (TYPE_OPERATION_SEQUENCE, "Construiește ordinea operațiilor"),
        (TYPE_OPERATION_WORKBENCH, "Calculează expresia pe etape"),
        (TYPE_DIVISIBILITY_VALUES, "Completează divizori și multipli"),
        (TYPE_DIVISIBILITY_SELECT, "Selectează divizori sau multipli"),
        (TYPE_DIVISIBILITY_SORT, "Sortează relații de divizibilitate"),
        (TYPE_DIVISIBILITY_ERROR, "Detectează eroarea de divizibilitate"),
        (TYPE_CRITERIA_TABLE, "Tabelul criteriilor de divizibilitate"),
        (TYPE_PRIME_WORKBENCH, "Atelierul numerelor prime"),
        (TYPE_DECIMAL_WORKBENCH, "Atelierul fracțiilor zecimale"),
        (TYPE_FRACTION_VISUAL, "Construiește și reprezintă fracții"),
        (TYPE_FRACTION_DOMINO, "Domino cu fracții echivalente"),
        (TYPE_FRACTION_COMPARE, "Compară și ordonează fracții"),
        (TYPE_FRACTION_AXIS, "Fracții pe axa numerelor"),
        (TYPE_GCD_WORKBENCH, "Atelier pentru c.m.m.d.c."),
        (TYPE_FRACTION_SCALE, "Amplifică și simplifică fracții"),
        (TYPE_FRACTION_REDUCE_PATH, "Traseu spre fracția ireductibilă"),
        (TYPE_LCM_WORKBENCH, "Atelier pentru c.m.m.m.c."),
        (TYPE_COMMON_DENOMINATOR, "Adu fracțiile la același numitor"),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    points = models.IntegerField(default=10)
    explanation = models.TextField(blank=True)
    question_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default=TYPE_MULTIPLE_CHOICE,
    )
    interactive_data = models.JSONField(default=dict, blank=True)
    format_tag = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default=FORMAT_GRID,
    )

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
