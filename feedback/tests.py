from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from feedback.middleware import ErrorCaptureMiddleware
from feedback.models import ErrorReport
from feedback.services import create_user_report, is_rate_limited, record_submission


class ErrorReportFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_guest_can_submit_with_email(self):
        response = self.client.post(
            reverse("report_error"),
            {
                "description": "Butonul de antrenare nu răspunde după submit.",
                "email": "guest@example.com",
                "page_url": "/quizzes/subiect/1/",
            },
        )
        self.assertEqual(response.status_code, 302)
        report = ErrorReport.objects.get()
        self.assertEqual(report.kind, ErrorReport.KIND_USER)
        self.assertEqual(report.email, "guest@example.com")
        self.assertIsNone(report.user_id)

    def test_guest_requires_email(self):
        response = self.client.post(
            reverse("report_error"),
            {
                "description": "Descriere suficient de lungă pentru validare.",
                "email": "",
                "page_url": "/",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adaugă un email")
        self.assertEqual(ErrorReport.objects.count(), 0)

    def test_logged_in_user_report(self):
        user = User.objects.create_user(username="reporter", password="testpass123")
        self.client.login(username="reporter", password="testpass123")
        response = self.client.post(
            reverse("report_error"),
            {
                "description": "Pagina de profil nu se încarcă corect la scroll.",
                "email": "",
                "page_url": "/accounts/profile/",
            },
        )
        self.assertEqual(response.status_code, 302)
        report = ErrorReport.objects.get()
        self.assertEqual(report.user, user)
        self.assertEqual(report.email, "")

    def test_rate_limit_blocks_spam(self):
        ip = "203.0.113.10"
        for _ in range(5):
            record_submission(ip)
        self.assertTrue(is_rate_limited(ip))

        response = self.client.post(
            reverse("report_error"),
            {
                "description": "Încă un raport de test pentru rate limit.",
                "email": "spam@example.com",
                "page_url": "/",
            },
            REMOTE_ADDR=ip,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ErrorReport.objects.count(), 0)

    @override_settings(FEEDBACK_NOTIFY_EMAIL="admin@example.com")
    def test_notify_email_sent(self):
        create_user_report(
            description="Test notificare email admin.",
            page_url="/test/",
            user_agent="pytest",
            email="user@example.com",
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Raport #", mail.outbox[0].subject)


class ErrorCaptureMiddlewareTests(TestCase):
    def setUp(self):
        self.middleware = ErrorCaptureMiddleware(lambda request: None)

    def test_middleware_creates_server_report(self):
        request = Client().get("/").wsgi_request
        request.user = User.objects.create_user(username="mwuser", password="x")
        try:
            raise ValueError("test failure")
        except ValueError as exc:
            self.middleware.process_exception(request, exc)

        report = ErrorReport.objects.get()
        self.assertEqual(report.kind, ErrorReport.KIND_SERVER)
        self.assertEqual(report.exception_type, "ValueError")
        self.assertIn("test failure", report.traceback)
        self.assertEqual(request._error_report_id, report.pk)


@override_settings(DEBUG=False)
class ErrorHandlerTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_custom_404_page(self):
        response = self.client.get("/pagina-inexistenta-test/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Pagina nu a fost găsită", status_code=404)
        self.assertContains(response, "Raportează problema", status_code=404)

    def test_handler500_shows_report_reference(self):
        from django.test import RequestFactory

        from feedback.handlers import handler500

        request = RequestFactory().get("/test/")
        request._error_report_id = 42
        response = handler500(request)
        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "Referință raport:", status_code=500)
        self.assertContains(response, "#42", status_code=500)
