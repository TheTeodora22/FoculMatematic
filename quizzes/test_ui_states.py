from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser, User
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import AnswerOption, Chapter, Question, Quiz


class StatePanelTests(SimpleTestCase):
    def context(self, **values):
        return {"user": AnonymousUser(), "feedback_report_url": "/feedback/raporteaza/", **values}

    def test_panel_escapes_content_and_has_a_real_action(self):
        html = render_to_string("includes/state_panel.html", {
            "state_title": "În pregătire", "state_text": "<script>fixture</script>",
            "action_url": "/quizzes/", "action_label": "Vezi clasele",
        })
        self.assertIn("&lt;script&gt;", html)
        self.assertIn('href="/quizzes/"', html)

    def test_empty_class_and_chapter_have_recovery_actions(self):
        html = render_to_string("quizzes/class_chapters.html", self.context(class_level=5, chapter_states=[]))
        self.assertIn("Clasa este în pregătire", html)
        self.assertIn("Vezi clasele", html)
        html = render_to_string("quizzes/chapter_topics.html", self.context(
            class_level=5, chapter=SimpleNamespace(title="Fixture", slug="fixture"), topic_states=[]))
        self.assertIn("Capitolul este în pregătire", html)
        self.assertIn("Vezi capitolele", html)

    def test_no_season_does_not_render_a_reward_list(self):
        html = render_to_string("battlepass/index.html", self.context(season=None))
        self.assertIn("Momentan nu există un sezon activ", html)
        self.assertIn("Continuă învățarea", html)
        self.assertNotIn('class="card tier-card', html)

    def test_lab_has_independent_boot_and_retry(self):
        html = render_to_string("math_demo.html", self.context())
        self.assertIn("math-demo-boot.js", html)
        self.assertIn("data-reload-page", html)
        self.assertIn('id="boards-error"', html)


class EmptyLessonTests(TestCase):
    def test_training_question_numbers_are_visible_without_javascript(self):
        user = User.objects.create_user(username="numbered-grid-fixture", password="fixture-pass")
        topic = Quiz.objects.create(title="Grilă numerotată", difficulty="easy")
        for index in range(3):
            question = Question.objects.create(quiz=topic, text=f"Întrebarea {index}")
            AnswerOption.objects.create(question=question, text="Da", is_correct=True)
            AnswerOption.objects.create(question=question, text="Nu", is_correct=False)
        self.client.force_login(user)
        response = self.client.get(reverse("training_index", args=[topic.pk, 0]))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertRegex(html, r'data-training-index="0"[^>]*>\s*1\s*</a>')
        self.assertRegex(html, r'data-training-index="2"[^>]*>\s*3\s*</a>')

    def test_empty_lesson_explains_its_state_without_starting_unavailable_modes(self):
        user = User.objects.create_user(username="empty-ui-fixture", password="fixture-pass")
        chapter = Chapter.objects.create(class_level=5, slug="empty-ui", title="Fixture")
        topic = Quiz.objects.create(chapter=chapter, title="Lecție goală", difficulty="easy")
        self.client.force_login(user)
        response = self.client.get(reverse("topic_detail", args=[topic.pk]))
        self.assertContains(response, "Exercițiile sunt în pregătire")
        self.assertNotContains(response, reverse("training_reset", args=[topic.pk]))
        self.assertNotContains(response, f'href="{reverse("generated_quiz", args=[topic.pk])}"')
