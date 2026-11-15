from unittest.mock import patch

import sympy as sp
from django.test import Client, TestCase
from django.urls import reverse

from .math_demo import SESSION_KEY
from .math_tools.quadratics import X, check_roots, expression, generate_quadratic


class MathDemoTests(TestCase):
    def test_generated_equations_have_two_distinct_bounded_integer_roots(self):
        for _ in range(80):
            coefficients = generate_quadratic()
            roots = sp.solve(expression(coefficients), X)
            self.assertNotEqual(coefficients[0], 0)
            self.assertEqual(len(roots), 2)
            self.assertTrue(all(root.is_Integer and -9 <= root <= 9 for root in roots))
            self.assertTrue(check_roots(coefficients, *roots))

    def test_check_requires_both_roots_and_accepts_reverse_order(self):
        self.assertTrue(check_roots([1, -4, 3], 3, 1))
        self.assertFalse(check_roots([1, -4, 3], 1, 1))
        self.assertFalse(check_roots([1, -4, 3], 1, 2))

    def start(self):
        with patch("FoculMatematic.math_demo.generate_quadratic", return_value=[1, -4, 3]):
            response = self.client.get(reverse("math_demo"))
        self.assertEqual(response.status_code, 200)
        return self.client.session[SESSION_KEY]["id"]

    def test_get_keeps_exercise_and_does_not_include_answers(self):
        exercise_id = self.start()
        response = self.client.get(reverse("math_demo"))
        self.assertEqual(self.client.session[SESSION_KEY]["id"], exercise_id)
        for key in ("roots", "solutions", "expected"):
            self.assertNotIn(key, response.context)
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, "jsxgraph@1.12.2")

    def test_correct_and_incorrect_posts(self):
        exercise_id = self.start()
        url = reverse("math_demo")
        response = self.client.post(url, {"exercise_id": exercise_id, "first": "1", "second": "2"})
        self.assertContains(response, "Răspuns incorect")
        response = self.client.post(url, {"exercise_id": exercise_id, "first": "3", "second": "1"})
        self.assertContains(response, "Corect!")

    def test_invalid_and_oversized_input_never_reaches_sympy(self):
        exercise_id = self.start()
        for value in ("__import__('os')", "x+1", "NaN", "1000", "9" * 5000):
            with patch("FoculMatematic.math_demo.check_roots") as checker:
                response = self.client.post(reverse("math_demo"), {
                    "exercise_id": exercise_id, "first": value, "second": "1"})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
                checker.assert_not_called()

    def test_old_exercise_and_other_sessions_are_rejected(self):
        exercise_id = self.start()
        self.client.post(reverse("math_demo"), {"action": "new"})
        self.client.get(reverse("math_demo"))
        response = self.client.post(reverse("math_demo"), {
            "exercise_id": exercise_id, "first": "1", "second": "3"})
        self.assertContains(response, "Exercițiul s-a schimbat")
        other = Client()
        response = other.post(reverse("math_demo"), {
            "exercise_id": exercise_id, "first": "1", "second": "3"})
        self.assertContains(response, "Exercițiul s-a schimbat")

    def test_csrf_is_enforced(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("math_demo"), {"first": "1", "second": "3"})
        self.assertEqual(response.status_code, 403)

    def test_new_equation_redirects(self):
        self.start()
        response = self.client.post(reverse("math_demo"), {"action": "new"})
        self.assertRedirects(response, reverse("math_demo"))
