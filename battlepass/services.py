from datetime import date

from django.utils import timezone

from accounts.utils import get_or_create_profile

from .models import BattlePassSeason, BattlePassTier, OwnedItem


def get_active_season():
    today = timezone.localdate()
    return (
        BattlePassSeason.objects.filter(start_date__lte=today, end_date__gte=today)
        .order_by("-start_date")
        .first()
    )


def grant_tier_rewards(user, new_level: int) -> list[str]:
    """Acordă itemele de battle pass pentru nivelul atins. Returnează numele recompenselor noi."""
    season = get_active_season()
    if season is None:
        return []

    tiers = BattlePassTier.objects.filter(
        season=season, level_req__lte=new_level
    ).order_by("level_req")
    owned_keys = set(user.items.values_list("item_key", flat=True))
    new_rewards = []

    for tier in tiers:
        if tier.reward_value in owned_keys:
            continue
        OwnedItem.objects.create(user=user, item_key=tier.reward_value)
        owned_keys.add(tier.reward_value)
        new_rewards.append(tier.reward_name)

    return new_rewards


def get_battlepass_progress(user):
    season = get_active_season()
    profile = get_or_create_profile(user)
    owned_keys = set(user.items.values_list("item_key", flat=True))

    if season is None:
        return {
            "season": None,
            "profile": profile,
            "tiers": [],
        }

    tiers = []
    for tier in season.tiers.order_by("level_req"):
        tiers.append(
            {
                "tier": tier,
                "unlocked": profile.level >= tier.level_req,
                "owned": tier.reward_value in owned_keys,
            }
        )

    return {
        "season": season,
        "profile": profile,
        "tiers": tiers,
    }
