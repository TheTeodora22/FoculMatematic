from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import Profile
from accounts.services import (
    award_quiz_xp,
    get_battlepass_preview,
    get_profile_dashboard,
    get_quiz_stats,
    get_recent_quiz_activities,
    level_for_xp,
)
from accounts.utils import get_or_create_profile
from battlepass.models import BattlePassSeason, BattlePassTier, OwnedItem
from battlepass.services import get_active_season, grant_tier_rewards
from django.utils import timezone
from datetime import timedelta

from quizzes.models import AnswerOption, GeneratedQuizSession, GeneratedQuizSessionQuestion, Question, Quiz


class RegisterTests(TestCase):
    def test_register_creates_user_and_profile(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Ana",
                "last_name": "Popescu",
                "username": "newuser",
                "password1": "complexpass123",
                "password2": "complexpass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newuser")
        self.assertEqual(user.first_name, "Ana")
        self.assertEqual(user.last_name, "Popescu")
        self.assertTrue(Profile.objects.filter(user=user).exists())


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="legacy", password="testpass123")
        Profile.objects.filter(user=self.user).delete()

    def test_profile_view_creates_missing_profile(self):
        self.assertFalse(Profile.objects.filter(user=self.user).exists())
        self.client.login(username="legacy", password="testpass123")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_profile_shows_completed_generated_quiz(self):
        self.client.login(username="legacy", password="testpass123")
        topic = Quiz.objects.create(title="Subiect profil", difficulty="easy")
        q = Question.objects.create(quiz=topic, text="2+2?", points=10)
        correct = AnswerOption.objects.create(question=q, text="4", is_correct=True)
        AnswerOption.objects.create(question=q, text="5", is_correct=False)
        session = GeneratedQuizSession.objects.create(
            user=self.user,
            topic=topic,
            status=GeneratedQuizSession.STATUS_COMPLETED,
        )
        GeneratedQuizSessionQuestion.objects.create(
            session=session,
            question=q,
            order=0,
            selected_option=correct,
            is_correct=True,
        )
        response = self.client.get(reverse("profile"))
        self.assertContains(response, "Subiect profil")
        self.assertContains(response, "1/1")
        self.assertNotContains(response, "Încă nu ai completat niciun chestionar")

    def test_profile_redesign_elements(self):
        self.client.login(username="legacy", password="testpass123")
        profile = get_or_create_profile(self.user)
        profile.clasa = 5
        profile.save()
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "profile-hero")
        self.assertContains(response, "legacy")
        self.assertContains(response, "profile-avatar")
        self.assertContains(response, "profile-stats-grid")
        self.assertContains(response, "Clasa mea")
        self.assertContains(response, "/quizzes/clasa/5/")

    def test_profile_empty_state(self):
        self.client.login(username="legacy", password="testpass123")
        response = self.client.get(reverse("profile"))
        self.assertContains(response, "profile-empty")
        self.assertContains(response, "Începe primul chestionar")


class ProfileStatsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="statsuser", password="x")
        self.topic = Quiz.objects.create(title="Stats topic", difficulty="easy")
        q = Question.objects.create(quiz=self.topic, text="1+1?", points=10)
        correct = AnswerOption.objects.create(question=q, text="2", is_correct=True)
        AnswerOption.objects.create(question=q, text="3", is_correct=False)
        session = GeneratedQuizSession.objects.create(
            user=self.user,
            topic=self.topic,
            status=GeneratedQuizSession.STATUS_COMPLETED,
        )
        GeneratedQuizSessionQuestion.objects.create(
            session=session,
            question=q,
            order=0,
            selected_option=correct,
            is_correct=True,
        )

    def test_get_quiz_stats(self):
        stats = get_quiz_stats(self.user)
        self.assertEqual(stats["quizzes_count"], 1)
        self.assertEqual(stats["correct_rate"], 100)

    def test_get_battlepass_preview(self):
        today = timezone.localdate()
        season = BattlePassSeason.objects.create(
            name="Preview Season",
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
        )
        BattlePassTier.objects.create(
            season=season,
            level_req=3,
            reward_name="Phoenix",
            reward_type="avatar",
            reward_value="phoenix_avatar",
        )
        preview = get_battlepass_preview(self.user)
        self.assertIsNotNone(preview)
        self.assertEqual(preview["reward_name"], "Phoenix")
        self.assertEqual(preview["level_req"], 3)

    def test_get_profile_dashboard(self):
        dashboard = get_profile_dashboard(self.user)
        self.assertEqual(dashboard["quizzes_count"], 1)
        self.assertIn("recent_activities", dashboard)
        self.assertIn("avatars/default.svg", dashboard["avatar_path"])


class XpTests(TestCase):
    def test_award_quiz_xp_and_level_up(self):
        user = User.objects.create_user(username="xpuser", password="x")
        profile = get_or_create_profile(user)
        xp, leveled = award_quiz_xp(profile, 100)
        profile.refresh_from_db()
        self.assertEqual(xp, 100)
        self.assertTrue(leveled)
        self.assertEqual(profile.level, 2)
        self.assertEqual(level_for_xp(profile.xp), 2)

    def test_zero_score_awards_no_xp(self):
        user = User.objects.create_user(username="zero", password="x")
        profile = get_or_create_profile(user)
        xp, leveled = award_quiz_xp(profile, 0)
        self.assertEqual(xp, 0)
        self.assertFalse(leveled)


class QuizXpIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="player", password="testpass123")
        self.quiz = Quiz.objects.create(title="XP Quiz", difficulty="easy")
        q = Question.objects.create(quiz=self.quiz, text="1+1?", points=50)
        correct = AnswerOption.objects.create(question=q, text="2", is_correct=True)
        AnswerOption.objects.create(question=q, text="3", is_correct=False)
        self.correct_id = correct.id
        self.q_id = q.id

    def test_quiz_awards_xp(self):
        self.client.login(username="player", password="testpass123")
        self.client.post(
            reverse("quiz_take", args=[self.quiz.pk]),
            {f"q_{self.q_id}": str(self.correct_id)},
        )
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.xp, 50)


class BattlePassTests(TestCase):
    def setUp(self):
        today = timezone.localdate()
        self.season = BattlePassSeason.objects.create(
            name="Test Season",
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
        self.user = User.objects.create_user(username="bpuser", password="x")
        get_or_create_profile(self.user)

    def test_active_season_found(self):
        self.assertEqual(get_active_season(), self.season)

    def test_grant_tier_rewards(self):
        rewards = grant_tier_rewards(self.user, 2)
        self.assertEqual(rewards, ["Dragon"])
        self.assertTrue(
            OwnedItem.objects.filter(user=self.user, item_key="dragon_avatar").exists()
        )

    def test_no_duplicate_owned_items(self):
        grant_tier_rewards(self.user, 2)
        grant_tier_rewards(self.user, 2)
        self.assertEqual(
            OwnedItem.objects.filter(
                user=self.user, item_key="dragon_avatar"
            ).count(),
            1,
        )

    def test_inactive_season_grants_nothing(self):
        self.season.end_date = timezone.localdate() - timedelta(days=1)
        self.season.save()
        rewards = grant_tier_rewards(self.user, 5)
        self.assertEqual(rewards, [])
