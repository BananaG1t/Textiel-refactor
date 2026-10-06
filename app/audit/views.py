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
        "level": "level",
        "email": "user__email__icontains",
        "object_id": "object_id",
    }

def log_details(request, pk):
    log = AuditLog.objects.get(pk=pk)
    return render(request, "log_details.html", {"log": log})