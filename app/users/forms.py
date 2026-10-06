from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User
from .validators import (
    validate_name,
    validate_email_address,
    validate_phone_number,
)
from authorization.models import Role

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

class PasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["old_password"].widget.attrs.pop("autofocus", None)

class UserFilterForm(forms.Form):

    search = forms.CharField(
        required=False,
        label=_("Search"),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Search by name or email"),
            },
        ),
    )

    id = forms.IntegerField(
        required=False,
        label=_("ID"),
    )

    role = forms.ModelChoiceField(
        required=False,
        label=_("Role"),
        queryset=Role.objects.all(),
        empty_label=_("All roles"),
    )

    is_active = forms.TypedChoiceField(
        required=False,
        label=_("Status"),
        choices=(
            ("", _("All")),
            ("true", _("Active")),
            ("false", _("Inactive")),
        ),
        coerce=lambda value: value == "true",
        initial="true"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_bound and "is_active" not in self.data:
            self.data = self.data.copy()
            self.data["is_active"] = "true"