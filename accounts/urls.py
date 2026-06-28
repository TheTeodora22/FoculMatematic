from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.auth_portal_view, {"initial_tab": "login"}, name="login"),
    path(
        "inregistrare/",
        views.auth_portal_view,
        {"initial_tab": "register"},
        name="register",
    ),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
]
