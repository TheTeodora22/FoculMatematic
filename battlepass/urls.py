from django.urls import path

from . import views

urlpatterns = [
    path("", views.battlepass_home, name="battlepass_home"),
    path("revendica/<int:tier_id>/", views.battlepass_claim, name="battlepass_claim"),
]
