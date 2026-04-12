from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
    user  = models.OneToOneField(User, on_delete=models.CASCADE)
    xp    = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    clasa = models.IntegerField(default=1)
    avatar = models.CharField(max_length=100, default="default_avatar")
    theme = models.CharField(
        max_length=20,
        default="system",
        choices=[
            ("light", "Luminos"),
            ("dark", "Întunecat"),
            ("system", "La fel ca sistemul"),
        ],
    )

    def __str__(self):
        return self.user.username