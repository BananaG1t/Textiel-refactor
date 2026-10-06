from django import forms

class AuditLogFilterForm(forms.Form):
    search = forms.CharField(required=False)
    level = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All levels"),
            ("INFO", "Info"),
            ("WARNING", "Warning"),
            ("ERROR", "Error"),
            ("CRITICAL", "Critical"),
        ],
    )
    action = forms.CharField(required=False)
    user = forms.CharField(required=False)
    object_type = forms.CharField(required=False)
    object_id = forms.CharField(required=False)