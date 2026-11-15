from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.test import SimpleTestCase, RequestFactory

from accounts.models import Profile
from FoculMatematic.views import index
from quizzes.models import Quiz
from quizzes.views import VALID_CLASS_LEVELS


class PageExperienceTests(SimpleTestCase):
    def context(self, **kwargs):
        return {"user": AnonymousUser(), "feedback_report_url": "/feedback/raporteaza/", **kwargs}

    def test_home_offers_every_supported_class_without_database_access(self):
        request = RequestFactory().get("/")
        request.user = AnonymousUser()
        response = index(request)
        html = response.content.decode()
        self.assertEqual(tuple(VALID_CLASS_LEVELS), Profile.CLASS_LEVELS)
        for level in Profile.CLASS_LEVELS:
            self.assertIn(f'href="/quizzes/clasa/{level}/"', html)
        self.assertLess(html.index('id="home-classes"'), html.index('id="method-title"'))
        self.assertNotIn("katex.min.js", html)

    def test_session_progress_counts_answered_questions_instead_of_current_question(self):
        topic = Quiz(pk=7, title="Fixture", difficulty="easy")
        item = SimpleNamespace(pk=1, question=SimpleNamespace(text="Alege", options=SimpleNamespace(all=[])))
        for question_number in (1, 4):
            with self.subTest(question=question_number):
                html = render_to_string("quizzes/generated_quiz.html", self.context(
                    topic=topic, item=item, question_number=question_number, total_count=5))
                self.assertIn(f'<progress value="{question_number-1}" max="5"', html)

    def test_result_exposes_a_real_continuation_before_long_explanations(self):
        topic = Quiz(pk=7, title="Fixture", difficulty="easy")
        html = render_to_string("quizzes/generated_quiz_result.html", self.context(
            topic=topic, result=SimpleNamespace(correct_count=1, total_count=2, xp_gained=0),
            wrong_items=[SimpleNamespace(question=SimpleNamespace(text="Fixture", explanation="Explicație"),
                                         selected_option=SimpleNamespace(text="Nu"))]))
        self.assertLess(html.index('href="/quizzes/subiect/7/antrenare/"'), html.index("Explicații —"))
        self.assertIn("Nu ai câștigat XP nou", html)

    def test_pending_google_signin_is_not_an_active_form_submission_or_fake_link(self):
        from accounts.forms import LoginForm, RegisterForm
        for name, form in (("login", LoginForm()), ("register", RegisterForm())):
            html = render_to_string(f"registration/{name}.html", self.context(form=form))
            self.assertIn('type="button" class="btn-google" disabled', html)
            self.assertNotIn('href="#" class="btn-google"', html)

    def test_chapter_without_exercises_does_not_show_an_empty_training_progress_bar(self):
        chapter = SimpleNamespace(title="Pregătire", slug="pregatire")
        html = render_to_string("quizzes/class_chapters.html", self.context(
            class_level=8, chapter_states=[SimpleNamespace(chapter=chapter, question_count=0, topic_count=2)]))
        self.assertIn("Exercițiile sunt în pregătire.", html)
        self.assertNotIn('role="progressbar"', html)
