from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class BattlePassSeason(models.Model):
    name       = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date   = models.DateField()

class BattlePassTier(models.Model):
    season      = models.ForeignKey(BattlePassSeason, on_delete=models.CASCADE, related_name="tiers")
    level_req   = models.IntegerField()  # e.g. level 5, 10, 15…
    reward_name = models.CharField(max_length=100)
    reward_type = models.CharField(max_length=50, choices=[
        ("avatar", "Avatar"),
        ("theme", "Theme"),
        ("badge", "Badge"),
    ])
    reward_value = models.CharField(max_length=100)  # e.g. "pink_dragon_avatar"

class OwnedItem(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    item_key = models.CharField(max_length=100)  # e.g. "dark_theme_1"
    acquired_at = models.DateTimeField(auto_now_add=True)
