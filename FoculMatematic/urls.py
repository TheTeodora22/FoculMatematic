from django.urls import path
from . import views
from .math_demo import math_demo
urlpatterns = [
	path("", views.index, name="index"),
    path("laborator-matematic/", math_demo, name="math_demo"),
]
