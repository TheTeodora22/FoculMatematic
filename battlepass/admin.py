from django.contrib import admin

from .models import BattlePassSeason, BattlePassTier, OwnedItem


class BattlePassTierInline(admin.TabularInline):
    model = BattlePassTier
    extra = 1


@admin.register(BattlePassSeason)
class BattlePassSeasonAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active_display")
    list_filter = ("start_date", "end_date")
    inlines = [BattlePassTierInline]

    @admin.display(boolean=True, description="Activ")
    def is_active_display(self, obj):
        return obj.is_active


@admin.register(BattlePassTier)
class BattlePassTierAdmin(admin.ModelAdmin):
    list_display = ("season", "level_req", "reward_name", "reward_type")
    list_filter = ("season", "reward_type")


@admin.register(OwnedItem)
class OwnedItemAdmin(admin.ModelAdmin):
    list_display = ("user", "item_key", "acquired_at")
    list_filter = ("item_key",)
    search_fields = ("user__username", "item_key")
