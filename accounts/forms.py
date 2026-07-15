from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "placeholder": "Nume utilizator",
            "aria-label": "Nume utilizator",
        })
        self.fields["password"].widget.attrs.update({
            "placeholder": "Parolă",
            "aria-label": "Parolă",
        })


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "first_name": "Prenume",
            "last_name": "Nume",
            "username": "Nume utilizator",
            "password1": "Parolă",
            "password2": "Confirmare parolă",
        }
        for name, placeholder in placeholders.items():
            self.fields[name].widget.attrs.update({
                "placeholder": placeholder,
                "aria-label": placeholder,
            })
        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("clasa", "avatar", "theme")
        labels = {
            "clasa": "Clasa",
            "avatar": "Avatar",
            "theme": "Temă",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        owned_keys = set()
        if user is not None:
            owned_keys = set(user.items.values_list("item_key", flat=True))

        avatar_choices = [("default_avatar", "Avatar implicit")]
        theme_choices = [("light", "Temă light"), ("dark_theme_1", "Temă dark")]

        for key in sorted(owned_keys):
            if "avatar" in key:
                avatar_choices.append((key, key.replace("_", " ").title()))
            elif "theme" in key:
                theme_choices.append((key, key.replace("_", " ").title()))
            else:
                avatar_choices.append((key, key.replace("_", " ").title()))

        self.fields["avatar"].widget = forms.Select(choices=avatar_choices)
        self.fields["theme"].widget = forms.Select(choices=theme_choices)
