from django.urls import path

from . import views

urlpatterns = [
    path("", views.quiz_list, name="quiz_list"),
    path("<int:pk>/", views.quiz_take, name="quiz_take"),
    path(
        "<int:pk>/rezultat/<int:attempt_id>/",
        views.quiz_result,
        name="quiz_result",
    ),
]
