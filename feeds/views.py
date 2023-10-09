import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.views.generic.base import ContextMixin

from feeds.models import Entry, Feed
from feeds.selectors import (get_all_feeds, get_entry_count,
                             get_entry_queryset, get_feed, get_next_entry,
                             get_previous_entry)
from feeds.services import mark_entry_as_read, toggle_entry_is_favorite

logger = logging.getLogger(__name__)


class BaseFeedColumnView(ContextMixin, View):
    """
    Put into context data required for "Feeds" column:
    - total number of entries in "Smart Feeds" (all, today, unread, read, favorites).
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["all_entries_count"] = get_entry_count("all")
        context["today_entries_count"] = get_entry_count("today")
        context["unread_entries_count"] = get_entry_count("unread")
        context["read_entries_count"] = get_entry_count("read")
        context["favorites_entries_count"] = get_entry_count("favorites")
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
        context["feeds"] = get_all_feeds()

        in_feed = self.request.GET.get("in_feed", None)
        if in_feed:
            context["in_feed"] = in_feed
            context["feed"] = get_feed(pk=in_feed)
        return context


class FeedListView(BaseFeedColumnView, ListView):
    """
    Represents first column of the UI - "Feeds".
    """

    model = Feed
    queryset = get_all_feeds()
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
        mode = self.kwargs.get("mode", None)
        queryset = get_entry_queryset(mode)

        if in_feed := self.request.GET.get("in_feed", None):
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

    model = Entry
    template_name = "feeds/layout.html"
    context_object_name = "entry"

    def get(self, request, *args, **kwargs):
        """
        Merk entry as "read" when user opens the page.
        """
        mark_entry_as_read(pk=self.get_object().pk)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        mode = self.kwargs.get("mode", "all")
        entry_queryset = get_entry_queryset(mode)

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


@require_POST
def entry_toggle_is_favorite_view(request: HttpRequest, entry_pk: int) -> HttpResponse:
    """
    Toggle Favorite status of an entry, then redirect user to the page passed in
    `redirect_url` POST parameter.

    :param HttpRequest request: HttpRequest object
    :param int entry_pk: entry where to toggle Favorite status
    """
    toggle_entry_is_favorite(pk=entry_pk)

    # noinspection PyArgumentList
    return redirect(
        request.POST.get(
            key="redirect_url",
            default=reverse_lazy(
                "feeds:entry_detail", kwargs={"pk": entry_pk, "mode": "all"}
            ),
        )
    )
