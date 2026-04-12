from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import FMPasswordChangeForm, ProfileThemeForm, UsernameChangeForm


def _fresh_forms(user, profile):
    return (
        UsernameChangeForm(user),
        FMPasswordChangeForm(user),
        ProfileThemeForm(instance=profile),
    )


@login_required
def profile_view(request):
    profile = request.user.profile

    username_form, password_form, theme_form = _fresh_forms(request.user, profile)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "username":
            username_form = UsernameChangeForm(request.user, request.POST)
            password_form, theme_form = (
                FMPasswordChangeForm(request.user),
                ProfileThemeForm(instance=profile),
            )
            if username_form.is_valid():
                username_form.save()
                messages.success(request, "Numele de utilizator a fost actualizat.")
                return redirect("profile")

        elif action == "password":
            password_form = FMPasswordChangeForm(request.user, request.POST)
            username_form, theme_form = (
                UsernameChangeForm(request.user),
                ProfileThemeForm(instance=profile),
            )
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Parola a fost schimbată.")
                return redirect("profile")

        elif action == "theme":
            theme_form = ProfileThemeForm(request.POST, instance=profile)
            username_form, password_form = (
                UsernameChangeForm(request.user),
                FMPasswordChangeForm(request.user),
            )
            if theme_form.is_valid():
                theme_form.save()
                messages.success(request, "Aspectul a fost salvat.")
                return redirect("profile")

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
            "username_form": username_form,
            "password_form": password_form,
            "theme_form": theme_form,
        },
    )
