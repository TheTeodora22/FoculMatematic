from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import (
    Answer,
    Chapter,
    Choice,
    Lesson,
    Question,
    QuizAttempt,
    SchoolClass,
)


class ChoiceInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(getattr(f, "errors", None) for f in self.forms):
            return
        active = []
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            data = form.cleaned_data
            if data.get("DELETE"):
                continue
            if not data:
                continue
            active.append(data)
        if not active:
            return
        correct = sum(1 for d in active if d.get("is_correct"))
        if correct != 1:
            raise ValidationError(
                "Fiecare întrebare trebuie să aibă exact o variantă marcată ca corectă."
            )


class ChoiceInline(admin.TabularInline):
    model = Choice
    formset = ChoiceInlineFormSet
    extra = 2


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ("text", "points", "order")
    show_change_link = True


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("title", "slug", "order")
    show_change_link = True
    prepopulated_fields = {"slug": ("title",)}


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    fields = ("title", "slug", "order")
    show_change_link = True
    prepopulated_fields = {"slug": ("title",)}


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order", "chapter_count")
    list_editable = ("order",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ChapterInline]

    @admin.display(description="Capitole")
    def chapter_count(self, obj):
        if not obj.pk:
            return "—"
        return obj.chapters.count()


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "school_class", "slug", "order", "lesson_count")
    list_filter = ("school_class",)
    list_editable = ("order",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("school_class",)
    inlines = [LessonInline]

    @admin.display(description="Lecții")
    def lesson_count(self, obj):
        if not obj.pk:
            return "—"
        return obj.lessons.count()


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "chapter", "slug", "order", "question_count")
    list_filter = ("chapter__school_class", "chapter")
    list_editable = ("order",)
    search_fields = ("title", "slug", "content")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("chapter",)
    inlines = [QuestionInline]

    @admin.display(description="Întrebări")
    def question_count(self, obj):
        if not obj.pk:
            return "—"
        return obj.questions.count()


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ("question", "choice")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text_preview", "lesson", "points", "order", "choice_count")
    list_filter = ("lesson__chapter__school_class", "lesson")
    list_editable = ("order", "points")
    search_fields = ("text",)
    autocomplete_fields = ("lesson",)
    inlines = [ChoiceInline]

    @admin.display(description="Întrebare")
    def text_preview(self, obj):
        t = obj.text
        return (t[:70] + "…") if len(t) > 70 else t

    @admin.display(description="Variante")
    def choice_count(self, obj):
        if not obj.pk:
            return "—"
        return obj.choices.count()


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "score", "max_score", "created_at")
    list_filter = ("lesson__chapter__school_class",)
    search_fields = ("user__username", "lesson__title", "lesson__slug")
    readonly_fields = ("user", "lesson", "score", "max_score", "created_at")
    inlines = [AnswerInline]

    def has_add_permission(self, request):
        return False


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "choice")
    list_select_related = ("attempt", "question", "choice")
