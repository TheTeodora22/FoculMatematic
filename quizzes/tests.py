import json

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
    submit_parentheses_answer,
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

    def test_parentheses_answer_and_json_payload(self):
        question = Question.objects.create(
            quiz=self.topic,
            text="Pune parantezele.",
            question_type=Question.TYPE_PARENTHESES_DRAG,
            interactive_data={
                "tokens": ["36", "+ 64", "+ 20"],
                "correct_open_index": 0,
                "correct_close_index": 2,
            },
            explanation="36 + 64 = 100.",
        )
        wrong = submit_parentheses_answer(self.user, question, 1, 3)
        self.assertFalse(wrong["is_correct"])

        self.client.login(username="trainuser", password="testpass123")
        response = self.client.post(
            reverse("training_submit", args=[self.topic.pk]),
            {"question_id": question.id, "open_index": 0, "close_index": 2},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["is_correct"])
        self.assertEqual(payload["status"], UserQuestionProgress.TRAINING_CORRECT)

    def test_all_subtraction_interactive_answers_are_checked(self):
        cases = [
            (
                Question.TYPE_COLUMN_SUBTRACTION,
                {
                    "minuend": "8642",
                    "subtrahend": "3217",
                    "correct_result": "5425",
                    "borrow_columns": [False, False, False, True],
                },
                {
                    "result_digits": "5425",
                    "borrow_columns": json.dumps([False, False, False, True]),
                },
            ),
            (
                Question.TYPE_MISSING_DIGITS,
                {
                    "minuend": "734",
                    "subtrahend": "269",
                    "result": "465",
                    "missing": ["minuend:1", "subtrahend:1"],
                },
                {"values": json.dumps({"minuend:1": "3", "subtrahend:1": "6"})},
            ),
            (
                Question.TYPE_ERROR_SPOTTING,
                {
                    "minuend": "5032",
                    "subtrahend": "1876",
                    "shown_result": "3256",
                    "correct_result": "3156",
                    "error_column": 1,
                },
                {"selected_column": "1"},
            ),
            (
                Question.TYPE_PARENTHESES_TARGET,
                {
                    "tokens": ["80", "− 30", "+ 10"],
                    "correct_open_index": 1,
                    "correct_close_index": 3,
                    "target": 40,
                },
                {"open_index": "1", "close_index": "3"},
            ),
            (
                Question.TYPE_INPUT_OUTPUT,
                {
                    "operation": "subtract",
                    "value": 275,
                    "rows": [
                        {"input": 1200, "output": None},
                        {"input": None, "output": 625},
                    ],
                },
                {"values": json.dumps({"0:output": "925", "1:input": "900"})},
            ),
        ]
        self.client.login(username="trainuser", password="testpass123")

        for index, (question_type, interactive, answer) in enumerate(cases):
            with self.subTest(question_type=question_type):
                question = Question.objects.create(
                    quiz=self.topic,
                    text=f"Exercițiu interactiv {index}",
                    question_type=question_type,
                    interactive_data=interactive,
                    explanation="Rezolvare corectă.",
                )
                response = self.client.post(
                    reverse("training_submit", args=[self.topic.pk]),
                    {"question_id": question.id, **answer},
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["is_correct"])
                progress = UserQuestionProgress.objects.get(
                    user=self.user, question=question
                )
                self.assertEqual(
                    progress.training_status,
                    UserQuestionProgress.TRAINING_CORRECT,
                )

    def test_addition_interactive_answers_are_checked(self):
        cases = [
            (
                Question.TYPE_COLUMN_ADDITION,
                {
                    "addend1": "468",
                    "addend2": "357",
                    "correct_result": "825",
                    "carry_columns": [True, True, False],
                },
                {
                    "result_digits": "825",
                    "borrow_columns": json.dumps([True, True, False]),
                },
            ),
            (
                Question.TYPE_MISSING_DIGITS,
                {
                    "operation": "add",
                    "addend1": "357",
                    "addend2": "245",
                    "result": "602",
                    "missing": ["addend1:1", "addend2:1"],
                },
                {"values": json.dumps({"addend1:1": "5", "addend2:1": "4"})},
            ),
            (
                Question.TYPE_ERROR_SPOTTING,
                {
                    "operation": "add",
                    "addend1": "468",
                    "addend2": "357",
                    "shown_result": "815",
                    "correct_result": "825",
                    "error_column": 1,
                },
                {"selected_column": "1"},
            ),
            (
                Question.TYPE_INPUT_OUTPUT,
                {
                    "operation": "add",
                    "value": 125,
                    "rows": [
                        {"input": 775, "output": None},
                        {"input": None, "output": 900},
                    ],
                },
                {"values": json.dumps({"0:output": "900", "1:input": "775"})},
            ),
        ]
        self.client.login(username="trainuser", password="testpass123")
        for index, (question_type, interactive, answer) in enumerate(cases):
            with self.subTest(question_type=question_type):
                question = Question.objects.create(
                    quiz=self.topic,
                    text=f"Adunare interactivă {index}",
                    question_type=question_type,
                    interactive_data=interactive,
                )
                response = self.client.post(
                    reverse("training_submit", args=[self.topic.pk]),
                    {"question_id": question.id, **answer},
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["is_correct"])

    def test_factor_common_interactive_answers_are_checked(self):
        cases = [
            (
                Question.TYPE_FACTOR_BUILDER,
                {"expression": "3 · 45 + 3 · 15", "common_factor": 3, "inner_terms": [45, 15], "operators": ["+"], "result": 180},
                {"values": json.dumps({"factor": "3", "inner:0": "45", "inner:1": "15", "result": "180"})},
            ),
            (
                Question.TYPE_FACTOR_ERROR,
                {"steps": ["28 · 7 + 28 · 12", "= 28 · 19", "= 512"], "error_index": 2},
                {"selected_step": "2"},
            ),
            (
                Question.TYPE_FACTOR_MATCH,
                {
                    "pairs": [
                        {"left": "7·2+7·3", "right": "7·(2+3)"},
                        {"left": "8·9−8", "right": "8·(9−1)"},
                        {"left": "4·5+4·5", "right": "4·(5+5)"},
                    ],
                    "right_order": [2, 0, 1],
                },
                {"values": json.dumps({"0": "0", "1": "1", "2": "2"})},
            ),
        ]
        self.client.login(username="trainuser", password="testpass123")
        for index, (question_type, interactive, answer) in enumerate(cases):
            with self.subTest(question_type=question_type):
                question = Question.objects.create(
                    quiz=self.topic,
                    text=f"Factor comun interactiv {index}",
                    question_type=question_type,
                    interactive_data=interactive,
                )
                response = self.client.post(
                    reverse("training_submit", args=[self.topic.pk]),
                    {"question_id": question.id, **answer},
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["is_correct"])

    def test_power_interactive_answers_are_checked(self):
        cases = [
            (
                Question.TYPE_POWER_BUILDER,
                {"mode": "compose", "base": 3, "exponent": 4, "value": 81, "factors": [3, 3, 3, 3]},
                {"base": "3", "exponent": "4"},
            ),
            (
                Question.TYPE_POWER_BUILDER,
                {"mode": "expand", "base": 5, "exponent": 3, "value": 125, "factors": [5, 5, 5]},
                {"factor:0": "5", "factor:1": "5", "factor:2": "5"},
            ),
            (
                Question.TYPE_POWER_BUILDER,
                {"mode": "missing", "base": 2, "exponent": 6, "value": 64, "factors": [2, 2, 2, 2, 2, 2], "missing": "value"},
                {"value": "64"},
            ),
            (
                Question.TYPE_POWER_MATCH,
                {"pairs": [{"left": "2⁵", "right": "32"}, {"left": "3³", "right": "27"}, {"left": "5²", "right": "25"}], "right_order": [2, 0, 1]},
                {"0": "0", "1": "1", "2": "2"},
            ),
            (
                Question.TYPE_POWER_TABLE,
                {"rows": [{"base": 2, "exponent": 5, "value": 32, "missing": "value"}, {"base": 3, "exponent": 4, "value": 81, "missing": "exponent"}]},
                {"0:value": "32", "1:exponent": "4"},
            ),
            (
                Question.TYPE_POWER_CYCLE,
                {"base": 2, "exponent": 10, "cycle": [2, 4, 8, 6], "last_digit": 4},
                {"cycle:0": "2", "cycle:1": "4", "cycle:2": "8", "cycle:3": "6", "last_digit": "4"},
            ),
            (
                Question.TYPE_POWER_SQUARE,
                {"side": 4, "value": 16},
                {"base": "4", "exponent": "2", "value": "16"},
            ),
        ]
        self.client.login(username="trainuser", password="testpass123")
        for index, (question_type, interactive, values) in enumerate(cases):
            with self.subTest(question_type=question_type):
                question = Question.objects.create(
                    quiz=self.topic,
                    text=f"Putere interactivă {index}",
                    question_type=question_type,
                    format_tag=Question.FORMAT_INTERACTIVE,
                    interactive_data=interactive,
                )
                response = self.client.post(
                    reverse("training_submit", args=[self.topic.pk]),
                    {"question_id": question.id, "values": json.dumps(values)},
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["is_correct"])

    def test_multiplication_interactive_answers_are_checked(self):
        cases = [
            (
                Question.TYPE_COLUMN_MULTIPLICATION,
                {
                    "multiplicand": "128",
                    "multiplier": "4",
                    "correct_result": "512",
                    "carry_columns": [True, True, False],
                },
                {"result_digits": "512", "borrow_columns": json.dumps([True, True, False])},
            ),
            (
                Question.TYPE_MISSING_DIGITS,
                {
                    "operation": "multiply",
                    "factor1": "128",
                    "factor2": "004",
                    "result": "512",
                    "missing": ["factor1:1", "result:1"],
                },
                {"values": json.dumps({"factor1:1": "2", "result:1": "1"})},
            ),
            (
                Question.TYPE_ERROR_SPOTTING,
                {
                    "operation": "multiply",
                    "factor1": "128",
                    "factor2": "004",
                    "shown_result": "502",
                    "correct_result": "512",
                    "error_column": 1,
                },
                {"selected_column": "1"},
            ),
            (
                Question.TYPE_INPUT_OUTPUT,
                {
                    "operation": "multiply",
                    "value": 3,
                    "rows": [{"input": 12, "output": None}, {"input": None, "output": 45}],
                },
                {"values": json.dumps({"0:output": "36", "1:input": "15"})},
            ),
        ]
        self.client.login(username="trainuser", password="testpass123")
        for index, (question_type, interactive, answer) in enumerate(cases):
            with self.subTest(question_type=question_type):
                question = Question.objects.create(
                    quiz=self.topic,
                    text=f"Înmulțire interactivă {index}",
                    question_type=question_type,
                    interactive_data=interactive,
                )
                response = self.client.post(
                    reverse("training_submit", args=[self.topic.pk]),
                    {"question_id": question.id, **answer},
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["is_correct"])

    def test_power_rules_and_comparison_answers_are_checked(self):
        cases = [
            (
                Question.TYPE_POWER_RULE_CHAIN,
                {"expression": "5³ · 5⁷ : 5⁴", "stages": [{"label": "5³ · 5⁷", "base": 5, "exponent": 10}, {"label": "5¹⁰ : 5⁴", "base": 5, "exponent": 6}]},
                {"values": json.dumps({"stage:0": "10", "stage:1": "6"})},
            ),
            (
                Question.TYPE_POWER_COMPARE,
                {"left": "9¹⁵", "right": "3²⁹", "relation": ">"},
                {"relation": ">"},
            ),
            (
                Question.TYPE_POWER_ORDER,
                {"direction": "asc", "items": [{"label": "2⁴", "value": 16}, {"label": "3³", "value": 27}, {"label": "5²", "value": 25}], "display_order": [1, 0, 2]},
                {"order": json.dumps([0, 2, 1])},
            ),
        ]
        self.client.login(username="trainuser", password="testpass123")
        for index, (question_type, interactive, answer) in enumerate(cases):
            with self.subTest(question_type=question_type):
                question = Question.objects.create(
                    quiz=self.topic,
                    text=f"Regulă sau comparație {index}",
                    question_type=question_type,
                    format_tag=Question.FORMAT_INTERACTIVE,
                    interactive_data=interactive,
                )
                response = self.client.post(
                    reverse("training_submit", args=[self.topic.pk]),
                    {"question_id": question.id, **answer},
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["is_correct"])

    def test_operation_order_interactive_answers_are_checked(self):
        cases = [
            (
                Question.TYPE_OPERATION_SEQUENCE,
                {"expression": "2 + 3² · 4", "steps": ["3²", "9 · 4", "2 + 36"], "display_order": [2, 0, 1], "correct_order": [0, 1, 2]},
                {"order": json.dumps([0, 1, 2])},
            ),
            (
                Question.TYPE_OPERATION_WORKBENCH,
                {"expression": "80 − 7 · 6", "stages": [{"expression": "7 · 6", "answer": 42}, {"expression": "80 − 42", "answer": 38}]},
                {"values": json.dumps({"stage:0": "42", "stage:1": "38"})},
            ),
        ]
        self.client.login(username="trainuser", password="testpass123")
        for index, (question_type, interactive, answer) in enumerate(cases):
            with self.subTest(question_type=question_type):
                question = Question.objects.create(
                    quiz=self.topic,
                    text=f"Ordinea operațiilor {index}",
                    question_type=question_type,
                    format_tag=Question.FORMAT_INTERACTIVE,
                    interactive_data=interactive,
                )
                response = self.client.post(
                    reverse("training_submit", args=[self.topic.pk]),
                    {"question_id": question.id, **answer},
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["is_correct"])

    def test_division_interactive_answers_are_checked(self):
        cases = [
            (Question.TYPE_COLUMN_DIVISION, {"dividend": 624, "divisor": 4, "quotient": 156, "remainders": [2, 2, 0]}, {"quotient": "156", "remainders": json.dumps(["2", "2", "0"])}),
            (Question.TYPE_COLUMN_DIVISION, {"dividend": 235, "divisor": 7, "quotient": 33, "remainder": 4, "remainders": [2, 2, 4]}, {"quotient": "33", "remainders": json.dumps(["2", "2", "4"])}),
            (Question.TYPE_MISSING_DIGITS, {"operation": "divide", "dividend": "624", "divisor": "004", "quotient": "156", "missing": ["dividend:1", "quotient:1"]}, {"values": json.dumps({"dividend:1": "2", "quotient:1": "5"})}),
            (Question.TYPE_ERROR_SPOTTING, {"operation": "divide", "dividend": "624", "divisor": "004", "shown_result": "166", "correct_result": "156", "error_column": 1}, {"selected_column": "1"}),
            (Question.TYPE_DIVISION_RELATION, {"dividend": 2268, "divisor": 63, "quotient": 36, "missing": "quotient"}, {"value": "36"}),
            (Question.TYPE_DIVISION_RELATION, {"dividend": 104, "divisor": 5, "quotient": 20, "remainder": 4, "missing": "remainder"}, {"value": "4"}),
            (Question.TYPE_INPUT_OUTPUT, {"operation": "divide", "value": 4, "rows": [{"input": 624, "output": None}, {"input": None, "output": 200}]}, {"values": json.dumps({"0:output": "156", "1:input": "800"})}),
            (Question.TYPE_OPERATION_CHAIN, {"start": 1800, "steps": [{"operation": "divide", "value": 12, "result": 150}, {"operation": "multiply", "value": 5, "result": 750}]}, {"values": json.dumps(["150", "750"])}),
            (Question.TYPE_DIVISION_TABLE, {"rows": [{"dividend": 624, "divisor": 4, "quotient": 156, "missing": "quotient"}, {"dividend": 735, "divisor": 35, "quotient": 21, "missing": "divisor"}]}, {"values": json.dumps({"0:quotient": "156", "1:divisor": "35"})}),
            (Question.TYPE_DIVISION_TABLE, {"rows": [{"dividend": 235, "divisor": 7, "quotient": 33, "remainder": 4, "missing": "remainder"}, {"dividend": 566, "divisor": 9, "quotient": 62, "remainder": 8, "missing": "quotient"}]}, {"values": json.dumps({"0:remainder": "4", "1:quotient": "62"})}),
            (Question.TYPE_NUMERIC_INPUT, {"answer": 45, "suffix": "kg"}, {"value": "45"}),
        ]
        self.client.login(username="trainuser", password="testpass123")
        for index, (question_type, interactive, answer) in enumerate(cases):
            with self.subTest(question_type=question_type):
                question = Question.objects.create(quiz=self.topic, text=f"Împărțire interactivă {index}", question_type=question_type, format_tag=Question.FORMAT_INTERACTIVE, interactive_data=interactive)
                response = self.client.post(reverse("training_submit", args=[self.topic.pk]), {"question_id": question.id, **answer})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["is_correct"])

    def test_unit_reduction_answers_are_checked(self):
        question = Question.objects.create(
            quiz=self.topic,
            text="Alege sensul dependenței.",
            question_type=Question.TYPE_UNIT_REDUCTION,
            format_tag=Question.FORMAT_INTERACTIVE,
            interactive_data={
                "mode": "dependency_direction",
                "first_change": "mai multe robinete",
                "second_change": "mai puțin timp",
                "answers": {"relation": "inverse"},
            },
        )
        self.client.login(username="trainuser", password="testpass123")
        response = self.client.post(
            reverse("training_submit", args=[self.topic.pk]),
            {"question_id": question.id, "values": json.dumps({"relation": "inverse"})},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_correct"])

    def test_numeral_system_interactive_answers_are_checked(self):
        cases = [
            (
                Question.TYPE_BASE_VALUES,
                {"mode": "complete_equality", "left_value": "13", "left_base": 10, "answer_base": 2, "answers": {"value": "1101"}},
                {"values": json.dumps({"value": "1101"})},
            ),
            (
                Question.TYPE_BASE_MATCH,
                {"pairs": [{"left": "5", "right": "101"}, {"left": "6", "right": "110"}, {"left": "7", "right": "111"}], "right_order": [2, 0, 1]},
                {"values": json.dumps({"0": "0", "1": "1", "2": "2"})},
            ),
            (
                Question.TYPE_BINARY_TOGGLE,
                {"decimal": 13, "binary": "1101"},
                {"values": json.dumps({"bits": "1101"})},
            ),
            (
                Question.TYPE_BASE_ERROR,
                {"steps": ["13 : 2 = 6 r 1", "6 : 2 = 3 r 0", "3 : 2 = 1 r 0"], "error_index": 2},
                {"selected_step": "2"},
            ),
        ]
        self.client.login(username="trainuser", password="testpass123")
        for index, (question_type, interactive, answer) in enumerate(cases):
            with self.subTest(question_type=question_type):
                question = Question.objects.create(
                    quiz=self.topic,
                    text=f"Sisteme de numerație {index}",
                    question_type=question_type,
                    format_tag=Question.FORMAT_INTERACTIVE,
                    interactive_data=interactive,
                )
                response = self.client.post(
                    reverse("training_submit", args=[self.topic.pk]),
                    {"question_id": question.id, **answer},
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["is_correct"])

    def test_divisibility_interactive_answers_are_checked(self):
        cases = [
            (
                Question.TYPE_DIVISIBILITY_VALUES,
                {"mode": "relation", "a": 56, "b": 7, "c": 8, "missing": "c", "fields": [{"key": "c"}], "answers": {"c": 8}},
                {"values": json.dumps({"c": "8"})},
            ),
            (
                Question.TYPE_DIVISIBILITY_VALUES,
                {"mode": "digit_sum", "number": 6498, "criterion": 9, "fields": [{"key": "sum"}], "answers": {"sum": 27}},
                {"values": json.dumps({"sum": "27"})},
            ),
            (
                Question.TYPE_DIVISIBILITY_SELECT,
                {"mode": "divisors", "cards": [{"id": "1", "label": "1"}, {"id": "2", "label": "2"}, {"id": "3", "label": "3"}, {"id": "4", "label": "4"}], "correct_ids": ["1", "2", "4"]},
                {"selected_ids": json.dumps(["4", "1", "2"])},
            ),
            (
                Question.TYPE_DIVISIBILITY_SORT,
                {"mode": "two_zones", "zones": [{"id": "yes", "label": "Da"}, {"id": "no", "label": "Nu"}], "cards": [{"id": "12", "label": "12", "zone": "yes"}, {"id": "14", "label": "14", "zone": "no"}, {"id": "20", "label": "20", "zone": "yes"}, {"id": "22", "label": "22", "zone": "no"}]},
                {"placements": json.dumps({"12": "yes", "14": "no", "20": "yes", "22": "no"})},
            ),
            (
                Question.TYPE_DIVISIBILITY_ERROR,
                {"steps": ["7 · 1 = 7", "7 · 2 = 14", "7 · 3 = 20"], "error_index": 2},
                {"selected_step": "2"},
            ),
            (
                Question.TYPE_CRITERIA_TABLE,
                {
                    "numbers": [10, 36, 45],
                    "divisors": [2, 5],
                    "answers": {"0:0": True, "0:1": True, "0:2": False, "1:0": True, "1:1": False, "1:2": True},
                },
                {"values": json.dumps({"0:0": True, "0:1": True, "0:2": False, "1:0": True, "1:1": False, "1:2": True})},
            ),
            (
                Question.TYPE_PRIME_WORKBENCH,
                {
                    "mode": "trial",
                    "number": 71,
                    "tests": [{"divisor": 2, "remainder": 1}, {"divisor": 3, "remainder": 2}],
                    "answers": {"remainder:2": 1, "remainder:3": 2, "classification": "prim"},
                },
                {"values": json.dumps({"remainder:2": "1", "remainder:3": "2", "classification": "prim"})},
            ),
            (
                Question.TYPE_PRIME_WORKBENCH,
                {"mode": "prime_pair", "target": 30, "operator": "+", "fields": [{"key": "left"}, {"key": "right"}], "answers": {"left": 13, "right": 17}},
                {"values": json.dumps({"left": "7", "right": "23"})},
            ),
            (
                Question.TYPE_DECIMAL_WORKBENCH,
                {"mode": "conversion", "source": "37/100", "target_kind": "decimal", "fields": [{"key": "decimal"}], "answers": {"decimal": "0,37"}},
                {"values": json.dumps({"decimal": "0.37"})},
            ),
        ]
        self.client.login(username="trainuser", password="testpass123")
        for index, (question_type, interactive, answer) in enumerate(cases):
            with self.subTest(question_type=question_type):
                question = Question.objects.create(
                    quiz=self.topic,
                    text=f"Divizibilitate interactivă {index}",
                    question_type=question_type,
                    format_tag=Question.FORMAT_INTERACTIVE,
                    interactive_data=interactive,
                )
                response = self.client.post(
                    reverse("training_submit", args=[self.topic.pk]),
                    {"question_id": question.id, **answer},
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["is_correct"])

    def test_generated_quiz_excludes_parentheses_questions(self):
        Question.objects.create(
            quiz=self.topic,
            text="Exercițiu interactiv",
            question_type=Question.TYPE_PARENTHESES_DRAG,
            interactive_data={
                "tokens": ["36", "+ 64", "+ 20"],
                "correct_open_index": 0,
                "correct_close_index": 2,
            },
        )
        picked = pick_questions_for_generated_quiz(self.user, self.topic, count=20)
        self.assertTrue(picked)
        self.assertTrue(
            all(q.question_type == Question.TYPE_MULTIPLE_CHOICE for q in picked)
        )

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
