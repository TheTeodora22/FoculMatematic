from django.contrib import admin

from .models import ErrorReport


@admin.action(description="Marchează ca rezolvat")
def mark_resolved(modeladmin, request, queryset):
    queryset.update(status=ErrorReport.STATUS_RESOLVED)


@admin.register(ErrorReport)
class ErrorReportAdmin(admin.ModelAdmin):
    list_display = ("id", "kind", "status", "short_page_url", "user", "email", "created_at")
    list_filter = ("kind", "status", "created_at")
    search_fields = ("description", "page_url", "email", "exception_type")
    readonly_fields = (
        "kind",
        "user",
        "email",
        "page_url",
        "user_agent",
        "exception_type",
        "traceback",
        "created_at",
    )
    actions = [mark_resolved]

    @admin.display(description="Pagină")
    def short_page_url(self, obj):
        if len(obj.page_url) > 60:
            return f"{obj.page_url[:57]}..."
        return obj.page_url
