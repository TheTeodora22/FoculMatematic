from django import forms
from django.template.loader import render_to_string
from django.test import SimpleTestCase


class FormComponentTests(SimpleTestCase):
    class ExampleForm(forms.Form):
        username = forms.CharField(label="Nume utilizator", help_text="Numele contului")
        password = forms.CharField(widget=forms.PasswordInput, label="Parolă")

    def test_field_has_visible_label_help_and_client_error_target(self):
        form = self.ExampleForm()
        html = render_to_string("includes/form_field.html", {"field": form["username"]})
        self.assertIn('for="id_username"', html)
        self.assertIn('id="id_username_help"', html)
        self.assertIn('id="id_username_client_error"', html)
        self.assertNotIn("has-error", html)

    def test_server_errors_remain_visible_without_javascript(self):
        form = self.ExampleForm(data={})
        html = render_to_string("includes/form_field.html", {"field": form["username"]})
        self.assertIn("has-error", html)
        self.assertIn('id="id_username_errors"', html)
        self.assertIn(str(form["username"].errors[0]), html)

    def test_password_toggle_is_a_non_submit_button_with_controls(self):
        form = self.ExampleForm()
        html = render_to_string("includes/form_field.html", {"field": form["password"], "password": True})
        self.assertIn('type="button"', html)
        self.assertIn('aria-controls="id_password"', html)
        self.assertIn('aria-pressed="false"', html)

    def test_modified_templates_compile(self):
        from django.template.loader import get_template
        for name in ("base.html", "accounts/profile_edit.html", "registration/login.html",
                     "registration/register.html", "feedback/report.html"):
            with self.subTest(template=name):
                get_template(name)

    def test_notification_has_status_and_a_dismiss_button(self):
        from django.contrib.auth.models import AnonymousUser
        from django.contrib.messages.storage.base import Message
        from django.contrib.messages import constants
        html = render_to_string("base.html", {
            "messages": [Message(constants.SUCCESS, "Salvat")],
            "user": AnonymousUser(), "feedback_report_url": "/feedback/raporteaza/",
        })
        self.assertIn('data-dismissible role="status"', html)
        self.assertIn('aria-label="Închide mesajul"', html)

    def test_register_uses_shared_fields_and_status_outside_form(self):
        from django.contrib.auth.models import AnonymousUser
        from accounts.forms import RegisterForm
        html = render_to_string("registration/register.html", {
            "form": RegisterForm(), "user": AnonymousUser(), "csrf_token": "test-token",
            "feedback_report_url": "/feedback/raporteaza/",
        })
        for name in ("first_name", "last_name", "username", "password1", "password2"):
            self.assertIn(f'for="id_{name}"', html)
        self.assertLess(html.index("</form>"), html.index(' id="form-submit-status"'))
