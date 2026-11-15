from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.signals import ensure_dev_users


@override_settings(DEBUG=True)
class DevelopmentAccountTests(TestCase):
    def seed(self):
        call_command("seed_dev_users", stdout=StringIO())

    def test_accounts_can_log_in_on_web_and_api(self):
        self.seed()
        for username, password, is_admin in (
            ("demo", "DemoMatematic123!", False),
            ("admin", "AdminMatematic123!", True),
        ):
            with self.subTest(username=username):
                user = get_user_model().objects.get(username=username)
                self.assertEqual(user.is_staff, is_admin)
                self.assertEqual(user.is_superuser, is_admin)
                self.assertTrue(self.client.login(username=username, password=password))
                self.assertEqual(
                    self.client.get(reverse("admin:index")).status_code,
                    200 if is_admin else 302,
                )
                self.client.logout()
                response = self.client.post(
                    reverse("api_token"),
                    {"username": username, "password": password},
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("access", response.json())
                self.assertEqual(user.profile.xp, 0)

    def test_reseeding_preserves_progress_and_restores_credentials(self):
        self.seed()
        user = get_user_model().objects.get(username="demo")
        original_id = user.pk
        profile = user.profile
        profile.xp = 250
        profile.save()
        user.set_password("changed-password")
        user.save()
        self.seed()
        user.refresh_from_db()
        profile.refresh_from_db()
        self.assertEqual(user.pk, original_id)
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertEqual(profile.xp, 250)
        self.assertTrue(user.check_password("DemoMatematic123!"))

    def test_post_migrate_creates_accounts(self):
        ensure_dev_users(sender=None, using="default")
        self.assertEqual(get_user_model().objects.count(), 2)

    @override_settings(DEBUG=False)
    def test_production_does_not_create_accounts(self):
        ensure_dev_users(sender=None, using="default")
        with self.assertRaises(CommandError):
            self.seed()
        self.assertFalse(get_user_model().objects.exists())
