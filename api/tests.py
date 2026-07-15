from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile
from battlepass.models import BattlePassSeason, BattlePassTier
from django.utils import timezone
from datetime import timedelta

from quizzes.models import AnswerOption, Question, Quiz


class ApiAuthTests(APITestCase):
    def test_register_and_token(self):
        response = self.client.post(
            reverse("api_register"),
            {"username": "apiuser", "password": "complexpass123", "clasa": 9},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="apiuser").exists())
        self.assertEqual(Profile.objects.get(user__username="apiuser").clasa, 9)

        token_resp = self.client.post(
            reverse("api_token"),
            {"username": "apiuser", "password": "complexpass123"},
            format="json",
        )
        self.assertEqual(token_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", token_resp.data)


class ApiQuizTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="quizapi", password="pass12345")
        self.client.force_authenticate(user=self.user)
        self.quiz = Quiz.objects.create(title="API Quiz", difficulty="easy")
        self.q1 = Question.objects.create(quiz=self.quiz, text="2+2?", points=10)
        self.correct = AnswerOption.objects.create(
            question=self.q1, text="4", is_correct=True
        )
        AnswerOption.objects.create(question=self.q1, text="5", is_correct=False)

    def test_quiz_detail_hides_is_correct(self):
        response = self.client.get(reverse("api_quiz_detail", args=[self.quiz.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        option = response.data["questions"][0]["options"][0]
        self.assertNotIn("is_correct", option)

    def test_submit_valid(self):
        response = self.client.post(
            reverse("api_quiz_submit", args=[self.quiz.pk]),
            {"answers": {str(self.q1.id): self.correct.id}},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["score"], 10)
        self.assertEqual(response.data["xp_gained"], 10)

    def test_submit_partial_rejected(self):
        response = self.client.post(
            reverse("api_quiz_submit", args=[self.quiz.pk]),
            {"answers": {}},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_attempt_not_visible_to_other(self):
        submit = self.client.post(
            reverse("api_quiz_submit", args=[self.quiz.pk]),
            {"answers": {str(self.q1.id): self.correct.id}},
            format="json",
        )
        attempt_id = submit.data["id"]
        other = User.objects.create_user(username="other", password="pass12345")
        self.client.force_authenticate(user=other)
        response = self.client.get(reverse("api_attempt_detail", args=[attempt_id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ApiProfileBattlePassTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="prof", password="pass12345")
        self.client.force_authenticate(user=self.user)
        today = timezone.localdate()
        self.season = BattlePassSeason.objects.create(
            name="API Season",
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
        )
        BattlePassTier.objects.create(
            season=self.season,
            level_req=2,
            reward_name="Dragon",
            reward_type="avatar",
            reward_value="dragon_avatar",
        )

    def test_profile_get(self):
        response = self.client.get(reverse("api_profile"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("xp_progress", response.data)

    def test_battlepass_get(self):
        response = self.client.get(reverse("api_battlepass"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["season"])
        self.assertEqual(len(response.data["tiers"]), 1)
