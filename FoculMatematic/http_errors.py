"""Răspunsuri HTTP prietenoase pentru erori client (4xx)."""

from __future__ import annotations

import secrets

from django.shortcuts import render


def render_bad_request(
    request,
    message: str,
    *,
    retry_url: str | None = None,
    retry_label: str = "Înapoi",
) -> object:
    """Pagină 400 stilizată (în loc de text simplu)."""
    return render(
        request,
        "errors/bad_request.html",
        {
            "error_message": message,
            "retry_url": retry_url,
            "retry_label": retry_label,
        },
        status=400,
    )


def _form_token_session_key(subject: str, subject_id: int) -> str:
    return f"fm_form_token:{subject}:{subject_id}"


def issue_quiz_form_token(request, subject: str, subject_id: int) -> str:
    """Emite token unic în sesiune pentru un formular de quiz (GET)."""
    token = secrets.token_urlsafe(32)
    request.session[_form_token_session_key(subject, subject_id)] = token
    request.session.modified = True
    return token


def verify_and_consume_quiz_form_token(
    request, subject: str, subject_id: int, posted: str
) -> bool:
    """
    Verifică token-ul din POST și îl consumă (o singură trimitere validă).
    Returnează False dacă lipsește, nu coincide sau a fost deja consumat.
    """
    key = _form_token_session_key(subject, subject_id)
    expected = request.session.get(key)
    if not expected or not posted:
        return False
    if not secrets.compare_digest(posted, expected):
        return False
    del request.session[key]
    request.session.modified = True
    return True
