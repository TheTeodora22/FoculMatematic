from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api.views.auth import RegisterView, TokenObtainPairAllowAnyView
from api.views.battlepass import BattlePassView
from api.views.profile import ProfileView
from api.views.quizzes import (
    AttemptDetailView,
    QuizDetailView,
    QuizListView,
    QuizSubmitView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="api_register"),
    path("auth/token/", TokenObtainPairAllowAnyView.as_view(), name="api_token"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),
    path("quizzes/", QuizListView.as_view(), name="api_quiz_list"),
    path("quizzes/<int:pk>/", QuizDetailView.as_view(), name="api_quiz_detail"),
    path("quizzes/<int:pk>/submit/", QuizSubmitView.as_view(), name="api_quiz_submit"),
    path("attempts/<int:pk>/", AttemptDetailView.as_view(), name="api_attempt_detail"),
    path("profile/", ProfileView.as_view(), name="api_profile"),
    path("battlepass/", BattlePassView.as_view(), name="api_battlepass"),
]
