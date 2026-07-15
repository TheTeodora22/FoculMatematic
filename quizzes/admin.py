from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import (
    AnswerOption,
    Chapter,
    GeneratedQuizSession,
    GeneratedQuizSessionQuestion,
    Question,
    Quiz,
    QuizAttempt,
    QuizAttemptAnswer,
    UserQuestionProgress,
)


class AnswerOptionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        options = [
            form.cleaned_data
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False)
        ]
        if len(options) < 2:
            raise ValidationError(
                "Fiecare întrebare trebuie să aibă minim 2 opțiuni de răspuns."
            )
        correct_count = sum(1 for opt in options if opt.get("is_correct"))
        if correct_count != 1:
            raise ValidationError(
                "Fiecare întrebare trebuie să aibă exact o opțiune corectă."
            )


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 2
    formset = AnswerOptionInlineFormSet


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "class_level", "exam_slug", "slug", "order")
    list_filter = ("class_level", "exam_slug")
    ordering = ("class_level", "order")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text_preview", "quiz", "points")
    list_filter = ("quiz",)
    inlines = [AnswerOptionInline]

    @admin.display(description="Întrebare")
    def text_preview(self, obj):
        return (obj.text[:60] + "…") if len(obj.text) > 60 else obj.text


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "chapter", "difficulty", "class_levels", "exam_slugs", "question_count")
    list_filter = ("difficulty", "chapter")
    search_fields = ("title", "source_file")

    @admin.display(description="Întrebări")
    def question_count(self, obj):
        return obj.questions.count()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.questions.count() == 0:
            messages.warning(
                request,
                f"Chestionarul „{obj.title}” nu are încă întrebări.",
            )


class QuizAttemptAnswerInline(admin.TabularInline):
    model = QuizAttemptAnswer
    extra = 0
    readonly_fields = ("question", "selected_option", "is_correct")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "max_score", "created_at")
    list_filter = ("quiz",)
    readonly_fields = ("user", "quiz", "score", "max_score", "created_at")
    inlines = [QuizAttemptAnswerInline]


@admin.register(UserQuestionProgress)
class UserQuestionProgressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "question",
        "xp_awarded",
        "training_status",
        "seen_in_generated_quiz",
    )
    list_filter = ("xp_awarded", "training_status", "seen_in_generated_quiz")


class GeneratedQuizSessionQuestionInline(admin.TabularInline):
    model = GeneratedQuizSessionQuestion
    extra = 0
    readonly_fields = ("question", "order", "selected_option", "is_correct")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(GeneratedQuizSession)
class GeneratedQuizSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "topic", "status", "current_index", "updated_at")
    list_filter = ("status",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [GeneratedQuizSessionQuestionInline]
