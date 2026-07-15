from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import get_or_create_profile


@receiver(post_save, sender=User)
def ensure_profile(sender, instance, **kwargs):
    get_or_create_profile(instance)
