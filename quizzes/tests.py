from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .mode_services import (
    complete_generated_session,
    pick_questions_for_generated_quiz,
    reset_training_progress,
    session_is_complete,
    start_or_resume_generated_session,
    submit_generated_answer,
    submit_training_answer,
)
from .models import (
    AnswerOption,
    Chapter,
    GeneratedQuizSession,
    Question,
    Quiz,
    QuizAttempt,
    UserQuestionProgress,
)


class QuizFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="quizuser", password="testpass123")
        self.other = User.objects.create_user(username="other", password="testpass123")
        self.quiz = Quiz.objects.create(title="Test", difficulty="easy")
        self.q1 = Question.objects.create(quiz=self.quiz, text="2+2?", points=10)
        self.correct1 = AnswerOption.objects.create(
            question=self.q1, text="4", is_correct=True
        )
        AnswerOption.objects.create(question=self.q1, text="5", is_correct=False)
        self.q2 = Question.objects.create(quiz=self.quiz, text="3+3?", points=10)
        self.correct2 = AnswerOption.objects.create(
            question=self.q2, text="6", is_correct=True
        )
        AnswerOption.objects.create(question=self.q2, text="7", is_correct=False)

    def _post_answers(self, answers: dict):
        self.client.login(username="quizuser", password="testpass123")
        return self.client.post(reverse("quiz_take", args=[self.quiz.pk]), answers)

    def test_anonymous_can_view_quiz(self):
        response = self.client.get(reverse("quiz_take", args=[self.quiz.pk]))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_post_redirects_to_login(self):
        response = self.client.post(
            reverse("quiz_take", args=[self.quiz.pk]),
            {
                f"q_{self.q1.id}": str(self.correct1.id),
                f"q_{self.q2.id}": str(self.correct2.id),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertFalse(QuizAttempt.objects.exists())

    def test_full_correct_submit(self):
        response = self._post_answers(
            {
                f"q_{self.q1.id}": str(self.correct1.id),
                f"q_{self.q2.id}": str(self.correct2.id),
            }
        )
        self.assertEqual(response.status_code, 302)
        attempt = QuizAttempt.objects.get(user=self.user, quiz=self.quiz)
        self.assertEqual(attempt.score, 20)
        self.assertEqual(attempt.max_score, 20)
        self.assertEqual(attempt.answers.count(), 2)

    def test_partial_submit_rejected(self):
        response = self._post_answers({f"q_{self.q1.id}": str(self.correct1.id)})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(QuizAttempt.objects.filter(user=self.user).exists())

    def test_invalid_option_rejected(self):
        response = self._post_answers(
            {
                f"q_{self.q1.id}": "99999",
                f"q_{self.q2.id}": str(self.correct2.id),
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_quiz_result_not_visible_to_other_user(self):
        self._post_answers(
            {
                f"q_{self.q1.id}": str(self.correct1.id),
                f"q_{self.q2.id}": str(self.correct2.id),
            }
        )
        attempt = QuizAttempt.objects.get(user=self.user)
        self.client.login(username="other", password="testpass123")
        response = self.client.get(
            reverse("quiz_result", args=[self.quiz.pk, attempt.pk])
        )
        self.assertEqual(response.status_code, 404)


class TopicModeTestMixin:
    _chapter_counter = 0

    def _make_topic_with_questions(self, count=12):
        TopicModeTestMixin._chapter_counter += 1
        n = TopicModeTestMixin._chapter_counter
        chapter = Chapter.objects.create(
            class_level=5,
            slug=f"test-chapter-{n}",
            title=f"Test Capitol {n}",
            order=n,
        )
        topic = Quiz.objects.create(
            title=f"Subiect test {n}",
            difficulty="easy",
            chapter=chapter,
            source_file=f"test-{n}.json",
        )
        questions = []
        for i in range(count):
            q = Question.objects.create(
                quiz=topic,
                text=f"Întrebarea {i}?",
                points=10,
                explanation=f"Explicație {i}",
            )
            correct = AnswerOption.objects.create(
                question=q, text=f"corect-{i}", is_correct=True
            )
            AnswerOption.objects.create(
                question=q, text=f"gresit-{i}", is_correct=False
            )
            questions.append((q, correct))
        return topic, questions


class PickQuestionsTests(TopicModeTestMixin, TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="picker", password="testpass123")
        self.topic, self.questions = self._make_topic_with_questions(12)

    def test_prioritizes_unseen_then_wrong_then_rest(self):
        for q, _ in self.questions[3:6]:
            UserQuestionProgress.objects.create(
                user=self.user,
                question=q,
                seen_in_generated_quiz=True,
                last_generated_quiz_correct=False,
            )
        for q, _ in self.questions[6:]:
            UserQuestionProgress.objects.create(
                user=self.user,
                question=q,
                seen_in_generated_quiz=True,
                last_generated_quiz_correct=True,
            )

        picked = pick_questions_for_generated_quiz(self.user, self.topic, 10)
        picked_ids = [q.id for q in picked]
        unseen_ids = {self.questions[i][0].id for i in range(3)}
        wrong_ids = {self.questions[i][0].id for i in range(3, 6)}

        self.assertEqual(len(picked), 10)
        self.assertTrue(unseen_ids.issubset(set(picked_ids)))
        self.assertTrue(wrong_ids.issubset(set(picked_ids)))
        first_six = set(picked_ids[:6])
        self.assertTrue(first_six <= unseen_ids | wrong_ids)

    def test_uses_all_questions_when_fewer_than_ten(self):
        topic, questions = self._make_topic_with_questions(6)
        picked = pick_questions_for_generated_quiz(self.user, topic, 10)
        self.assertEqual(len(picked), 6)


class GeneratedSessionTests(TopicModeTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="genuser", password="testpass123")
        self.topic, self.questions = self._make_topic_with_questions(10)

    def test_session_resume_after_partial_answers(self):
        session = start_or_resume_generated_session(self.user, self.topic)
        item0 = session.items.get(order=0)
        item1 = session.items.get(order=1)
        correct0 = AnswerOption.objects.get(question=item0.question, is_correct=True)
        correct1 = AnswerOption.objects.get(question=item1.question, is_correct=True)
        submit_generated_answer(session, item0, correct0.id)
        submit_generated_answer(session, item1, correct1.id)

        resumed = start_or_resume_generated_session(self.user, self.topic)
        self.assertEqual(resumed.pk, session.pk)
        self.assertEqual(resumed.items.filter(selected_option__isnull=False).count(), 2)

    def test_xp_awarded_only_once_per_question(self):
        session = start_or_resume_generated_session(self.user, self.topic)
        for item in session.items.all():
            correct = AnswerOption.objects.get(question=item.question, is_correct=True)
            submit_generated_answer(session, item, correct.id)
        result1 = complete_generated_session(session)
        self.assertEqual(result1["xp_gained"], 100)

        session2 = start_or_resume_generated_session(self.user, self.topic)
        for item in session2.items.all():
            correct = AnswerOption.objects.get(question=item.question, is_correct=True)
            submit_generated_answer(session2, item, correct.id)
        result2 = complete_generated_session(session2)
        self.assertEqual(result2["xp_gained"], 0)

    def test_login_required_for_generated_quiz(self):
        response = self.client.get(reverse("generated_quiz", args=[self.topic.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)


class TrainingTests(TopicModeTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="trainuser", password="testpass123")
        self.topic, self.questions = self._make_topic_with_questions(4)

    def test_training_grid_and_reset(self):
        q0, correct0 = self.questions[0]
        wrong = AnswerOption.objects.filter(question=q0, is_correct=False).first()
        submit_training_answer(self.user, q0, wrong.id)
        progress = UserQuestionProgress.objects.get(user=self.user, question=q0)
        self.assertEqual(progress.training_status, UserQuestionProgress.TRAINING_WRONG)

        submit_training_answer(self.user, q0, correct0.id)
        progress.refresh_from_db()
        self.assertEqual(progress.training_status, UserQuestionProgress.TRAINING_CORRECT)

        reset_training_progress(self.user, self.topic)
        progress.refresh_from_db()
        self.assertEqual(
            progress.training_status, UserQuestionProgress.TRAINING_UNANSWERED
        )

    def test_training_retry_after_wrong_shows_options(self):
        self.client.login(username="trainuser", password="testpass123")
        q0 = self.questions[0][0]
        wrong = AnswerOption.objects.filter(question=q0, is_correct=False).first()
        response = self.client.post(
            reverse("training_index", args=[self.topic.pk, 0]),
            {"option_id": wrong.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Încearcă alt răspuns")
        self.assertContains(response, "Verifică răspunsul")
        self.assertContains(response, wrong.text)

    def test_login_required_for_training(self):
        response = self.client.get(reverse("training", args=[self.topic.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_training_page_shows_grid(self):
        self.client.login(username="trainuser", password="testpass123")
        response = self.client.get(reverse("training", args=[self.topic.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "training-grid")
        self.assertContains(response, "training-data")
        self.assertContains(response, "training-loader")
        self.assertContains(response, "training.js")
        self.assertContains(response, '"questions"')

    def test_training_submit_json_correct(self):
        self.client.login(username="trainuser", password="testpass123")
        q0, correct0 = self.questions[0]
        response = self.client.post(
            reverse("training_submit", args=[self.topic.pk]),
            {"question_id": q0.id, "option_id": correct0.id},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["is_correct"])
        self.assertEqual(payload["status"], UserQuestionProgress.TRAINING_CORRECT)
        progress = UserQuestionProgress.objects.get(user=self.user, question=q0)
        self.assertEqual(progress.training_status, UserQuestionProgress.TRAINING_CORRECT)

    def test_training_submit_json_wrong(self):
        self.client.login(username="trainuser", password="testpass123")
        q0 = self.questions[0][0]
        wrong = AnswerOption.objects.filter(question=q0, is_correct=False).first()
        response = self.client.post(
            reverse("training_submit", args=[self.topic.pk]),
            {"question_id": q0.id, "option_id": wrong.id},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["is_correct"])
        self.assertEqual(payload["status"], UserQuestionProgress.TRAINING_WRONG)

    def test_training_submit_requires_login(self):
        q0, correct0 = self.questions[0]
        response = self.client.post(
            reverse("training_submit", args=[self.topic.pk]),
            {"question_id": q0.id, "option_id": correct0.id},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)


class NavigationTests(TopicModeTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="navuser", password="testpass123")
        self.topic, _ = self._make_topic_with_questions(3)
        self.chapter_title = self.topic.chapter.title

    def test_class_chapters_requires_login(self):
        response = self.client.get(reverse("class_chapters", args=[5]))
        self.assertEqual(response.status_code, 302)

    def test_topic_detail_requires_login(self):
        response = self.client.get(reverse("topic_detail", args=[self.topic.pk]))
        self.assertEqual(response.status_code, 302)

    def test_class_chapters_lists_chapter(self):
        self.client.login(username="navuser", password="testpass123")
        response = self.client.get(reverse("class_chapters", args=[5]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.chapter_title)


class ExamTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="examuser", password="testpass123")

    def test_exam_detail_requires_login(self):
        response = self.client.get(reverse("exam_detail", args=["evaluare-nationala"]))
        self.assertEqual(response.status_code, 302)

    def test_exam_detail_page(self):
        self.client.login(username="examuser", password="testpass123")
        response = self.client.get(reverse("exam_detail", args=["evaluare-nationala"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Evaluarea Națională")

    def test_exam_unknown_slug_404(self):
        self.client.login(username="examuser", password="testpass123")
        response = self.client.get(reverse("exam_detail", args=["inexistent"]))
        self.assertEqual(response.status_code, 404)

    def test_tagged_topic_appears_on_exam_page(self):
        from quizzes.lesson_tags import topics_for_exam

        topic = Quiz.objects.create(
            title="Subiect EN",
            difficulty="easy",
            class_levels=[8],
            exam_slugs=["evaluare-nationala"],
        )
        self.client.login(username="examuser", password="testpass123")
        response = self.client.get(reverse("exam_detail", args=["evaluare-nationala"]))
        self.assertContains(response, "Subiect EN")
        self.assertIn(topic, list(topics_for_exam("evaluare-nationala")))


class LessonTagTests(TestCase):
    def test_build_lesson_tags_from_fields(self):
        from quizzes.lesson_tags import build_lesson_tags

        chapter = Chapter.objects.create(
            class_level=5,
            slug="capitol-test",
            title="Capitol test",
        )
        topic = Quiz.objects.create(
            title="Lectie mixta",
            difficulty="easy",
            chapter=chapter,
            class_levels=[5, 8],
            exam_slugs=["evaluare-nationala"],
        )
        tags = build_lesson_tags(topic)
        labels = [tag["label"] for tag in tags]
        self.assertIn("Clasa a 5-a", labels)
        self.assertIn("Clasa a 8-a", labels)
        self.assertIn("Evaluarea Națională", labels)
