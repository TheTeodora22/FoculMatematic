from django.contrib import admin

from .models import BattlePassSeason, BattlePassTier, OwnedItem


class BattlePassTierInline(admin.TabularInline):
    model = BattlePassTier
    extra = 1
    ordering = ("level_req", "pk")


@admin.register(BattlePassSeason)
class BattlePassSeasonAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "tier_count")
    inlines = [BattlePassTierInline]

    @admin.display(description="Niveluri")
    def tier_count(self, obj):
        if not obj.pk:
            return "—"
        return obj.tiers.count()


@admin.register(BattlePassTier)
class BattlePassTierAdmin(admin.ModelAdmin):
    list_display = ("season", "level_req", "reward_name", "reward_type")
    list_filter = ("season", "reward_type")
    ordering = ("season", "level_req")


@admin.register(OwnedItem)
class OwnedItemAdmin(admin.ModelAdmin):
    list_display = ("user", "item_key", "acquired_at")
    search_fields = ("user__username", "item_key")
