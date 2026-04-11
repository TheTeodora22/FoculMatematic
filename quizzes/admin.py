from django.contrib import admin

from .models import AnswerOption, Question, Quiz, QuizAttempt


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 2


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
    list_display = ("title", "difficulty")
    list_filter = ("difficulty",)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "max_score", "created_at")
    list_filter = ("quiz",)
    readonly_fields = ("user", "quiz", "score", "max_score", "created_at")
