from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, transaction

from accounts.models import Profile


class Command(BaseCommand):
    help = "Create reusable demo and superuser accounts for local development."

    def add_arguments(self, parser):
        parser.add_argument("--database", default=DEFAULT_DB_ALIAS)

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Development accounts require DEBUG=True.")

        database = options["database"]
        users = get_user_model().objects.db_manager(database)
        with transaction.atomic(using=database):
            for username, password, is_admin in (
                ("demo", "DemoMatematic123!", False),
                ("admin", "AdminMatematic123!", True),
            ):
                user, _ = users.get_or_create(username=username)
                user.is_active = True
                user.is_staff = is_admin
                user.is_superuser = is_admin
                if not user.check_password(password):
                    user.set_password(password)
                user.save(using=database)
                Profile.objects.using(database).get_or_create(user=user)

        self.stdout.write(self.style.SUCCESS("Development accounts ready: demo, admin."))
