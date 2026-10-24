import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth.models import User
from django.test import TestCase

from quizzes.catalog_reorganization import OLD_EMPTY, OLD_SOURCE
from quizzes.models import AnswerOption, Question, UserQuestionProgress, Quiz
from quizzes.seed_loader import SeedValidationError, load_all_quizzes


class RealNumberReorganizationTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "clasa_9").mkdir()
        self.old = Quiz.objects.create(title="Lecție reunită",difficulty="medium",source_file=OLD_SOURCE)
        self.empty = Quiz.objects.create(title="Intervale vechi",difficulty="easy",source_file=OLD_EMPTY)
        self.questions = []
        for text in ["Operație", "Modul"]:
            q = Question.objects.create(quiz=self.old,text=text)
            AnswerOption.objects.create(question=q,text="1",is_correct=True)
            AnswerOption.objects.create(question=q,text="2",is_correct=False)
            self.questions.append(q)
        user = User.objects.create_user(username="reorganization")
        self.progress = UserQuestionProgress.objects.create(user=user,question=self.questions[1])
        topics = []
        for i in range(1,7):
            filename = f"clasa_9/section_{i}.json"
            topics.append(filename)
            text = "Operație" if i==1 else "Modul" if i==3 else None
            payload = {"title":f"1.{i}. Subcapitol", "difficulty":"medium", "questions": []}
            if text:
                payload["questions"] = [{"text":text,"options":[{"text":"1","is_correct":True},{"text":"2","is_correct":False}]}]
            (self.root / filename).write_text(json.dumps(payload),encoding="utf-8")
        (self.root / "chapters.json").write_text(json.dumps([{
            "class_level":9,"slug":"multimea-numerelor-reale","title":"Mulțimea numerelor reale","order":1,"topics":topics,
        }]),encoding="utf-8")

    def test_preserves_questions_options_progress_and_is_idempotent(self):
        ids = set(Question.objects.values_list("pk",flat=True))
        option_ids = set(AnswerOption.objects.values_list("pk",flat=True))
        load_all_quizzes(self.root)
        self.old.refresh_from_db()
        self.empty.refresh_from_db()
        self.progress.refresh_from_db()
        self.questions[1].refresh_from_db()
        self.assertEqual(self.old.source_file,"section_1.json")
        self.assertEqual(self.empty.source_file,"section_6.json")
        self.assertEqual(self.questions[1].quiz.source_file,"section_3.json")
        self.assertEqual(self.progress.question_id,self.questions[1].pk)
        self.assertEqual(set(Question.objects.values_list("pk",flat=True)),ids)
        self.assertEqual(set(AnswerOption.objects.values_list("pk",flat=True)),option_ids)
        load_all_quizzes(self.root)
        self.assertEqual(Quiz.objects.count(),6)
        self.assertEqual(set(Question.objects.values_list("pk",flat=True)),ids)

    def test_unmapped_question_rolls_back_without_losing_data(self):
        q = Question.objects.create(quiz=self.old,text="Întrebare fără destinație")
        with self.assertRaises(SeedValidationError):
            load_all_quizzes(self.root)
        self.old.refresh_from_db()
        q.refresh_from_db()
        self.assertEqual(self.old.source_file,OLD_SOURCE)
        self.assertEqual(q.quiz_id,self.old.pk)
        self.assertEqual(Quiz.objects.count(),2)
