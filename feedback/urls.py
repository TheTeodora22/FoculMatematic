from django.urls import path

from . import views

urlpatterns = [
    path("raporteaza/", views.report_error, name="report_error"),
]
