from django.views.generic import DetailView, ListView

from feeds.models import Entry
from feeds.selectors import get_next_entry, get_previous_entry


class AllEntriesListView(ListView):
    paginate_by = 100
    model = Entry
    template_name = "feeds/entry_list_all.html"
    queryset = Entry.objects.all()
    context_object_name = "entries"


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
        context["previous_entry"] = get_previous_entry(entry=entry)
        context["next_entry"] = get_next_entry(entry=entry)
        return context
