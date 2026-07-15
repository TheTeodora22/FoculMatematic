from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import PageView

EXCLUDED_PREFIXES = ("/static/", "/admin/", "/api/")


def log_page_view(*, path: str, session_key: str, user=None) -> PageView:
    return PageView.objects.create(
        path=path[:500],
        session_key=session_key[:40],
        user=user if user and user.is_authenticated else None,
    )


def _since(days: int):
    return timezone.now() - timedelta(days=days)


def get_top_pages(*, days: int = 7, limit: int = 15):
    return list(
        PageView.objects.filter(created_at__gte=_since(days))
        .values("path")
        .annotate(
            views=Count("id"),
            unique_sessions=Count("session_key", distinct=True),
        )
        .order_by("-views")[:limit]
    )


def get_active_stats(*, days: int = 7):
    since = _since(days)
    qs = PageView.objects.filter(created_at__gte=since)
    return {
        "views": qs.count(),
        "unique_sessions": qs.values("session_key").distinct().count(),
        "logged_in_users": qs.filter(user__isnull=False)
        .values("user")
        .distinct()
        .count(),
    }


def get_daily_active_users(days: int = 14):
    since = _since(days)
    rows = (
        PageView.objects.filter(created_at__gte=since)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(
            sessions=Count("session_key", distinct=True),
            users=Count("user", distinct=True),
        )
        .order_by("day")
    )
    return list(rows)
