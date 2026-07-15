from django.shortcuts import render

from feedback.context_processors import feedback_report_url


def handler404(request, exception):
    return render(
        request,
        "404.html",
        {
            "report_url": feedback_report_url(request.path),
        },
        status=404,
    )


def handler500(request):
    report_id = getattr(request, "_error_report_id", None)
    return render(
        request,
        "500.html",
        {
            "report_id": report_id,
            "report_url": feedback_report_url(request.path),
        },
        status=500,
    )
