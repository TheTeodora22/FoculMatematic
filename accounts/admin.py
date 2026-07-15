from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "clasa", "level", "xp", "avatar", "theme")
    list_filter = ("clasa", "level")
    search_fields = ("user__username",)
