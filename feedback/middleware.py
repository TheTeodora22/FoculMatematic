import traceback

from django.core.exceptions import PermissionDenied
from django.http import Http404

from .models import ErrorReport
from .services import create_server_report, notify_admin


class ErrorCaptureMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, (Http404, PermissionDenied)):
            return None

        report = create_server_report(
            page_url=request.build_absolute_uri(),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            exception_type=type(exception).__name__,
            traceback_text=traceback.format_exc(),
            user=getattr(request, "user", None),
        )
        request._error_report_id = report.pk
        notify_admin(report)
        return None
