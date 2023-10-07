import logging
from datetime import datetime

from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from feeds.models import Entry, Feed, Tag
from feeds.selectors import get_next_entry, get_previous_entry

logger = logging.getLogger(__name__)

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
    template_name = "feeds/layout.html"
    context_object_name = "entries"

    def get_queryset(self):
        queryset = Entry.objects.all()
        mode = self.kwargs.get("mode", None)
        in_feed = self.request.GET.get("in_feed", None)

        if mode in MODE_QUERYSETS.keys():
            queryset = MODE_QUERYSETS.get(mode)

        if in_feed:
            queryset = queryset.filter(feed=in_feed)

        return queryset.select_related("feed").prefetch_related("tags")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"] = self.kwargs.get("mode", "all")
        context["entry_count"] = self.get_queryset().count()
        context["feeds"] = Feed.objects.all()

        context["all_entries_count"] = MODE_QUERYSETS["all"].count()
        context["today_entries_count"] = MODE_QUERYSETS["today"].count()
        context["unread_entries_count"] = MODE_QUERYSETS["unread"].count()
        context["read_entries_count"] = MODE_QUERYSETS["read"].count()
        context["favorites_entries_count"] = MODE_QUERYSETS["favorites"].count()

        in_feed = self.request.GET.get("in_feed", None)
        if in_feed:
            context["in_feed"] = in_feed
            context["feed"] = Feed.objects.get(pk=in_feed)
        return context


class EntryDetailView(DetailView):
    model = Entry
    template_name = "feeds/layout.html"
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
        mode = self.kwargs.get("mode", "all")
        in_feed = self.request.GET.get("in_feed", None)

        if mode not in MODE_QUERYSETS.keys():
            mode = "all"

        entry_queryset = MODE_QUERYSETS[mode]

        if in_feed:
            entry_queryset = entry_queryset.filter(feed=in_feed)
            context["in_feed"] = in_feed
            context["feed"] = Feed.objects.get(pk=in_feed)

        context["entry_count"] = entry_queryset.count()
        context["mode"] = mode

        context["all_entries_count"] = MODE_QUERYSETS["all"].count()
        context["today_entries_count"] = MODE_QUERYSETS["today"].count()
        context["unread_entries_count"] = MODE_QUERYSETS["unread"].count()
        context["read_entries_count"] = MODE_QUERYSETS["read"].count()
        context["favorites_entries_count"] = MODE_QUERYSETS["favorites"].count()

        # Specific for this view
        entry = self.get_object()
        context["previous_entry"] = get_previous_entry(
            entry=entry, queryset=entry_queryset
        )
        context["next_entry"] = get_next_entry(entry=entry, queryset=entry_queryset)
        context["feeds"] = Feed.objects.all().prefetch_related("entries")
        context["entries"] = entry_queryset.prefetch_related("feed")
        return context


class TagListView(ListView):
    model = Tag
    queryset = (
        Tag.objects.all()
        .annotate(num_entries=Count("entries"))
        .order_by("-num_entries")
    )
    template_name = "feeds/layout.html"
    context_object_name = "tags"


class FeedListView(ListView):
    model = Feed
    queryset = Feed.objects.all().prefetch_related("entries")
    template_name = "feeds/layout.html"
    context_object_name = "feeds"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["all_entries_count"] = MODE_QUERYSETS["all"].count()
        context["today_entries_count"] = MODE_QUERYSETS["today"].count()
        context["unread_entries_count"] = MODE_QUERYSETS["unread"].count()
        context["read_entries_count"] = MODE_QUERYSETS["read"].count()
        context["favorites_entries_count"] = MODE_QUERYSETS["favorites"].count()
        return context


@require_POST
def entry_toggle_is_favorite_view(request: HttpRequest, entry_pk: int) -> HttpResponse:
    """
    Toggle `is_favorite` value for an entry, then redirect user to the page passed in
    `redirect_url` POST parameter.

    :param HttpRequest request: HttpRequest object
    :param int entry_pk: entry where to toggle `is_favorite` value
    """
    entry = get_object_or_404(Entry, pk=entry_pk)
    entry.is_favorite = not entry.is_favorite
    entry.save()

    # noinspection PyArgumentList
    return redirect(
        request.POST.get(
            key="redirect_url",
            default=reverse_lazy(
                "feeds:entry_detail", kwargs={"pk": entry_pk, "mode": "all"}
            ),
        )
    )
