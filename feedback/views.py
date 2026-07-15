from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ErrorReportForm
from .services import create_user_report, is_rate_limited, record_submission


def _client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _default_page_url(request) -> str:
    from_param = request.GET.get("from", "").strip()
    if from_param.startswith("/"):
        return from_param[:500]
    referer = request.META.get("HTTP_REFERER", "")
    if referer:
        return referer[:500]
    return request.build_absolute_uri(request.path)


def report_error(request):
    require_email = not request.user.is_authenticated
    initial = {"page_url": _default_page_url(request)}

    if request.method == "POST":
        if is_rate_limited(_client_ip(request)):
            messages.error(
                request,
                "Ai trimis prea multe raportări. Încearcă din nou peste o oră.",
            )
            return redirect("report_error")

        form = ErrorReportForm(
            request.POST,
            require_email=require_email,
        )
        if form.is_valid():
            report = create_user_report(
                description=form.cleaned_data["description"],
                page_url=form.cleaned_data.get("page_url") or _default_page_url(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                user=request.user,
                email=form.cleaned_data.get("email", ""),
            )
            record_submission(_client_ip(request))
            messages.success(
                request,
                f"Mulțumim! Raportul #{report.pk} a fost înregistrat.",
            )
            return redirect(reverse("report_error") + "?sent=1")
    else:
        form = ErrorReportForm(initial=initial, require_email=require_email)

    return render(
        request,
        "feedback/report.html",
        {
            "form": form,
            "sent": request.GET.get("sent") == "1",
        },
    )
