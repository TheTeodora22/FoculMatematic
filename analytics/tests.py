from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from analytics.models import PageView
from analytics.services import get_active_stats, get_top_pages, log_page_view


class PageViewMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()
        PageView.objects.all().delete()

    def test_logs_successful_page_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PageView.objects.count(), 1)
        view = PageView.objects.get()
        self.assertEqual(view.path, "/")

    def test_skips_static_and_admin(self):
        self.client.get("/static/core/css/fm-app.css")
        self.client.get("/admin/")
        self.assertEqual(PageView.objects.count(), 0)

    def test_logs_authenticated_user(self):
        user = User.objects.create_user(username="analyticsuser", password="testpass123")
        self.client.login(username="analyticsuser", password="testpass123")
        self.client.get(reverse("index"))
        view = PageView.objects.get()
        self.assertEqual(view.user, user)

    @override_settings(ANALYTICS_EXCLUDE_STAFF=True)
    def test_skips_staff_users(self):
        User.objects.create_superuser(
            username="staff",
            email="staff@example.com",
            password="testpass123",
        )
        self.client.login(username="staff", password="testpass123")
        self.client.get(reverse("index"))
        self.assertEqual(PageView.objects.count(), 0)

    @override_settings(ANALYTICS_ENABLED=False)
    def test_disabled_via_setting(self):
        self.client.get(reverse("index"))
        self.assertEqual(PageView.objects.count(), 0)


class AnalyticsServicesTests(TestCase):
    def test_top_pages_and_active_stats(self):
        user = User.objects.create_user(username="statuser", password="x")
        log_page_view(path="/", session_key="abc", user=user)
        log_page_view(path="/", session_key="abc", user=user)
        log_page_view(path="/quizzes/", session_key="def", user=None)

        stats = get_active_stats(days=7)
        self.assertEqual(stats["views"], 3)
        self.assertEqual(stats["unique_sessions"], 2)
        self.assertEqual(stats["logged_in_users"], 1)

        top = get_top_pages(days=7)
        self.assertEqual(top[0]["path"], "/")
        self.assertEqual(top[0]["views"], 2)


class AnalyticsDashboardTests(TestCase):
    def test_dashboard_requires_staff(self):
        response = self.client.get(reverse("analytics_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_view_dashboard(self):
        User.objects.create_superuser(
            username="adminview",
            email="a@example.com",
            password="testpass123",
        )
        self.client.login(username="adminview", password="testpass123")
        response = self.client.get(reverse("analytics_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Analitice")
        self.assertContains(response, "Pagini cele mai accesate")
