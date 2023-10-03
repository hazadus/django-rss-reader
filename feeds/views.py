from datetime import datetime

from django.views.generic import DetailView, ListView

from feeds.models import Entry
from feeds.selectors import get_next_entry, get_previous_entry

VIEW_QUERYSETS = {
    "all": Entry.objects.all(),
    "today": Entry.objects.filter(
        pub_date__day=datetime.today().day,
        pub_date__month=datetime.today().month,
        pub_date__year=datetime.today().year,
    ),
    "unread": Entry.objects.filter(is_read=False),
    "read": Entry.objects.filter(is_read=True),
    "favorites": Entry.objects.filter(is_favorite=True),
}


class EntriesListView(ListView):
    paginate_by = 100
    model = Entry
    template_name = "feeds/entry_list.html"
    context_object_name = "entries"

    def get_queryset(self):
        queryset = Entry.objects.all()
        view = self.kwargs.get("view", None)

        if view in VIEW_QUERYSETS.keys():
            queryset = VIEW_QUERYSETS.get(view)

        return queryset.select_related("feed").prefetch_related("tags")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view"] = self.kwargs.get("view", "all")
        context["entry_count"] = self.get_queryset().count()
        return context


class EntryDetailView(DetailView):
    model = Entry
    template_name = "feeds/entry_detail.html"
    context_object_name = "entry"

    def get(self, request, *args, **kwargs):
        """
        Merk entry as read when user open the page.
        """
        entry: Entry = self.get_object()
        entry.is_read = True
        entry.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = self.get_object()
        view = self.kwargs.get("view", "all")

        if view not in VIEW_QUERYSETS.keys():
            view = "all"

        context["view"] = view
        context["previous_entry"] = get_previous_entry(
            entry=entry, queryset=VIEW_QUERYSETS[view]
        )
        context["next_entry"] = get_next_entry(
            entry=entry, queryset=VIEW_QUERYSETS[view]
        )
        return context
