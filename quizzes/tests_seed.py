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

    def test_true_false_format_is_persisted(self):
        path = self._write("true_false.json", {"title": "Adevărat sau fals", "difficulty": "easy", "questions": [{
            "text": "12 : 3 = 4.", "format": "true_false", "options": [
                {"text": "Adevărat", "is_correct": True}, {"text": "Fals", "is_correct": False}
            ]
        }]})
        quiz, _ = load_quiz_file(path)
        self.assertEqual(quiz.questions.get().format_tag, Question.FORMAT_TRUE_FALSE)

    def test_load_parentheses_drag_question(self):
        path = self._write(
            "interactive.json",
            {
                "title": "Interactiv",
                "difficulty": "easy",
                "questions": [
                    {
                        "text": "Pune parantezele.",
                        "type": "parentheses_drag",
                        "interactive": {
                            "tokens": ["36", "+ 64", "+ 20"],
                            "correct_open_index": 0,
                            "correct_close_index": 2,
                        },
                    }
                ],
            },
        )
        quiz, _ = load_quiz_file(path)
        question = quiz.questions.get()
        self.assertEqual(question.question_type, Question.TYPE_PARENTHESES_DRAG)
        self.assertEqual(question.options.count(), 0)
        self.assertEqual(question.interactive_data["correct_close_index"], 2)

    def test_loads_all_subtraction_interactive_question_types(self):
        path = self._write(
            "subtraction_interactive.json",
            {
                "title": "Scădere interactivă",
                "difficulty": "medium",
                "questions": [
                    {
                        "text": "Calculează în coloană.",
                        "type": "column_subtraction",
                        "interactive": {
                            "minuend": "8642",
                            "subtrahend": "3217",
                            "correct_result": "5425",
                            "borrow_columns": [False, False, False, True],
                        },
                    },
                    {
                        "text": "Completează cifrele lipsă.",
                        "type": "missing_digits",
                        "interactive": {
                            "minuend": "734",
                            "subtrahend": "269",
                            "result": "465",
                            "missing": ["minuend:1", "subtrahend:1"],
                        },
                    },
                    {
                        "text": "Găsește coloana greșită.",
                        "type": "error_spotting",
                        "interactive": {
                            "minuend": "5032",
                            "subtrahend": "1876",
                            "shown_result": "3256",
                            "correct_result": "3156",
                            "error_column": 1,
                        },
                    },
                    {
                        "text": "Pune parantezele pentru a obține 40.",
                        "type": "parentheses_target",
                        "interactive": {
                            "tokens": ["80", "− 30", "+ 10"],
                            "correct_open_index": 1,
                            "correct_close_index": 3,
                            "target": 40,
                        },
                    },
                    {
                        "text": "Completează mașina.",
                        "type": "input_output",
                        "interactive": {
                            "operation": "subtract",
                            "value": 275,
                            "rows": [
                                {"input": 1200, "output": None},
                                {"input": None, "output": 625},
                            ],
                        },
                    },
                ],
            },
        )

        quiz, _ = load_quiz_file(path)
        self.assertEqual(quiz.questions.count(), 5)
        self.assertEqual(AnswerOption.objects.filter(question__quiz=quiz).count(), 0)
        self.assertSetEqual(
            set(quiz.questions.values_list("question_type", flat=True)),
            {
                Question.TYPE_COLUMN_SUBTRACTION,
                Question.TYPE_MISSING_DIGITS,
                Question.TYPE_ERROR_SPOTTING,
                Question.TYPE_PARENTHESES_TARGET,
                Question.TYPE_INPUT_OUTPUT,
            },
        )

    def test_loads_addition_interactive_question_types(self):
        path = self._write(
            "addition_interactive.json",
            {
                "title": "Adunare interactivă",
                "difficulty": "easy",
                "questions": [
                    {
                        "text": "Adună în coloană.",
                        "type": "column_addition",
                        "interactive": {
                            "addend1": "468",
                            "addend2": "357",
                            "correct_result": "825",
                            "carry_columns": [True, True, False],
                        },
                    },
                    {
                        "text": "Completează adunarea.",
                        "type": "missing_digits",
                        "interactive": {
                            "operation": "add",
                            "addend1": "357",
                            "addend2": "245",
                            "result": "602",
                            "missing": ["addend1:1", "addend2:1"],
                        },
                    },
                    {
                        "text": "Găsește greșeala din adunare.",
                        "type": "error_spotting",
                        "interactive": {
                            "operation": "add",
                            "addend1": "468",
                            "addend2": "357",
                            "shown_result": "815",
                            "correct_result": "825",
                            "error_column": 1,
                        },
                    },
                    {
                        "text": "Completează mașina de adunare.",
                        "type": "input_output",
                        "interactive": {
                            "operation": "add",
                            "value": 125,
                            "rows": [
                                {"input": 775, "output": None},
                                {"input": None, "output": 900},
                            ],
                        },
                    },
                ],
            },
        )
        quiz, _ = load_quiz_file(path)
        self.assertEqual(quiz.questions.count(), 4)
        self.assertEqual(AnswerOption.objects.filter(question__quiz=quiz).count(), 0)

    def test_loads_all_unit_reduction_factory_modes_with_format_tags(self):
        from data.quizzes.generators import unit_reduction_factory as factory

        exercises = [
            factory.visual_scale("Scalare", 8, 24, 5, "kg", "🍎", "8 kg costă 24 lei, deci 5 kg costă 15 lei."),
            factory.unit_path("Drum", 8, 24, 5, "lei", "Trecem prin valoarea unei unități."),
            factory.balance("Balanță", 6, 3, 9, factory.INVERSE, ["robinete", "ore"], "Produsul rămâne 18."),
            factory.basket("Coș", 3, 5, "📘", "lei", "5 caiete costă 15 lei."),
            factory.faucets("Robinete", 6, 3, 9, "🚰", "9 robinete umplu piscina în 2 ore."),
            factory.dependency_direction("Sens", "mai multe robinete", "mai puțin timp", factory.INVERSE, "Mărimile variază în sensuri opuse."),
            factory.unit_table("Tabel", [{"cantitate": 8, "valoare": 24, "missing": "valoare"}, {"cantitate": 1, "valoare": 3, "missing": "cantitate"}], ["cantitate", "valoare"], "Completăm prin unitate."),
            factory.operation_drop("Operații", ["8 kg", "1 kg", "5 kg"], [": 8", "× 5"], ["× 8", ": 5"], "Operațiile corecte sunt împărțire, apoi înmulțire."),
            factory.timeline("Bandă", 1, 12, 1, 6, "12 muncitori", "6 muncitori", "Timpul corect este 6 zile."),
            factory.problem_builder("Construiește", ["mere", "robinete"], ["Cât costă?", "În cât timp?"], ["direct", "invers"], [0, 0, 0], "Alegem piesele compatibile."),
            factory.speed_simulator("Viteză", 50, 300, 10, "🐟", "300 : 50 = 6 secunde."),
            factory.triple_match("Potrivește", [{"problem": "P1", "scheme": "S1", "answer": "R1"}, {"problem": "P2", "scheme": "S2", "answer": "R2"}, {"problem": "P3", "scheme": "S3", "answer": "R3"}], "Potrivim fiecare problemă cu schema și răspunsul ei."),
            factory.visual_true_false("Adevărat sau fals", "Mai multe robinete înseamnă mai puțin timp.", True, "🚰", "Bazinul se umple mai repede.", "Afirmația este adevărată."),
        ]
        path = self._write("unit_reduction.json", {"title": "Reducerea la unitate", "difficulty": "easy", "questions": exercises})
        quiz, _ = load_quiz_file(path)

        self.assertEqual(quiz.questions.count(), 13)
        self.assertSetEqual(set(quiz.questions.values_list("question_type", flat=True)), {Question.TYPE_UNIT_REDUCTION})
        self.assertEqual(quiz.questions.filter(format_tag=Question.FORMAT_INTERACTIVE).count(), 12)
        self.assertEqual(quiz.questions.filter(format_tag=Question.FORMAT_TRUE_FALSE).count(), 1)

    def test_loads_factor_common_interactive_types(self):
        path = self._write(
            "factor_common_interactive.json",
            {
                "title": "Factor comun interactiv",
                "difficulty": "medium",
                "questions": [
                    {
                        "text": "Construiește factorizarea.",
                        "type": "factor_builder",
                        "interactive": {
                            "expression": "3 · 45 + 3 · 15",
                            "common_factor": 3,
                            "inner_terms": [45, 15],
                            "operators": ["+"],
                            "result": 180,
                        },
                    },
                    {
                        "text": "Găsește pasul greșit.",
                        "type": "factor_error",
                        "interactive": {
                            "steps": ["28 · 7 + 28 · 12", "= 28 · 19", "= 512"],
                            "error_index": 2,
                        },
                    },
                    {
                        "text": "Potrivește expresiile.",
                        "type": "factor_match",
                        "interactive": {
                            "pairs": [
                                {"left": "7·2+7·3", "right": "7·(2+3)"},
                                {"left": "8·9−8", "right": "8·(9−1)"},
                                {"left": "4·5+4·5", "right": "4·(5+5)"},
                            ],
                            "right_order": [2, 0, 1],
                        },
                    },
                ],
            },
        )
        quiz, _ = load_quiz_file(path)
        self.assertEqual(quiz.questions.count(), 3)
        self.assertEqual(AnswerOption.objects.filter(question__quiz=quiz).count(), 0)

    def test_loads_multiplication_interactive_question_types(self):
        path = self._write(
            "multiplication_interactive.json",
            {
                "title": "Înmulțire interactivă",
                "difficulty": "easy",
                "questions": [
                    {
                        "text": "Înmulțește în coloană.",
                        "type": "column_multiplication",
                        "interactive": {
                            "multiplicand": "128",
                            "multiplier": "4",
                            "correct_result": "512",
                            "carry_columns": [True, True, False],
                        },
                    },
                    {
                        "text": "Completează cifrele.",
                        "type": "missing_digits",
                        "interactive": {
                            "operation": "multiply",
                            "factor1": "128",
                            "factor2": "004",
                            "result": "512",
                            "missing": ["factor1:1", "result:1"],
                        },
                    },
                    {
                        "text": "Găsește greșeala.",
                        "type": "error_spotting",
                        "interactive": {
                            "operation": "multiply",
                            "factor1": "128",
                            "factor2": "004",
                            "shown_result": "502",
                            "correct_result": "512",
                            "error_column": 1,
                        },
                    },
                    {
                        "text": "Completează mașina.",
                        "type": "input_output",
                        "interactive": {
                            "operation": "multiply",
                            "value": 3,
                            "rows": [
                                {"input": 12, "output": None},
                                {"input": None, "output": 45},
                            ],
                        },
                    },
                ],
            },
        )
        quiz, _ = load_quiz_file(path)
        self.assertEqual(quiz.questions.count(), 4)
        self.assertEqual(AnswerOption.objects.filter(question__quiz=quiz).count(), 0)
