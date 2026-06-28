from django.contrib import admin

from .models import Achievement, UserAchievement


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "trigger", "threshold", "sort_order", "icon")
    list_filter = ("trigger",)
    list_editable = ("sort_order",)
    search_fields = ("title", "slug", "description")
    ordering = ("sort_order", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ("user", "achievement", "unlocked_at")
    list_filter = ("achievement",)
    search_fields = ("user__username", "achievement__title")
    readonly_fields = ("unlocked_at",)
    autocomplete_fields = ("achievement",)
    raw_id_fields = ("user",)
