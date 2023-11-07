import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.base import ContextMixin, TemplateView

from feeds.forms import FeedCreateForm
from feeds.models import Entry, Feed
from feeds.selectors import (
    get_all_feeds,
    get_all_folders,
    get_entry_queryset,
    get_feed,
    get_next_entry,
    get_previous_entry,
    get_total_entry_count,
    get_unread_entry_count,
)
from feeds.services import (
    mark_entry_as_read,
    mark_feed_as_read,
    toggle_entry_is_favorite,
)
from feeds.tasks import parse_and_set_image_for_feed, update_feed

logger = logging.getLogger(__name__)


class BaseFeedColumnView(ContextMixin, View):
    """
    Put data required for "Feeds" column into context:
    - total number of entries in "Smart Feeds" (all, today, unread, read, favorites).
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["all_entries_count"] = get_total_entry_count(
            user=self.request.user, mode="all"
        )
        context["all_unread_count"] = get_unread_entry_count(
            user=self.request.user, mode="all"
        )
        context["today_entries_count"] = get_total_entry_count(
            user=self.request.user, mode="today"
        )
        context["today_unread_count"] = get_unread_entry_count(
            user=self.request.user, mode="today"
        )
        context["unread_entries_count"] = get_total_entry_count(
            user=self.request.user, mode="unread"
        )
        context["read_entries_count"] = get_total_entry_count(
            user=self.request.user, mode="read"
        )
        context["favorites_entries_count"] = get_total_entry_count(
            user=self.request.user, mode="favorites"
        )
        return context


class BaseEntryColumnView(ContextMixin, View):
    """
    Put data required for "Entries" (and "Feeds) columns into context:
    - "mode"    - selected "Smart Feed" (all, today, unread, read, favorites).
    - "folders" - all user's folders.
    - "feeds"   - all feeds query set (for "Feeds" column, because in `EntryListView` we won't
                  have it by default)
    - "in_feed" - `pk` of selected feed (if any).
    - "feed"    - instance of selecred feed (if any).
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"] = self.kwargs.get("mode", "all")
        context["folders"] = get_all_folders(user=self.request.user)
        context["feeds"] = get_all_feeds(user=self.request.user)

        in_feed = self.request.GET.get("in_feed", None)
        if in_feed:
            context["in_feed"] = in_feed
            context["feed"] = get_feed(pk=in_feed)
        return context


class FeedListView(LoginRequiredMixin, BaseFeedColumnView, ListView):
    """
    Represents first column of the UI - "Feeds".
    """

    model = Feed
    template_name = "feeds/layout.html"
    context_object_name = "feeds"

    def get_queryset(self):
        return get_all_feeds(user=self.request.user)


class EntryListView(
    LoginRequiredMixin, BaseEntryColumnView, BaseFeedColumnView, ListView
):
    """
    Represents two columns of the UI "Entries" and "Feeds".
    """

    paginate_by = 100
    model = Entry
    template_name = "feeds/layout.html"
    context_object_name = "entries"

    def get_queryset(self):
        mode = self.kwargs.get("mode", None)
        queryset = get_entry_queryset(user=self.request.user, mode=mode)

        if in_feed := self.request.GET.get("in_feed", None):
            queryset = queryset.filter(feed=in_feed)

        return queryset.select_related("feed").prefetch_related("tags")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # NB: `all()` is workaround for queryset caching
        context["entry_count"] = self.get_queryset().all().count()
        return context


class EntryDetailView(
    LoginRequiredMixin, BaseEntryColumnView, BaseFeedColumnView, DetailView
):
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
        entry_queryset = get_entry_queryset(user=self.request.user, mode=mode)

        if context.get("feed", None):
            entry_queryset = entry_queryset.filter(feed=context.get("feed"))

        # NB: `all()` is workaround for queryset caching
        context["entry_count"] = entry_queryset.all().count()
        context["entries"] = entry_queryset.prefetch_related("feed")

        # Stuff specific for detailed entry view
        entry = self.get_object()
        context["previous_entry"] = get_previous_entry(
            user=self.request.user, entry=entry, queryset=entry_queryset
        )
        context["next_entry"] = get_next_entry(
            user=self.request.user, entry=entry, queryset=entry_queryset
        )
        return context


@login_required
def entry_export_favorites(request: HttpRequest) -> HttpResponse:
    """
    Export user's favorite entries as Markdown file.
    """
    response = HttpResponse(content_type="text/plain")
    response["Content-Disposition"] = "attachment; filename=favorites.md"

    lines = ["# Your favorite entries from RSS feeds\n\n"]

    for entry in get_entry_queryset(user=request.user, mode="favorites"):
        lines.append(
            "- [{title}]({url}) in [{feed_title}]({site_url}) on {pub_date}\n".format(
                title=entry.title,
                url=entry.url,
                feed_title=entry.feed.title,
                site_url=entry.feed.site_url,
                pub_date=entry.pub_date.strftime("%d.%m.%Y"),
            )
        )

    lines.append("\nCreated by [rss.hazadus.ru](https://rss.hazadus.ru/)")
    response.writelines(lines)
    return response


@login_required
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


@login_required
@require_POST
def feed_mark_as_read_view(request: HttpRequest, feed_pk: int) -> HttpResponse:
    """
    Mark all entries in the feed as read.

    :param HttpRequest request: HttpRequest object
    :param int feed_pk: primary key of the Feed where to mark entries as read
    """
    mark_feed_as_read(feed_pk=feed_pk)

    # noinspection PyArgumentList
    return redirect(
        request.POST.get(
            key="redirect_url",
            default=reverse_lazy("feeds:entry_list", kwargs={"mode": "all"})
            + "?in_feed="
            + str(feed_pk),
        )
    )


class FeedsSettingsView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Settings page - "Feeds" tab - "Add New Feed" form and "Manage Feeds" list.
    """

    model = Feed
    form_class = FeedCreateForm
    template_name = "layout_settings.html"
    success_message = "New feed was successfully created."

    def get_form(self, form_class=None):
        """
        Pass `request` object to the form instance.
        """
        return FeedCreateForm(self.request.POST, request=self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["feeds"] = get_all_feeds(user=self.request.user)
        context["folders"] = get_all_folders(user=self.request.user)
        return context

    def form_valid(self, form):
        """
        Set logged in user as `user` of new Feed.
        """
        feed = form.save(commit=False)
        # Associate new Feed with logged in user:
        feed.user = self.request.user
        feed.save()

        parse_and_set_image_for_feed.delay(feed.pk)
        update_feed.delay(feed.pk)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("feeds:settings_feeds")


class FeedUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView
):
    """
    Update individual Feed.
    """

    model = Feed
    fields = ["url", "title", "site_url", "image_url", "folder"]
    template_name = "layout_settings.html"
    context_object_name = "feed"
    success_message = "Feed successfully updated!"

    def test_func(self):
        """Only allow owner of the feed to update it."""
        feed = self.get_object()
        return feed.user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["folders"] = get_all_folders(user=self.request.user)
        return context

    def get_success_url(self):
        return reverse_lazy("feeds:update_feed", kwargs={"pk": self.get_object().pk})


class FeedDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Feed
    template_name = "layout_settings.html"
    context_object_name = "feed"
    success_url = reverse_lazy("feeds:settings_feeds")

    def test_func(self):
        """Only allow owner of the feed to delete it."""
        feed = self.get_object()
        return feed.user == self.request.user


class FoldersSettingsView(LoginRequiredMixin, TemplateView):
    """
    Settings page - "Folders" tab.
    """

    template_name = "layout_settings.html"
