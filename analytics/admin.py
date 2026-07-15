from django.contrib import admin

from .models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("created_at", "path", "user", "session_key")
    list_filter = ("created_at",)
    search_fields = ("path", "session_key", "user__username")
    readonly_fields = ("path", "user", "session_key", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
