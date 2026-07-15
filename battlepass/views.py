from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import get_battlepass_progress


@login_required
def battlepass_view(request):
    progress = get_battlepass_progress(request.user)
    return render(request, "battlepass/index.html", progress)
