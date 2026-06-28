from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("clase/", views.school_class_list, name="school_class_list"),
    path("clase/<slug:slug>/", views.school_class_detail, name="school_class_detail"),
    path("clase/<slug:slug>/capitole/", views.school_class_chapters, name="school_class_chapters"),
    path("resurse/lectii/", views.lesson_catalog, name="lesson_catalog"),
    path("lectii/<slug:lesson_slug>/", views.lesson_detail, name="lesson_detail"),
    path("lectii/<slug:lesson_slug>/quiz/", views.lesson_quiz, name="lesson_quiz"),
    path(
        "lectii/<slug:lesson_slug>/rezultate/<int:attempt_id>/",
        views.lesson_quiz_results,
        name="lesson_quiz_results",
    ),
    path("progres/", views.user_progress, name="user_progress"),
]
