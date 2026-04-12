from django.urls import path

from . import views

urlpatterns = [
    path("clase/", views.class_hub, name="quiz_classes"),
    path("examene/", views.exam_hub, name="quiz_exams"),
    path("categorie/<slug:tag_slug>/", views.quiz_list_by_tag, name="quiz_list_by_tag"),
    path("", views.quiz_list, name="quiz_list"),
    path("<int:pk>/", views.quiz_take, name="quiz_take"),
    path(
        "<int:pk>/rezultat/<int:attempt_id>/",
        views.quiz_result,
        name="quiz_result",
    ),
]
