from django.db.models.signals import post_save

from .models import Profile


def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
