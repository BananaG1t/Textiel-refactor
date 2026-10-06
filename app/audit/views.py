from django.shortcuts import render
from .models import AuditLog
from common.views import FilteredListView
from .forms import AuditLogFilterForm

# Create your views here.
class AuditLogListView(FilteredListView):
    model = AuditLog
    template_name = "logs.html"
    context_object_name = "logs"

    filter_form_class = AuditLogFilterForm

    search_fields = (
        "message",
        "action",
    )

    filter_map = {
        "user": "user_id",
    }