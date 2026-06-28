from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .avatars import AVATAR_CHOICES, DEFAULT_AVATAR
from .leveling import compute_level_number, get_level_progress


class User(AbstractUser):
    """
    E-mail unic la nivel de bază de date când este setat (NULL pentru cont fără e-mail).
    Username rămâne unic ca la Django standard; formularul de profil verifică și
    variații de majuscule (iexact).
    """

    email = models.EmailField(
        _("email address"),
        blank=True,
        null=True,
        unique=True,
    )


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    clasa = models.IntegerField(default=1)
    avatar = models.CharField(
        max_length=32,
        choices=AVATAR_CHOICES,
        default=DEFAULT_AVATAR,
        help_text="Avatar afișat în profil și în joc.",
    )
    theme = models.CharField(
        max_length=20,
        default="system",
        choices=[
            ("light", "Luminos"),
            ("dark", "Întunecat"),
            ("system", "La fel ca sistemul"),
        ],
    )

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profile"

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.level = compute_level_number(self.xp)
        super().save(*args, **kwargs)

    def xp_progress(self):
        """Date pentru UI (bară XP, titlu nivel)."""
        return get_level_progress(self.xp)
