from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .services import get_active_stats, get_daily_active_users, get_top_pages


@staff_member_required
def dashboard(request):
    period = request.GET.get("period", "7")
    try:
        days = max(1, min(int(period), 90))
    except (TypeError, ValueError):
        days = 7

    today_stats = get_active_stats(days=1)
    period_stats = get_active_stats(days=days)

    return render(
        request,
        "analytics/dashboard.html",
        {
            "days": days,
            "today": today_stats,
            "period": period_stats,
            "top_pages": get_top_pages(days=days),
            "daily": get_daily_active_users(days=min(days, 14)),
        },
    )
