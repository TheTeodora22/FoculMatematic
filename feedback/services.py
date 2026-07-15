import logging

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

from .models import ErrorReport

logger = logging.getLogger(__name__)

RATE_LIMIT_MAX = 5
RATE_LIMIT_SECONDS = 3600


def _rate_limit_key(ip: str) -> str:
    return f"feedback:rate:{ip}"


def is_rate_limited(ip: str) -> bool:
    key = _rate_limit_key(ip)
    count = cache.get(key, 0)
    return count >= RATE_LIMIT_MAX


def record_submission(ip: str) -> None:
    key = _rate_limit_key(ip)
    count = cache.get(key, 0)
    cache.set(key, count + 1, RATE_LIMIT_SECONDS)


def create_user_report(
    *,
    description: str,
    page_url: str,
    user_agent: str,
    user=None,
    email: str = "",
) -> ErrorReport:
    report = ErrorReport.objects.create(
        kind=ErrorReport.KIND_USER,
        description=description,
        page_url=page_url[:500],
        user=user if user and user.is_authenticated else None,
        email=email,
        user_agent=user_agent[:500],
    )
    notify_admin(report)
    return report


def create_server_report(
    *,
    page_url: str,
    user_agent: str,
    exception_type: str,
    traceback_text: str,
    user=None,
) -> ErrorReport:
    return ErrorReport.objects.create(
        kind=ErrorReport.KIND_SERVER,
        description=f"Excepție: {exception_type}",
        page_url=page_url[:500],
        user=user if user and user.is_authenticated else None,
        user_agent=user_agent[:500],
        exception_type=exception_type[:200],
        traceback=traceback_text,
    )


def notify_admin(report: ErrorReport) -> None:
    notify_email = getattr(settings, "FEEDBACK_NOTIFY_EMAIL", "")
    if not notify_email:
        return

    subject = f"[Focul Matematic] Raport #{report.pk} — {report.get_kind_display()}"
    body = (
        f"Tip: {report.get_kind_display()}\n"
        f"Status: {report.get_status_display()}\n"
        f"Pagină: {report.page_url}\n"
        f"Utilizator: {report.user or '—'}\n"
        f"Email: {report.email or '—'}\n\n"
        f"{report.description}\n"
    )
    if report.traceback:
        body += f"\n--- Traceback ---\n{report.traceback[:4000]}\n"

    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [notify_email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Nu am putut trimite notificarea pentru raportul #%s", report.pk)
