from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class BattlePassSeason(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

    @property
    def is_active(self) -> bool:
        today = timezone.localdate()
        return self.start_date <= today <= self.end_date


class BattlePassTier(models.Model):
    season = models.ForeignKey(
        BattlePassSeason, on_delete=models.CASCADE, related_name="tiers"
    )
    level_req = models.IntegerField()
    reward_name = models.CharField(max_length=100)
    reward_type = models.CharField(
        max_length=50,
        choices=[
            ("avatar", "Avatar"),
            ("theme", "Temă"),
            ("badge", "Insignă"),
        ],
    )
    reward_value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.season.name} — Nivel {self.level_req}: {self.reward_name}"


class OwnedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    item_key = models.CharField(max_length=100)
    acquired_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "item_key")]

    def __str__(self):
        return f"{self.user.username}: {self.item_key}"
