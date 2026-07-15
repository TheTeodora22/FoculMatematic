from django.conf import settings

from .models import PageView
from .services import EXCLUDED_PREFIXES, log_page_view


class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if getattr(settings, "ANALYTICS_ENABLED", True) and self._should_log(request, response):
            session = getattr(request, "session", None)
            if not session:
                return response
            if not session.session_key:
                session.save()
            session_key = session.session_key or ""
            if not session_key:
                return response
            log_page_view(
                path=request.path,
                session_key=session_key,
                user=getattr(request, "user", None),
            )
        return response

    def _should_log(self, request, response) -> bool:
        if request.method != "GET":
            return False
        if response.status_code >= 400:
            return False

        path = request.path
        if path in ("/favicon.ico", "/robots.txt"):
            return False
        if any(path.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            return False

        user = getattr(request, "user", None)
        if (
            getattr(settings, "ANALYTICS_EXCLUDE_STAFF", True)
            and user
            and user.is_authenticated
            and user.is_staff
        ):
            return False

        return True
