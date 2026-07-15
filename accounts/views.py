from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileEditForm, RegisterForm
from .services import get_profile_dashboard
from .utils import get_or_create_profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cont creat cu succes. Te poți conecta acum.")
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def profile_view(request):
    dashboard = get_profile_dashboard(request.user)
    return render(
        request,
        "accounts/profile.html",
        {"dashboard": dashboard},
    )


@login_required
def profile_edit_view(request):
    profile = get_or_create_profile(request.user)

    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profilul a fost actualizat.")
            return redirect("profile")
    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    return render(request, "accounts/profile_edit.html", {"form": form})
