from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

from .models import Profile


class UsernameChangeForm(forms.Form):
    username = forms.CharField(
        label="Nume utilizator",
        max_length=150,
        help_text="Litere, cifre și @ . + - _",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["username"].initial = user.username

    def clean_username(self):
        name = self.cleaned_data["username"].strip()
        if (
            User.objects.exclude(pk=self.user.pk)
            .filter(username__iexact=name)
            .exists()
        ):
            raise forms.ValidationError("Acest nume de utilizator este deja folosit.")
        return name

    def save(self):
        self.user.username = self.cleaned_data["username"]
        self.user.save(update_fields=["username"])
        return self.user


class ProfileThemeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("theme",)
        labels = {"theme": "Aspect"}
        help_texts = {
            "theme": "„La fel ca sistemul” urmărește setarea dispozitivului (luminos/întunecat).",
        }
        widgets = {
            "theme": forms.HiddenInput(),
        }


class FMPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "Parola curentă"
        self.fields["new_password1"].label = "Parola nouă"
        self.fields["new_password2"].label = "Confirmă parola nouă"
