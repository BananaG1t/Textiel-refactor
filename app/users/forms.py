from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User
from .validators import (
    validate_name,
    validate_email_address,
    validate_phone_number,
)

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "autocomplete": "email",
            "placeholder": _("you@example.com")
            ,
            "autofocus": True
        }),
    )

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": _("Your password"),
            }
        )
    )

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        validators=[validate_name],
    )

    last_name = forms.CharField(
        validators=[validate_name],
    )

    email = forms.EmailField(
        validators=[validate_email_address],
    )

    phone_number = forms.CharField(
        required=False,
        validators=[validate_phone_number],
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
        )

        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone_number": forms.TextInput(
                attrs={
                    "autocomplete": "tel",
                    "placeholder": "+31 6 12345678",
                }
            ),
        }

    def clean_first_name(self):
        value = self.cleaned_data["first_name"]
        return " ".join(
            part.capitalize()
            for part in value.strip().split()
        )

    def clean_last_name(self):
        value = self.cleaned_data["last_name"]
        return " ".join(
            part.capitalize()
            for part in value.strip().split()
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if (
            email != self.instance.email.lower()
            and User.objects.filter(email__iexact=email).exists()
        ):
            raise forms.ValidationError(
                "Dit e-mailadres is al in gebruik."
            )

        return email