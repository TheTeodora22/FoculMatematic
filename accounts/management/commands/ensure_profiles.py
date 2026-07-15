from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.utils import get_or_create_profile


class Command(BaseCommand):
    help = "Create Profile records for users that do not have one."

    def handle(self, *args, **options):
        created = 0
        for user in User.objects.filter(profile__isnull=True):
            get_or_create_profile(user)
            created += 1

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created {created} profile(s)."))
        else:
            self.stdout.write("All users already have profiles.")
