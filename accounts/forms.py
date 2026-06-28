from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.core.exceptions import ValidationError

from .avatars import AVATAR_CHOICES
from .models import Profile

# Clase școlare (1–12) pentru profil
SCHOOL_CLASS_CHOICES = [(i, f"Clasa a {i}-a") for i in range(1, 13)]

_AUTH_INPUT_CLASS = "auth-portal__input"


def _widget_attrs(autocomplete: str) -> dict:
    return {"class": _AUTH_INPUT_CLASS, "autocomplete": autocomplete}


class FMAuthenticationForm(AuthenticationForm):
    """Conectare cu aceleași reguli Django; câmpuri etichetate în română."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nume utilizator"
        self.fields["password"].label = "Parolă"
        self.fields["username"].widget.attrs.update(_widget_attrs("username"))
        self.fields["password"].widget.attrs.update(_widget_attrs("current-password"))


class FMRegisterForm(UserCreationForm):
    """Cont nou: username, e-mail opțional unic, parolă cu validatorii din settings."""

    email = forms.EmailField(
        label="E-mail (opțional)",
        required=False,
        widget=forms.EmailInput(attrs=_widget_attrs("email")),
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nume utilizator"
        self.fields["username"].help_text = ""
        self.fields["username"].widget.attrs.update(_widget_attrs("username"))
        self.fields["password1"].widget.attrs.update(_widget_attrs("new-password"))
        self.fields["password2"].widget.attrs.update(_widget_attrs("new-password"))
        self.fields["password1"].label = "Parolă"
        self.fields["password2"].label = "Confirmă parola"

    def clean_username(self):
        name = (self.cleaned_data.get("username") or "").strip()
        if len(name) < 3:
            raise ValidationError("Numele de utilizator trebuie să aibă cel puțin 3 caractere.")
        if (
            get_user_model()
            .objects.filter(username__iexact=name)
            .exists()
        ):
            raise ValidationError("Acest nume de utilizator este deja folosit.")
        return name

    def clean_email(self):
        raw = (self.cleaned_data.get("email") or "").strip()
        if not raw:
            return ""
        if get_user_model().objects.filter(email__iexact=raw).exists():
            raise ValidationError(
                "Această adresă de e-mail este deja folosită de alt cont."
            )
        return raw

    def save(self, commit=True):
        user = super().save(commit=False)
        raw_email = (self.cleaned_data.get("email") or "").strip()
        user.email = raw_email if raw_email else None
        if commit:
            user.save()
            self.save_m2m()
        return user


class ProfileEditForm(forms.Form):
    """Editare: username, email (unic dacă e completat), clasă, avatar."""

    username = forms.CharField(
        label="Nume utilizator",
        max_length=150,
        help_text="",
    )
    email = forms.EmailField(
        label="E-mail",
        required=False,
        help_text="",
    )
    clasa = forms.TypedChoiceField(
        label="Clasa ta",
        coerce=int,
        choices=SCHOOL_CLASS_CHOICES,
    )
    avatar = forms.ChoiceField(
        label="Avatar",
        choices=AVATAR_CHOICES,
        widget=forms.HiddenInput(),
    )

    def __init__(self, user, profile, *args, **kwargs):
        self.user = user
        self.profile = profile
        super().__init__(*args, **kwargs)
        self.fields["username"].initial = user.username
        self.fields["email"].initial = user.email or ""
        self.fields["clasa"].initial = profile.clasa
        self.fields["avatar"].initial = profile.avatar

    def clean_username(self):
        name = self.cleaned_data["username"].strip()
        if not name:
            raise ValidationError("Introdu un nume de utilizator.")
        if (
            get_user_model()
            .objects.exclude(pk=self.user.pk)
            .filter(username__iexact=name)
            .exists()
        ):
            raise ValidationError("Acest nume de utilizator este deja folosit.")
        return name

    def clean_email(self):
        raw = (self.cleaned_data.get("email") or "").strip()
        if not raw:
            return ""
        if (
            get_user_model()
            .objects.exclude(pk=self.user.pk)
            .filter(email__iexact=raw)
            .exists()
        ):
            raise ValidationError(
                "Această adresă de e-mail este deja folosită de alt cont."
            )
        return raw

    def save(self):
        self.user.username = self.cleaned_data["username"]
        raw_email = self.cleaned_data["email"]
        self.user.email = raw_email if raw_email else None
        self.user.save(update_fields=["username", "email"])
        self.profile.clasa = self.cleaned_data["clasa"]
        self.profile.avatar = self.cleaned_data["avatar"]
        self.profile.save(update_fields=["clasa", "avatar"])
        return self.user


class ProfileThemeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("theme",)
        labels = {"theme": "Temă"}
        help_texts = {"theme": ""}
        widgets = {
            "theme": forms.HiddenInput(),
        }


class FMPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "Parola curentă"
        self.fields["new_password1"].label = "Parola nouă"
        self.fields["new_password2"].label = "Confirmă parola nouă"
