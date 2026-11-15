import secrets

from django import forms
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .math_tools.quadratics import check_roots, equation_latex, generate_quadratic

SESSION_KEY = "math_demo_quadratic"


class RootsForm(forms.Form):
    exercise_id = forms.CharField(max_length=32, widget=forms.HiddenInput)
    first = forms.IntegerField(label="Prima soluție", min_value=-100, max_value=100)
    second = forms.IntegerField(label="A doua soluție", min_value=-100, max_value=100)


@never_cache
@require_http_methods(["GET", "POST"])
def math_demo(request):
    exercise = request.session.get(SESSION_KEY)
    if request.method == "POST" and request.POST.get("action") == "new":
        request.session.pop(SESSION_KEY, None)
        return redirect("math_demo")
    if exercise is None:
        exercise = {"id": secrets.token_hex(16), "coefficients": generate_quadratic()}
        request.session[SESSION_KEY] = exercise
    form = RootsForm(request.POST if request.method == "POST" else None,
                     initial={"exercise_id": exercise["id"]})
    feedback = None
    if request.method == "POST" and form.is_valid():
        if form.cleaned_data["exercise_id"] != exercise["id"]:
            form.add_error(None, "Exercițiul s-a schimbat. Reîncarcă pagina și încearcă din nou.")
        elif check_roots(exercise["coefficients"], form.cleaned_data["first"], form.cleaned_data["second"]):
            feedback = "Corect! Ai găsit ambele soluții."
        else:
            feedback = "Răspuns incorect. Verifică ambele soluții și încearcă din nou."
    return render(request, "math_demo.html", {
        "form": form, "feedback": feedback,
        "equation": equation_latex(exercise["coefficients"]),
    })
