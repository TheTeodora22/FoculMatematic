import json
from pathlib import Path

from django.test import TestCase, override_settings

from quizzes.models import AnswerOption, Question, Quiz
from quizzes.seed_loader import SeedValidationError, load_all_quizzes, load_quiz_file


@override_settings(BASE_DIR=Path(__file__).resolve().parent.parent)
class SeedQuizzesTests(TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).resolve().parent.parent / "data" / "test_quizzes"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        for f in self.data_dir.glob("*.json"):
            f.unlink()
        if self.data_dir.exists():
            self.data_dir.rmdir()

    def _write(self, name: str, payload: dict):
        path = self.data_dir / name
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def test_load_creates_quiz(self):
        self._write(
            "test.json",
            {
                "title": "Test Seed",
                "difficulty": "easy",
                "questions": [
                    {
                        "text": "1+1?",
                        "points": 10,
                        "options": [
                            {"text": "2", "is_correct": True},
                            {"text": "3", "is_correct": False},
                        ],
                    }
                ],
            },
        )
        results = load_all_quizzes(self.data_dir)
        self.assertEqual(len(results), 1)
        quiz = Quiz.objects.get(title="Test Seed")
        self.assertEqual(quiz.questions.count(), 1)
        self.assertEqual(AnswerOption.objects.filter(question__quiz=quiz).count(), 2)

    def test_rerun_updates_without_duplicates(self):
        payload = {
            "title": "Test Idempotent",
            "difficulty": "medium",
            "questions": [
                {
                    "text": "Q1",
                    "points": 10,
                    "options": [
                        {"text": "A", "is_correct": True},
                        {"text": "B", "is_correct": False},
                    ],
                }
            ],
        }
        self._write("q.json", payload)
        load_all_quizzes(self.data_dir)
        load_all_quizzes(self.data_dir)
        self.assertEqual(Quiz.objects.filter(title="Test Idempotent").count(), 1)
        self.assertEqual(Question.objects.filter(quiz__title="Test Idempotent").count(), 1)

    def test_invalid_single_correct(self):
        self._write(
            "bad.json",
            {
                "title": "Bad",
                "difficulty": "easy",
                "questions": [
                    {
                        "text": "Q",
                        "options": [
                            {"text": "A", "is_correct": True},
                            {"text": "B", "is_correct": True},
                        ],
                    }
                ],
            },
        )
        with self.assertRaises(SeedValidationError):
            load_quiz_file(self.data_dir / "bad.json")
