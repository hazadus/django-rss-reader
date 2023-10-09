from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from feeds.models import Entry, Feed

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


class EntryDetailViewTest(TestCase):
    """
    Test "feeds:entry_list" view with various options.
    """

    fixtures = [
        "users/tests/fixtures/users.json",
        "feeds/tests/fixtures/tags.json",
        "feeds/tests/fixtures/feeds.json",
        "feeds/tests/fixtures/entries.json",
    ]

    @classmethod
    def setUpTestData(cls):
        pass

    def test_entry_detail_view_marks_as_read(self):
        """
        Test that when user opens entry detail view the entry's `is_read` is set to `True`.
        """
        entry = Entry.objects.filter(is_read=False).first()
        entry_pk = entry.pk
        url = reverse("feeds:entry_detail", kwargs={"mode": "all", "pk": entry_pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Entry.objects.get(pk=entry_pk).is_read, True)

    def test_entry_detail_view_context_data_in_smart_feeds(self):
        """
        Test that correct context data is passed to each entry detail view in each "Smart Feed".
        Slow test, but we need to ensure correct context data.
        """

        for mode in MODE_QUERYSETS.keys():
            for entry in MODE_QUERYSETS[mode]:
                url = reverse(
                    "feeds:entry_detail", kwargs={"mode": mode, "pk": entry.pk}
                )
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["mode"], mode)
                self.assertEqual(
                    response.context["entry_count"], MODE_QUERYSETS[mode].count()
                )
                self.assertEqual(
                    len(response.context["feeds"]), Feed.objects.all().count()
                )
                self.assertEqual(
                    response.context["all_entries_count"], MODE_QUERYSETS["all"].count()
                )
                self.assertEqual(
                    response.context["today_entries_count"],
                    MODE_QUERYSETS["today"].count(),
                )
                self.assertEqual(
                    response.context["unread_entries_count"],
                    MODE_QUERYSETS["unread"].count(),
                )
                self.assertEqual(
                    response.context["read_entries_count"],
                    MODE_QUERYSETS["read"].count(),
                )
                self.assertEqual(
                    response.context["favorites_entries_count"],
                    MODE_QUERYSETS["favorites"].count(),
                )

    def test_entry_detail_view_context_data_in_each_feed(self):
        """
        Test that correct context data is passed to each entry detail view in each feed.
        Slow test, but we need to ensure correct context data.
        """
        mode = "all"

        for feed in Feed.objects.all():
            for entry in feed.entries.all():
                url = reverse(
                    "feeds:entry_detail", kwargs={"mode": mode, "pk": entry.pk}
                )
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["mode"], mode)
                self.assertEqual(
                    response.context["entry_count"], MODE_QUERYSETS[mode].count()
                )
                self.assertEqual(
                    len(response.context["feeds"]), Feed.objects.all().count()
                )
                self.assertEqual(
                    response.context["all_entries_count"], MODE_QUERYSETS["all"].count()
                )
                self.assertEqual(
                    response.context["today_entries_count"],
                    MODE_QUERYSETS["today"].count(),
                )
                self.assertEqual(
                    response.context["unread_entries_count"],
                    # NB: `all()` is workaround for queryset caching
                    MODE_QUERYSETS["unread"].all().count(),
                )
                self.assertEqual(
                    response.context["read_entries_count"],
                    # NB: `all()` is workaround for queryset caching
                    MODE_QUERYSETS["read"].all().count(),
                )
                self.assertEqual(
                    response.context["favorites_entries_count"],
                    MODE_QUERYSETS["favorites"].count(),
                )
