import logging
from datetime import datetime

from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.views.generic.base import ContextMixin

from feeds.models import Entry, Feed, Tag
from feeds.selectors import get_next_entry, get_previous_entry

logger = logging.getLogger(__name__)

# TODO: refactor - move to service layer
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


class BaseFeedColumnView(ContextMixin, View):
    """
    Put into context data required for "Feeds" column:
    - total number of entries in "Smart Feeds" (all, today, unread, read, favorites).
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["all_entries_count"] = MODE_QUERYSETS["all"].count()
        context["today_entries_count"] = MODE_QUERYSETS["today"].count()
        context["unread_entries_count"] = MODE_QUERYSETS["unread"].count()
        context["read_entries_count"] = MODE_QUERYSETS["read"].count()
        context["favorites_entries_count"] = MODE_QUERYSETS["favorites"].count()
        return context


class BaseEntryColumnView(ContextMixin, View):
    """
    Put into context data required for "Entries" (and "Feeds) columns:
    - "mode"    - selected "Smart Feed" (all, today, unread, read, favorites).
    - "feeds"   - all feeds query set (for "Feeds" column, because in `EntryListView` we won't
                  have it by default)
    - "in_feed" - `pk` of selected feed (if any).
    - "feed"    - instance of selecred feed (if any).
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"] = self.kwargs.get("mode", "all")
        context["feeds"] = Feed.objects.all().prefetch_related("entries")

        in_feed = self.request.GET.get("in_feed", None)
        if in_feed:
            context["in_feed"] = in_feed
            context["feed"] = Feed.objects.get(pk=in_feed)
        return context


class FeedListView(BaseFeedColumnView, ListView):
    """
    Represents first column of the UI - "Feeds".
    """

    # TODO: tests

    model = Feed
    queryset = Feed.objects.all().prefetch_related("entries")
    template_name = "feeds/layout.html"
    context_object_name = "feeds"


class EntryListView(BaseEntryColumnView, BaseFeedColumnView, ListView):
    """
    Represents two columns of the UI "Entries" and "Feeds".
    """

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
        context["entry_count"] = self.get_queryset().count()
        return context


class EntryDetailView(BaseEntryColumnView, BaseFeedColumnView, DetailView):
    """
    Represents all three columns of the UI - Entry detail view, plus "Entries" and "Feeds" columns.
    """

    # TODO: tests

    model = Entry
    template_name = "feeds/layout.html"
    context_object_name = "entry"

    def get(self, request, *args, **kwargs):
        """
        Merk entry as "read" when user opens the page.
        """
        # TODO: refactor - use service layer
        entry: Entry = self.get_object()
        entry.is_read = True
        entry.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        mode = self.kwargs.get("mode", "all")
        entry_queryset = MODE_QUERYSETS[mode]

        if context.get("feed", None):
            entry_queryset = entry_queryset.filter(feed=context.get("feed"))

        context["entry_count"] = entry_queryset.count()
        context["entries"] = entry_queryset.prefetch_related("feed")

        # Stuff specific for detailed entry view
        entry = self.get_object()
        context["previous_entry"] = get_previous_entry(
            entry=entry, queryset=entry_queryset
        )
        context["next_entry"] = get_next_entry(entry=entry, queryset=entry_queryset)
        return context


class TagListView(ListView):
    # TODO: move to `BaseFeedColumnView`

    model = Tag
    queryset = (
        Tag.objects.all()
        .annotate(num_entries=Count("entries"))
        .order_by("-num_entries")
    )
    template_name = "feeds/layout.html"
    context_object_name = "tags"


@require_POST
def entry_toggle_is_favorite_view(request: HttpRequest, entry_pk: int) -> HttpResponse:
    """
    Toggle `is_favorite` value for an entry, then redirect user to the page passed in
    `redirect_url` POST parameter.

    :param HttpRequest request: HttpRequest object
    :param int entry_pk: entry where to toggle `is_favorite` value
    """
    # TODO: refactor - use service layer
    # TODO: add test
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
