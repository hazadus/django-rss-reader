from django.urls import reverse

from feeds.models import Entry, Feed

from .base_test_case import BaseFeedsViewsTestCase


class EntryDetailViewTest(BaseFeedsViewsTestCase):
    """
    Test "feeds:entry_list" view with various options.
    """

    def test_entry_detail_view_marks_as_read(self):
        """
        Test that when user opens entry detail view the entry's `is_read` is set to `True`.
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        # Do the actual test
        entry = Entry.objects.all().first()
        entry.is_read = False
        entry.save()
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

        # Login
        url = reverse("account_login")
        response = self.client.post(
            url,
            {"login": self.email, "password": self.password},
            follow=True,
        )

        # Do the actual test
        for mode in self.MODE_QUERYSETS.keys():
            for entry in self.MODE_QUERYSETS[mode]:
                url = reverse(
                    "feeds:entry_detail", kwargs={"mode": mode, "pk": entry.pk}
                )
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["mode"], mode)
                self.assertEqual(
                    response.context["entry_count"],
                    self.MODE_QUERYSETS[mode].count(),
                )
                self.assertEqual(
                    len(response.context["feeds"]),
                    Feed.objects.filter(user=self.user).count(),
                )
                self.assertEqual(
                    response.context["all_entries_count"],
                    self.MODE_QUERYSETS["all"].count(),
                )
                self.assertEqual(
                    response.context["today_entries_count"],
                    self.MODE_QUERYSETS["today"].count(),
                )
                self.assertEqual(
                    response.context["unread_entries_count"],
                    self.MODE_QUERYSETS["unread"].count(),
                )
                self.assertEqual(
                    response.context["read_entries_count"],
                    self.MODE_QUERYSETS["read"].count(),
                )
                self.assertEqual(
                    response.context["favorites_entries_count"],
                    self.MODE_QUERYSETS["favorites"].count(),
                )

    def test_entry_detail_view_context_data_in_each_feed(self):
        """
        Test that correct context data is passed to each entry detail view in each feed.
        Slow test, but we need to ensure correct context data.
        """
        mode = "all"

        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        # Do the actual test
        for feed in Feed.objects.all():
            for entry in feed.entries.all():
                url = reverse(
                    "feeds:entry_detail", kwargs={"mode": mode, "pk": entry.pk}
                )
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["mode"], mode)
                self.assertEqual(
                    response.context["entry_count"],
                    self.MODE_QUERYSETS[mode].count(),
                )
                self.assertEqual(
                    len(response.context["feeds"]),
                    Feed.objects.filter(user=self.user).count(),
                )
                self.assertEqual(
                    response.context["all_entries_count"],
                    self.MODE_QUERYSETS["all"].count(),
                )
                self.assertEqual(
                    response.context["today_entries_count"],
                    self.MODE_QUERYSETS["today"].count(),
                )
                self.assertEqual(
                    response.context["unread_entries_count"],
                    # NB: `all()` is workaround for queryset caching
                    self.MODE_QUERYSETS["unread"].all().count(),
                )
                self.assertEqual(
                    response.context["read_entries_count"],
                    # NB: `all()` is workaround for queryset caching
                    self.MODE_QUERYSETS["read"].all().count(),
                )
                self.assertEqual(
                    response.context["favorites_entries_count"],
                    self.MODE_QUERYSETS["favorites"].count(),
                )
