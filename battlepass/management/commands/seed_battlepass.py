from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from battlepass.models import BattlePassSeason, BattlePassTier


class Command(BaseCommand):
    help = "Creează un sezon demo de battle pass cu recompense."

    def handle(self, *args, **options):
        today = timezone.localdate()
        season, created = BattlePassSeason.objects.get_or_create(
            name="Sezonul 1 — Focul Matematic",
            defaults={
                "start_date": today - timedelta(days=30),
                "end_date": today + timedelta(days=90),
            },
        )

        tiers_data = [
            (2, "Avatar Dragon", "avatar", "dragon_avatar"),
            (3, "Temă Întunecată", "theme", "dark_theme_1"),
            (5, "Insignă Matematician", "badge", "math_badge_1"),
            (7, "Avatar Phoenix", "avatar", "phoenix_avatar"),
            (10, "Temă Foc", "theme", "fire_theme"),
        ]

        for level_req, reward_name, reward_type, reward_value in tiers_data:
            BattlePassTier.objects.get_or_create(
                season=season,
                level_req=level_req,
                defaults={
                    "reward_name": reward_name,
                    "reward_type": reward_type,
                    "reward_value": reward_value,
                },
            )

        action = "creat" if created else "actualizat"
        self.stdout.write(
            self.style.SUCCESS(
                f"Sezon battle pass {action}: {season.name} ({season.tiers.count()} tier-uri)"
            )
        )
