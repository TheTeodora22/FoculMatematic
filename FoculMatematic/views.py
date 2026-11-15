from django.shortcuts import render
from accounts.models import Profile


def index(request):
    return render(request, "index.html", {"class_levels": Profile.CLASS_LEVELS})

