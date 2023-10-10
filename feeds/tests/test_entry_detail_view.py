from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from feeds.models import Entry, Feed
from users.models import CustomUser

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

    username = "anon@mail.com"
    password = "12345678"
    user = None

    fixtures = [
        "users/tests/fixtures/users.json",
        "feeds/tests/fixtures/tags.json",
        "feeds/tests/fixtures/feeds.json",
        "feeds/tests/fixtures/entries.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.get(email=cls.username)

    def test_entry_detail_view_marks_as_read(self):
        """
        Test that when user opens entry detail view the entry's `is_read` is set to `True`.
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.username, "password": self.password}, follow=True
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
            {"login": self.username, "password": self.password},
            follow=True,
        )

        # Do the actual test
        for mode in MODE_QUERYSETS.keys():
            for entry in MODE_QUERYSETS[mode]:
                url = reverse(
                    "feeds:entry_detail", kwargs={"mode": mode, "pk": entry.pk}
                )
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["mode"], mode)
                self.assertEqual(
                    response.context["entry_count"],
                    MODE_QUERYSETS[mode].filter(feed__user=self.user).count(),
                )
                self.assertEqual(
                    len(response.context["feeds"]),
                    Feed.objects.filter(user=self.user).count(),
                )
                self.assertEqual(
                    response.context["all_entries_count"],
                    MODE_QUERYSETS["all"].filter(feed__user=self.user).count(),
                )
                self.assertEqual(
                    response.context["today_entries_count"],
                    MODE_QUERYSETS["today"].filter(feed__user=self.user).count(),
                )
                self.assertEqual(
                    response.context["unread_entries_count"],
                    MODE_QUERYSETS["unread"].filter(feed__user=self.user).count(),
                )
                self.assertEqual(
                    response.context["read_entries_count"],
                    MODE_QUERYSETS["read"].filter(feed__user=self.user).count(),
                )
                self.assertEqual(
                    response.context["favorites_entries_count"],
                    MODE_QUERYSETS["favorites"].filter(feed__user=self.user).count(),
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
            url, {"login": self.username, "password": self.password}, follow=True
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
                    MODE_QUERYSETS[mode].filter(feed__user=self.user).count(),
                )
                self.assertEqual(
                    len(response.context["feeds"]),
                    Feed.objects.filter(user=self.user).count(),
                )
                self.assertEqual(
                    response.context["all_entries_count"],
                    MODE_QUERYSETS["all"].filter(feed__user=self.user).count(),
                )
                self.assertEqual(
                    response.context["today_entries_count"],
                    MODE_QUERYSETS["today"].filter(feed__user=self.user).count(),
                )
                self.assertEqual(
                    response.context["unread_entries_count"],
                    # NB: `all()` is workaround for queryset caching
                    MODE_QUERYSETS["unread"].filter(feed__user=self.user).all().count(),
                )
                self.assertEqual(
                    response.context["read_entries_count"],
                    # NB: `all()` is workaround for queryset caching
                    MODE_QUERYSETS["read"].filter(feed__user=self.user).all().count(),
                )
                self.assertEqual(
                    response.context["favorites_entries_count"],
                    MODE_QUERYSETS["favorites"].filter(feed__user=self.user).count(),
                )
