from .models import Profile


def theme_preference(request):
    pref = "system"
    if request.user.is_authenticated:
        try:
            pref = request.user.profile.theme or "system"
        except Profile.DoesNotExist:
            pref = "system"
    return {"theme_pref": pref}
