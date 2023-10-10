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


class EntryListViewTest(TestCase):
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

    def test_entry_list_mode_all_view(self):
        """
        Mode "all"
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.username, "password": self.password}, follow=True
        )

        # Do the actual test
        url = reverse("feeds:entry_list", kwargs={"mode": "all"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["mode"], "all")
        self.assertEqual(
            response.context["entry_count"],
            MODE_QUERYSETS["all"].filter(feed__user=self.user).count(),
        )
        self.assertEqual(
            len(response.context["feeds"]), Feed.objects.filter(user=self.user).count()
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

    def test_entry_list_mode_today_view(self):
        """
        Mode "today"
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.username, "password": self.password}, follow=True
        )

        # Do the actual test
        url = reverse("feeds:entry_list", kwargs={"mode": "today"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["mode"], "today")
        self.assertEqual(
            response.context["entry_count"],
            MODE_QUERYSETS["today"].filter(feed__user=self.user).count(),
        )
        self.assertEqual(
            len(response.context["feeds"]), Feed.objects.filter(user=self.user).count()
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

    def test_entry_list_mode_unread_view(self):
        """
        Mode "unread"
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.username, "password": self.password}, follow=True
        )

        # Do the actual test
        url = reverse("feeds:entry_list", kwargs={"mode": "unread"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["mode"], "unread")
        self.assertEqual(
            response.context["entry_count"],
            MODE_QUERYSETS["unread"].filter(feed__user=self.user).count(),
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

    def test_entry_list_mode_read_view(self):
        """
        Mode "read"
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.username, "password": self.password}, follow=True
        )

        # Do the actual test
        url = reverse("feeds:entry_list", kwargs={"mode": "read"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["mode"], "read")
        self.assertEqual(
            response.context["entry_count"],
            MODE_QUERYSETS["read"].filter(feed__user=self.user).count(),
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

    def test_entry_list_mode_favorites_view(self):
        """
        Mode "favorites"
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.username, "password": self.password}, follow=True
        )

        # Do the actual test
        url = reverse("feeds:entry_list", kwargs={"mode": "favorites"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["mode"], "favorites")
        self.assertEqual(
            response.context["entry_count"],
            MODE_QUERYSETS["favorites"].filter(feed__user=self.user).count(),
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

    def test_entry_list_in_feed_view(self):
        """
        Test "feeds:entry_list" with all modes and all feeds using
        "in_feed" GET parameter.
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.username, "password": self.password}, follow=True
        )

        # Do the actual test
        for mode in MODE_QUERYSETS.keys():
            for feed in Feed.objects.all():
                url = (
                    reverse("feeds:entry_list", kwargs={"mode": mode})
                    + "?in_feed="
                    + str(feed.pk)
                )
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["mode"], mode)
                self.assertEqual(response.context["in_feed"], str(feed.pk))
                self.assertEqual(response.context["feed"], feed)
                self.assertEqual(
                    response.context["entry_count"],
                    MODE_QUERYSETS[mode]
                    .filter(feed__user=self.user, feed=feed)
                    .count(),
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
