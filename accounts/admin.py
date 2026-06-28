from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Profile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "clasa", "xp", "level", "avatar", "theme")
    list_filter = ("clasa", "theme")
    search_fields = ("user__username",)
