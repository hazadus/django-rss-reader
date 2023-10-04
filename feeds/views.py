from datetime import datetime

from django.db.models import Count
from django.views.generic import DetailView, ListView

from feeds.models import Entry, Tag, Feed
from feeds.selectors import get_next_entry, get_previous_entry

MODE_QUERYSETS = {
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
        mode = self.kwargs.get("mode", None)

        if mode in MODE_QUERYSETS.keys():
            queryset = MODE_QUERYSETS.get(mode)

        return queryset.select_related("feed").prefetch_related("tags")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"] = self.kwargs.get("mode", "all")
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
        mode = self.kwargs.get("mode", "all")

        if mode not in MODE_QUERYSETS.keys():
            mode = "all"

        context["mode"] = mode
        context["previous_entry"] = get_previous_entry(
            entry=entry, queryset=MODE_QUERYSETS[mode]
        )
        context["next_entry"] = get_next_entry(
            entry=entry, queryset=MODE_QUERYSETS[mode]
        )
        return context


class TagListView(ListView):
    model = Tag
    queryset = (
        Tag.objects.all()
        .annotate(num_entries=Count("entries"))
        .order_by("-num_entries")
    )
    template_name = "feeds/tag_list.html"
    context_object_name = "tags"


class FeedListView(ListView):
    model = Feed
    queryset = Feed.objects.all().prefetch_related("entries")
    template_name = "feeds/feed_list.html"
    context_object_name = "feeds"