from django import forms


class PaginationForm(forms.Form):
    per_page = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=200,
        initial=50,
    )

    def __init__(self, *args, options=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.options = options or ()