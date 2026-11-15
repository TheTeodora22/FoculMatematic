"""Release gates: assert desired behavior; known defects deliberately fail.

Run on Django's isolated test database, never against the live database.
"""
import json
from io import StringIO
from pathlib import Path

from django.contrib.auth import authenticate, get_user_model
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from accounts.signals import ensure_dev_users
from quizzes.mode_services import build_training_payload
from quizzes.models import AnswerOption, Question, Quiz


@override_settings(
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    ANALYTICS_ENABLED=False,
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class LaunchP0FlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('release-student', password='Test-only-123!')
        self.topic = Quiz.objects.create(title='Release fixture', difficulty='easy')
        self.question = Question.objects.create(quiz=self.topic, text='2+2?', points=10)
        self.correct = AnswerOption.objects.create(question=self.question, text='4', is_correct=True)
        AnswerOption.objects.create(question=self.question, text='5', is_correct=False)

    def test_classic_repeated_identical_post_does_not_award_xp_twice(self):
        """Replay the same request, rather than start a second deliberate attempt."""
        self.client.force_login(self.user)
        url = reverse('quiz_take', args=[self.topic.pk])
        answers = {f'q_{self.question.pk}': str(self.correct.pk)}
        self.assertEqual(self.client.post(url, answers).status_code, 302)
        self.user.profile.refresh_from_db()
        awarded_once = self.user.profile.xp
        self.assertGreater(awarded_once, 0)
        self.client.post(url, answers)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.xp, awarded_once,
                         'An identical POST replay awarded XP a second time (P0-18).')

    def test_password_reset_page_can_be_rendered(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200, 'Password recovery must be reachable (P0-09).')
        self.assertContains(response, 'name="email"')

    def test_login_exposes_a_password_recovery_link(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("password_reset")}"',
                            msg_prefix='P0-09: users cannot discover password recovery from login')

    def test_training_payload_does_not_disclose_the_answer_key(self):
        payload = build_training_payload(self.user, self.topic, 0, '/fixture/submit/')
        first = payload['questions'][0]
        self.assertNotIn('correctOptionId', first,
                         'Answer keys are available before answering (P0-27); this gate requires a product decision for training mode.')

    def test_migrating_development_database_blocks_known_accounts_in_production(self):
        with override_settings(DEBUG=True):
            call_command('seed_dev_users', stdout=StringIO())
        # Keep the SAME database: this is precisely the missing migration scenario.
        with override_settings(DEBUG=False):
            ensure_dev_users(sender=None, using='default')
            for name, password in [('demo', 'DemoMatematic123!'), ('admin', 'AdminMatematic123!')]:
                with self.subTest(account=name):
                    self.assertIsNone(authenticate(username=name, password=password),
                                      'Known development credentials still work after switching to production (P0-25).')

    def test_unrelated_option_is_rejected_without_awarding_xp(self):
        other = Question.objects.create(quiz=self.topic, text='Other')
        foreign = AnswerOption.objects.create(question=other, text='unrelated', is_correct=True)
        self.client.force_login(self.user)
        before = self.user.profile.xp
        response = self.client.post(reverse('quiz_take', args=[self.topic.pk]),
                                    {f'q_{self.question.pk}': foreign.pk, f'q_{other.pk}': foreign.pk})
        self.assertEqual(response.status_code, 400)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.xp, before)


class LaunchP0ContentTests(SimpleTestCase):
    def questions(self):
        root = Path(__file__).resolve().parents[1] / 'data/quizzes'
        for path in sorted(root.glob('clasa_*/*.json')):
            data = json.loads(path.read_text(encoding='utf-8-sig'))
            for index, question in enumerate(data.get('questions', []), 1):
                yield path.name, index, question

    def test_every_question_has_an_explanation(self):
        missing = [f'{name} #{index}' for name, index, q in self.questions()
                   if not str(q.get('explanation', '')).strip()]
        self.assertFalse(missing, f'P0-20: {len(missing)} missing explanations: {missing[:8]}')

    def test_options_have_one_correct_answer_and_distinct_text(self):
        issues = []
        for name, index, q in self.questions():
            options = q.get('options', [])
            if not options:
                continue
            values = [o['text'].strip() for o in options]
            if sum(bool(o.get('is_correct')) for o in options) != 1 or len(set(values)) != len(values):
                issues.append(f'{name} #{index}')
        self.assertFalse(issues, f'P0-21: invalid answer choices: {issues}')
