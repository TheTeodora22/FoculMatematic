from django import forms
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.test import SimpleTestCase


class AccessibilityTests(SimpleTestCase):
    def test_errors_and_help_are_associated_without_javascript(self):
        class Example(forms.Form):
            email = forms.EmailField(help_text="Adresa contului")
        field = Example(data={})["email"]
        html = render_to_string("includes/form_field.html", {"field": field})
        self.assertIn('aria-describedby="id_email_help id_email_errors id_email_client_error"', html)
        self.assertIn('aria-invalid="true"', html)
        self.assertIn('autocomplete="email"', html)

    def test_home_has_one_main_and_static_fallback(self):
        html = render_to_string("index.html", {"user": AnonymousUser()})
        self.assertEqual(html.count("<main "), 1)
        self.assertLess(html.index("</main>"), html.index("<footer"))
        self.assertIn('id="home-title"', html)
        self.assertIn('poster="/static/core/img/FMImage.png"', html)
        self.assertIn("data-motion-toggle hidden", html)

    def test_math_form_does_not_reference_client_error_elements(self):
        from django.template import Template, Context
        class Example(forms.Form):
            value = forms.CharField()
        html = Template('{% load accessible_forms %}{% accessible_field field False %}').render(Context({"field": Example()["value"]}))
        self.assertNotIn("client_error", html)
