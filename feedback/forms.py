from django import forms


class ErrorReportForm(forms.Form):
    description = forms.CharField(
        label="Descriere",
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "Descrie ce nu a funcționat și ce încercai să faci...",
                "aria-label": "Descriere problemă",
            }
        ),
        min_length=10,
        max_length=5000,
    )
    email = forms.EmailField(
        label="Email (opțional)",
        required=False,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "email@exemplu.ro",
                "aria-label": "Email pentru răspuns",
            }
        ),
    )
    page_url = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        max_length=500,
    )

    def __init__(self, *args, require_email=False, **kwargs):
        self.require_email = require_email
        super().__init__(*args, **kwargs)
        if require_email:
            self.fields["email"].widget.attrs["placeholder"] = "email@exemplu.ro (obligatoriu)"

    def clean(self):
        cleaned_data = super().clean()
        if self.require_email and not cleaned_data.get("email"):
            self.add_error("email", "Adaugă un email ca să te putem contacta.")
        return cleaned_data
