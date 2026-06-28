from django.conf import settings
from django.db import models

# Create your models here.
class BattlePassSeason(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name

class BattlePassTier(models.Model):
    season = models.ForeignKey(
        BattlePassSeason,
        on_delete=models.CASCADE,
        related_name="tiers",
    )
    level_req = models.IntegerField()
    reward_name = models.CharField(max_length=100)
    reward_type = models.CharField(
        max_length=50,
        choices=[
            ("avatar", "Avatar"),
            ("theme", "Theme"),
            ("badge", "Badge"),
        ],
    )
    reward_value = models.CharField(
        max_length=100,
        help_text="Cheie tehnică (ex. id avatar) sau descriere scurtă.",
    )

    class Meta:
        ordering = ["season_id", "level_req", "pk"]

    def __str__(self):
        return f"{self.season.name} · niv.{self.level_req} — {self.reward_name}"


class OwnedItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="items",
    )
    item_key = models.CharField(max_length=100)
    acquired_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "item_key"],
                name="battlepass_owneditem_unique_user_item_key",
            ),
        ]

    def __str__(self):
        return f"{self.user_id} · {self.item_key}"
