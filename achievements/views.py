from django.shortcuts import render

from .models import Achievement, UserAchievement
from .services import progress_hint, sync_achievements


def achievement_list(request):
    if request.user.is_authenticated:
        sync_achievements(request.user)

    achievements = list(Achievement.objects.order_by("sort_order", "slug"))
    unlocked_ids = set()
    unlocked_at = {}
    if request.user.is_authenticated:
        for ua in UserAchievement.objects.filter(user=request.user).select_related(
            "achievement"
        ):
            unlocked_ids.add(ua.achievement_id)
            unlocked_at[ua.achievement_id] = ua.unlocked_at

    rows = []
    for ach in achievements:
        is_unlocked = ach.id in unlocked_ids
        hint = None
        if request.user.is_authenticated and not is_unlocked:
            hint = progress_hint(request.user, ach)
        rows.append(
            {
                "achievement": ach,
                "unlocked": is_unlocked,
                "unlocked_at": unlocked_at.get(ach.id),
                "progress": hint,
            }
        )

    total = len(achievements)
    done = len(unlocked_ids) if request.user.is_authenticated else 0

    return render(
        request,
        "achievements/list.html",
        {
            "rows": rows,
            "total_count": total,
            "unlocked_count": done,
        },
    )
