from django.urls import path

from . import views

urlpatterns = [
    path("", views.quiz_list, name="quiz_list"),
    path("clasa/<int:class_level>/", views.class_chapters, name="class_chapters"),
    path("examene/<slug:slug>/", views.exam_detail, name="exam_detail"),
    path(
        "examene/<slug:exam_slug>/<slug:chapter_slug>/",
        views.exam_chapter_topics,
        name="exam_chapter_topics",
    ),
    path(
        "clasa/<int:class_level>/<slug:slug>/",
        views.chapter_topics,
        name="chapter_topics",
    ),
    path("subiect/<int:pk>/", views.topic_detail, name="topic_detail"),
    path(
        "subiect/<int:pk>/genereaza/",
        views.generated_quiz,
        name="generated_quiz",
    ),
    path(
        "subiect/<int:pk>/genereaza/rezultat/",
        views.generated_quiz_result,
        name="generated_quiz_result",
    ),
    path(
        "subiect/<int:pk>/antrenare/",
        views.training,
        name="training",
    ),
    path(
        "subiect/<int:pk>/antrenare/<int:index>/",
        views.training,
        name="training_index",
    ),
    path(
        "subiect/<int:pk>/antrenare/raspuns/",
        views.training_submit,
        name="training_submit",
    ),
    path(
        "subiect/<int:pk>/antrenare/reset/",
        views.training_reset,
        name="training_reset",
    ),
    path("<int:pk>/", views.quiz_take, name="quiz_take"),
    path(
        "<int:pk>/rezultat/<int:attempt_id>/",
        views.quiz_result,
        name="quiz_result",
    ),
]
