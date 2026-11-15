import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth.models import User
from django.test import TestCase

from quizzes.catalog_reorganization import PROGRESSIONS_FILES, PROGRESSIONS_OLD
from quizzes.models import Quiz, Question, AnswerOption, UserQuestionProgress
from quizzes.seed_loader import load_all_quizzes, load_quiz_file, SeedValidationError


class ProgressionSplitTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.payloads = []
        for i, filename in enumerate(PROGRESSIONS_FILES):
            payload = {'title': f'Progresii {i}', 'difficulty': 'medium', 'questions': [
                {'text': f'Intrebarea {i}', 'points': 10, 'options': [
                    {'text': 'Corect', 'is_correct': True},
                    {'text': 'Gresit', 'is_correct': False}]}]}
            self.payloads.append(payload)
            (self.root / filename).write_text(json.dumps(payload), encoding='utf-8')
        manifest = [{'class_level': 9, 'slug': 'functii', 'title': 'Functii',
                     'order': 3, 'topics': PROGRESSIONS_FILES}]
        (self.root / 'chapters.json').write_text(json.dumps(manifest), encoding='utf-8')
        legacy = dict(self.payloads[0])
        legacy['questions'] = [p['questions'][0] for p in self.payloads]
        path = self.root / PROGRESSIONS_OLD
        path.write_text(json.dumps(legacy), encoding='utf-8')
        self.old, _ = load_quiz_file(path)
        path.unlink()

    def test_preserves_questions_options_progress_and_is_idempotent(self):
        ids = list(Question.objects.values_list('id', 'text'))
        options = list(AnswerOption.objects.values_list('id', 'question_id', 'text'))
        user = User.objects.create_user('split-test')
        progress = UserQuestionProgress.objects.create(user=user,
            question=Question.objects.last(), xp_awarded=True, training_status='correct')
        load_all_quizzes(self.root)
        load_all_quizzes(self.root)
        self.assertEqual(list(Question.objects.values_list('id', 'text')), ids)
        self.assertEqual(list(AnswerOption.objects.values_list('id', 'question_id', 'text')), options)
        progress.refresh_from_db()
        self.assertTrue(progress.xp_awarded)
        self.assertEqual(progress.training_status, 'correct')
        for i, filename in enumerate(PROGRESSIONS_FILES):
            quiz = Quiz.objects.get(source_file=filename)
            self.assertEqual(list(quiz.questions.values_list('text', flat=True)), [f'Intrebarea {i}'])
        self.assertEqual(Quiz.objects.get(source_file=PROGRESSIONS_FILES[0]).pk, self.old.pk)
        self.assertFalse(Quiz.objects.filter(source_file=PROGRESSIONS_OLD).exists())

    def test_unknown_question_rolls_back(self):
        Question.objects.create(quiz=self.old, text='Extra', points=10)
        with self.assertRaises(SeedValidationError):
            load_all_quizzes(self.root)
        self.old.refresh_from_db()
        self.assertEqual(self.old.source_file, PROGRESSIONS_OLD)
        self.assertEqual(self.old.questions.count(), 4)
        self.assertFalse(Quiz.objects.filter(source_file__in=PROGRESSIONS_FILES).exists())
