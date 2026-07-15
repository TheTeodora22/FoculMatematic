from django.urls import NoReverseMatch, reverse

FEEDBACK_REPORT_PATH = "/feedback/raporteaza/"


def feedback_report_url(from_path: str = "") -> str:
    try:
        url = reverse("report_error")
    except NoReverseMatch:
        url = FEEDBACK_REPORT_PATH
    if from_path:
        return f"{url}?from={from_path}"
    return url


def feedback_urls(request):
    return {
        "feedback_report_url": feedback_report_url(),
    }
