from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
    user  = models.OneToOneField(User, on_delete=models.CASCADE)
    xp    = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    CLASS_LEVELS = tuple(range(5, 13))
    clasa = models.IntegerField(default=5, choices=[(n, f"Clasa a {n}-a") for n in CLASS_LEVELS])
    avatar = models.CharField(max_length=100, default="default_avatar")
    theme  = models.CharField(max_length=50, default="light")

    def __str__(self):
        return self.user.username
