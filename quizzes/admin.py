from django.contrib import admin

from .models import AnswerOption, Question, Quiz, QuizAttempt, QuizQuestion, QuizTag


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 2


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    fk_name = "quiz"
    extra = 1
    autocomplete_fields = ("question",)
    ordering = ("order", "pk")


class QuestionQuizLinkInline(admin.TabularInline):
    """În ce chestionare apare această întrebare."""

    model = QuizQuestion
    fk_name = "question"
    extra = 1
    autocomplete_fields = ("quiz",)
    ordering = ("quiz", "order", "pk")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text_preview", "points", "quiz_count")
    search_fields = ("text",)
    inlines = [AnswerOptionInline, QuestionQuizLinkInline]

    @admin.display(description="Întrebare")
    def text_preview(self, obj):
        return (obj.text[:60] + "…") if len(obj.text) > 60 else obj.text

    @admin.display(description="Nr. chestionare")
    def quiz_count(self, obj):
        return obj.quiz_links.count()


@admin.register(QuizTag)
class QuizTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "kind", "sort_order")
    list_filter = ("kind",)
    search_fields = ("name", "slug")
    ordering = ("sort_order", "slug")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "difficulty", "question_count", "tag_list")
    list_filter = ("difficulty", "tags")
    filter_horizontal = ("tags",)
    inlines = [QuizQuestionInline]
    search_fields = ("title",)

    @admin.display(description="Tag-uri")
    def tag_list(self, obj):
        if not obj.pk:
            return "—"
        return ", ".join(t.name for t in obj.tags.all()[:8])

    @admin.display(description="Întrebări")
    def question_count(self, obj):
        return obj.question_links.count()


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "max_score", "created_at")
    list_filter = ("quiz",)
    readonly_fields = ("user", "quiz", "score", "max_score", "created_at")


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "question", "order")
    list_filter = ("quiz",)
    ordering = ("quiz", "order", "pk")
