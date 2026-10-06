from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView
from django.db.models import Q
from .forms import PaginationForm


def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render(request=request))

def settings(request):
    template = loader.get_template('settings.html')
    return HttpResponse(template.render(request=request))

class FilteredListView(ListView):
    filter_form_class = None
    scope_func = None

    pagination_form_class = PaginationForm
    paginate_by = 50
    pagination_options = (25, 50, 100, 200)

    search_fields = ()
    filter_map = {}

    def get_filter_form(self):
        if self.filter_form_class:
            return self.filter_form_class(self.request.GET)

        return None

    def get_pagination_form(self):
        return self.pagination_form_class(
            self.request.GET,
            options=self.pagination_options,
        )

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.scope_func:
            queryset = self.scope_func(queryset, self.request.user)

        form = self.get_filter_form()

        if form and form.is_valid():
            queryset = self.filter_queryset(
                queryset,
                form.cleaned_data,
            )

        return queryset

    def filter_queryset(self, queryset, data):
        search = data.get("search")

        if search and self.search_fields:
            search_query = Q()

            for field in self.search_fields:
                search_query |= Q(**{f"{field}__icontains": search})

            queryset = queryset.filter(search_query)

        for field, value in data.items():
            if field == "search" or value in (None, ""):
                continue

            lookup = self.filter_map.get(field, f"{field}__icontains")

            queryset = queryset.filter(
                **{lookup: value}
            )

        return queryset

    def get_paginate_by(self, queryset):
        form = self.get_pagination_form()

        if form.is_valid():
            return form.cleaned_data["per_page"] or self.paginate_by

        return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["filter_form"] = self.get_filter_form()
        context["pagination_form"] = self.get_pagination_form()

        return context