from django.conf import settings
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from achievements.models import UserAchievement

from .avatars import AVATAR_CHOICES, AVATAR_EMOJI
from .forms import (
    FMAuthenticationForm,
    FMRegisterForm,
    FMPasswordChangeForm,
    ProfileEditForm,
    ProfileThemeForm,
)


def _redirect_after_auth(request, next_url: str):
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect(settings.LOGIN_REDIRECT_URL)


@require_http_methods(["GET", "HEAD", "POST"])
def auth_portal_view(request, initial_tab="login"):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    next_url = (request.POST.get("next") or request.GET.get("next") or "").strip()

    login_form = FMAuthenticationForm(prefix="login")
    register_form = FMRegisterForm(prefix="reg")

    if request.method == "GET":
        active_tab = "register" if request.GET.get("tab") == "register" else initial_tab
        if active_tab not in ("login", "register"):
            active_tab = "login"
    else:
        active_tab = "login"
        action = request.POST.get("action")
        if action == "login":
            login_form = FMAuthenticationForm(
                request, data=request.POST, prefix="login"
            )
            if login_form.is_valid():
                login(request, login_form.get_user())
                return _redirect_after_auth(request, next_url)
        elif action == "register":
            register_form = FMRegisterForm(request.POST, prefix="reg")
            active_tab = "register"
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return _redirect_after_auth(request, next_url)
        else:
            active_tab = initial_tab

    return render(
        request,
        "accounts/auth_portal.html",
        {
            "login_form": login_form,
            "register_form": register_form,
            "next": next_url,
            "auth_active_tab": active_tab,
        },
    )


@login_required
def profile_view(request):
    profile = request.user.profile
    theme_form = ProfileThemeForm(instance=profile)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "theme":
            theme_form = ProfileThemeForm(request.POST, instance=profile)
            if theme_form.is_valid():
                theme_form.save()
                return redirect("profile")

    xp_meta = profile.xp_progress()
    current_avatar_emoji = AVATAR_EMOJI.get(profile.avatar, "⭐")

    recent_badges = list(
        UserAchievement.objects.filter(user=request.user)
        .select_related("achievement")
        .order_by("-unlocked_at")[:8]
    )

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
            "xp_meta": xp_meta,
            "theme_form": theme_form,
            "current_avatar_emoji": current_avatar_emoji,
            "recent_badges": recent_badges,
        },
    )


@login_required
def profile_edit_view(request):
    profile = request.user.profile
    avatar_options = [
        {"key": k, "label": lab, "emoji": AVATAR_EMOJI.get(k, "⭐")}
        for k, lab in AVATAR_CHOICES
    ]

    form = ProfileEditForm(request.user, profile)
    password_form = FMPasswordChangeForm(request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "password":
            password_form = FMPasswordChangeForm(request.user, request.POST)
            form = ProfileEditForm(request.user, profile)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect("profile_edit")
        else:
            form = ProfileEditForm(request.user, profile, request.POST)
            password_form = FMPasswordChangeForm(request.user)
            if form.is_valid():
                form.save()
                return redirect("profile")

    return render(
        request,
        "accounts/profile_edit.html",
        {
            "form": form,
            "password_form": password_form,
            "profile": profile,
            "avatar_options": avatar_options,
        },
    )
