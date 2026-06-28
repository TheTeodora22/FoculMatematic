from datetime import date

from achievements.services import flash_new_achievements
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import BattlePassSeason, BattlePassTier, OwnedItem


def _active_season():
    today = date.today()
    return (
        BattlePassSeason.objects.filter(start_date__lte=today, end_date__gte=today)
        .order_by("-start_date")
        .first()
    )


def claim_item_key(tier):
    return f"battlepass_tier_{tier.pk}"


def battlepass_home(request):
    season = _active_season()
    tiers = []
    user_level = None
    claimed_keys = set()
    if request.user.is_authenticated:
        user_level = request.user.profile.level
        claimed_keys = set(
            OwnedItem.objects.filter(user=request.user).values_list(
                "item_key", flat=True
            )
        )
    tier_cards = []
    if season:
        for t in season.tiers.order_by("level_req", "pk"):
            key = claim_item_key(t)
            tier_cards.append(
                {
                    "tier": t,
                    "claim_key": key,
                    "unlocked": user_level is not None and user_level >= t.level_req,
                    "claimed": key in claimed_keys,
                }
            )
    return render(
        request,
        "battlepass/home.html",
        {
            "season": season,
            "tier_cards": tier_cards,
            "user_level": user_level,
        },
    )


@login_required
@require_POST
def battlepass_claim(request, tier_id):
    tier = get_object_or_404(
        BattlePassTier.objects.select_related("season"),
        pk=tier_id,
    )
    season = tier.season
    today = date.today()
    if not (season.start_date <= today <= season.end_date):
        messages.error(request, "Sezonul nu este activ.")
        return redirect("battlepass_home")
    if request.user.profile.level < tier.level_req:
        messages.error(
            request,
            f"Ai nevoie de nivelul {tier.level_req} pentru această recompensă (ai nivelul {request.user.profile.level}).",
        )
        return redirect("battlepass_home")
    key = claim_item_key(tier)
    if OwnedItem.objects.filter(user=request.user, item_key=key).exists():
        messages.info(request, "Ai revendicat deja această recompensă.")
        return redirect("battlepass_home")
    try:
        with transaction.atomic():
            OwnedItem.objects.create(user=request.user, item_key=key)
    except IntegrityError:
        messages.info(request, "Această recompensă a fost deja revendicată.")
        return redirect("battlepass_home")
    messages.success(
        request,
        f"Recompensă deblocată: {tier.reward_name}",
    )
    flash_new_achievements(request, request.user)
    return redirect("battlepass_home")
