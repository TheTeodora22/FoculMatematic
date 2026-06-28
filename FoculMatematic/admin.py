from django import forms
from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import Textarea
from django.urls import reverse
from django.utils.html import format_html

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


class CurriculumEntryAdminMixin:
    """Setări comune pentru introducere rapidă în admin."""

    save_on_top = True
    save_as = True
    show_full_result_count = False
    list_max_show_all = 500
    search_help_text = (
        "Caută după titlu, slug, text întrebare sau lecție (unde e cazul)."
    )


class ChoiceInline(admin.TabularInline):
    model = Choice
    formset = ChoiceInlineFormSet
    extra = 4
    fields = ("text", "is_correct")
    ordering = ("pk",)
    verbose_name_plural = "Variante (exact una corectă)"


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    min_num = 0
    fields = ("order", "points", "text")
    show_change_link = True
    ordering = ("order", "pk")
    formfield_overrides = {
        models.TextField: {
            "widget": Textarea(
                attrs={
                    "rows": 3,
                    "class": "vLargeTextField",
                    "style": "width:100%;max-width:40rem;",
                }
            )
        },
    }
    verbose_name_plural = "Întrebări (salvează lecția, apoi adaugă variantele din întrebare)"


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ("title", "slug", "order")
    show_change_link = True
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "slug")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("chapter")


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    fields = ("title", "slug", "order")
    show_change_link = True
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "slug")


@admin.register(SchoolClass)
class SchoolClassAdmin(CurriculumEntryAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "order",
        "quiz_tag",
        "chapter_count",
        "view_site_link",
    )
    list_editable = ("order",)
    list_display_links = ("title",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ChapterInline]
    ordering = ("order", "slug")

    fieldsets = (
        (None, {"fields": ("title", "slug", "order", "quiz_tag")}),
    )

    @admin.display(description="Pe site")
    def view_site_link(self, obj):
        if not obj.pk:
            return "—"
        url = obj.get_absolute_url()
        return format_html('<a href="{}" target="_blank" rel="noopener">Vezi</a>', url)

    @admin.display(description="Capitole")
    def chapter_count(self, obj):
        if not obj.pk:
            return "—"
        return obj.chapters.count()


@admin.register(Chapter)
class ChapterAdmin(CurriculumEntryAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "school_class",
        "slug",
        "order",
        "lesson_count",
        "view_site_link",
    )
    list_filter = (("school_class", RelatedOnlyFieldListFilter),)
    list_editable = ("order",)
    list_display_links = ("title",)
    search_fields = ("title", "slug", "school_class__title", "school_class__slug")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("school_class",)
    inlines = [LessonInline]
    list_select_related = ("school_class",)
    ordering = ("school_class__order", "school_class__slug", "order", "slug")

    fieldsets = (
        (None, {"fields": ("school_class", "title", "slug", "order")}),
    )

    @admin.display(description="Pe site")
    def view_site_link(self, obj):
        if not obj.pk:
            return "—"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Capitole</a>',
            obj.get_absolute_url(),
        )

    @admin.display(description="Lecții")
    def lesson_count(self, obj):
        if not obj.pk:
            return "—"
        return obj.lessons.count()


@admin.register(Lesson)
class LessonAdmin(CurriculumEntryAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "chapter",
        "school_class_brief",
        "slug",
        "order",
        "question_count",
        "view_site_link",
    )
    list_filter = (
        ("chapter__school_class", RelatedOnlyFieldListFilter),
        ("chapter", RelatedOnlyFieldListFilter),
    )
    list_editable = ("order",)
    list_display_links = ("title",)
    search_fields = (
        "title",
        "slug",
        "content",
        "chapter__title",
        "chapter__slug",
        "chapter__school_class__title",
        "chapter__school_class__slug",
    )
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("chapter",)
    inlines = [QuestionInline]
    list_select_related = ("chapter", "chapter__school_class")
    ordering = (
        "chapter__school_class__order",
        "chapter__order",
        "order",
        "slug",
    )

    fieldsets = (
        (
            "Legătură",
            {"fields": ("chapter",)},
        ),
        (
            "Titlu & URL",
            {"fields": ("title", "slug", "order")},
        ),
        (
            "Conținut lecție",
            {
                "fields": ("content",),
                "description": "Text simplu; rândurile noi apar pe site ca paragrafe.",
            },
        ),
    )

    class Media:
        css = {"all": ("admin/css/curriculum_admin.css",)}

    @admin.display(description="Clasă")
    def school_class_brief(self, obj):
        if obj.pk and obj.chapter_id:
            return obj.chapter.school_class.title
        return "—"

    @admin.display(description="Pe site")
    def view_site_link(self, obj):
        if not obj.pk:
            return "—"
        url = obj.get_absolute_url()
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Lecție</a> · '
            '<a href="{}" target="_blank" rel="noopener">Quiz</a>',
            url,
            reverse("lesson_quiz", kwargs={"lesson_slug": obj.slug}),
        )

    @admin.display(description="Întrebări")
    def question_count(self, obj):
        if not obj.pk:
            return "—"
        return obj.questions.count()


@admin.register(Question)
class QuestionAdmin(CurriculumEntryAdminMixin, admin.ModelAdmin):
    list_display = (
        "text_preview",
        "lesson",
        "lesson_slug_brief",
        "points",
        "order",
        "choice_count",
        "edit_choices_hint",
    )
    list_filter = (
        ("lesson__chapter__school_class", RelatedOnlyFieldListFilter),
        ("lesson", RelatedOnlyFieldListFilter),
    )
    list_editable = ("order", "points")
    list_display_links = ("text_preview",)
    search_fields = (
        "text",
        "lesson__title",
        "lesson__slug",
        "lesson__chapter__title",
        "lesson__chapter__school_class__title",
    )
    autocomplete_fields = ("lesson",)
    inlines = [ChoiceInline]
    list_select_related = ("lesson", "lesson__chapter", "lesson__chapter__school_class")
    ordering = ("lesson__chapter__school_class__order", "lesson__order", "order", "pk")

    fieldsets = (
        (
            None,
            {
                "fields": ("lesson", "order", "points", "text"),
                "description": "După salvare, completează variantele mai jos (exact una corectă).",
            },
        ),
    )
    formfield_overrides = {
        models.TextField: {
            "widget": Textarea(
                attrs={"rows": 5, "cols": 80, "style": "width:100%;max-width:48rem;"}
            )
        },
    }

    class Media:
        css = {"all": ("admin/css/curriculum_admin.css",)}

    @admin.display(description="Slug lecție")
    def lesson_slug_brief(self, obj):
        if obj.pk and obj.lesson_id:
            return obj.lesson.slug
        return "—"

    @admin.display(description="Întrebare")
    def text_preview(self, obj):
        t = obj.text
        return (t[:70] + "…") if len(t) > 70 else t

    @admin.display(description="Var.")
    def choice_count(self, obj):
        if not obj.pk:
            return "—"
        return obj.choices.count()

    @admin.display(description="")
    def edit_choices_hint(self, obj):
        if not obj.pk:
            return "—"
        n = obj.choices.count()
        if n < 2:
            return format_html(
                '<span style="color:#c00;font-weight:600;">Adaugă variante</span>'
            )
        return ""


@admin.register(Choice)
class ChoiceAdmin(CurriculumEntryAdminMixin, admin.ModelAdmin):
    list_display = ("text_preview", "question", "lesson_brief", "is_correct")
    list_filter = (
        "is_correct",
        ("question__lesson__chapter__school_class", RelatedOnlyFieldListFilter),
        ("question__lesson", RelatedOnlyFieldListFilter),
    )
    list_editable = ("is_correct",)
    search_fields = (
        "text",
        "question__text",
        "question__lesson__title",
        "question__lesson__slug",
    )
    autocomplete_fields = ("question",)
    list_select_related = ("question", "question__lesson")
    ordering = ("question__lesson_id", "question_id", "pk")
    save_as = True

    fieldsets = (
        (None, {"fields": ("question", "text", "is_correct")}),
    )

    @admin.display(description="Variantă")
    def text_preview(self, obj):
        t = obj.text
        return (t[:50] + "…") if len(t) > 50 else t

    @admin.display(description="Lecție")
    def lesson_brief(self, obj):
        if obj.pk and obj.question_id:
            return obj.question.lesson.title
        return "—"


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ("question", "choice", "is_correct_display")
    can_delete = False

    @admin.display(description="Corect?")
    def is_correct_display(self, obj):
        if obj.pk and obj.choice_id:
            return "Da" if obj.choice.is_correct else "Nu"
        return "—"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("question", "choice")
            .order_by("question__order", "question_id")
        )

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "score", "max_score", "created_at")
    list_filter = (
        ("lesson__chapter__school_class", RelatedOnlyFieldListFilter),
        ("lesson", RelatedOnlyFieldListFilter),
    )
    search_fields = (
        "user__username",
        "user__email",
        "lesson__title",
        "lesson__slug",
    )
    readonly_fields = ("user", "lesson", "score", "max_score", "created_at")
    inlines = [AnswerInline]
    list_select_related = ("user", "lesson", "lesson__chapter")
    show_full_result_count = False
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            "answers__question",
            "answers__choice",
        )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt_brief", "question_preview", "choice", "correct")
    list_filter = (
        ("attempt__lesson__chapter__school_class", RelatedOnlyFieldListFilter),
    )
    search_fields = (
        "question__text",
        "choice__text",
        "attempt__user__username",
        "attempt__lesson__title",
        "attempt__lesson__slug",
    )
    autocomplete_fields = ("attempt", "question", "choice")
    list_select_related = ("attempt", "attempt__user", "question", "choice")
    readonly_fields = ("attempt", "question", "choice")

    @admin.display(description="Încercare")
    def attempt_brief(self, obj):
        if not obj.pk:
            return "—"
        a = obj.attempt
        return f"{a.user} · {a.lesson.title} ({a.score}/{a.max_score})"

    @admin.display(description="Întrebare")
    def question_preview(self, obj):
        if not obj.pk:
            return "—"
        t = obj.question.text
        return (t[:40] + "…") if len(t) > 40 else t

    @admin.display(description="OK", boolean=True)
    def correct(self, obj):
        if obj.pk and obj.choice_id:
            return obj.choice.is_correct
        return False

    def has_add_permission(self, request):
        return False


# Titluri admin — recunoscut la încărcarea modulului admin
admin.site.site_header = "Focul Matematic — administrare"
admin.site.site_title = "FM Admin"
admin.site.index_title = "Curriculum, chestionare și utilizatori"
