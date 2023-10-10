from django.urls import reverse

from feeds.models import Feed

from .base_test_case import BaseFeedsViewsTestCase


class EntryListViewTest(BaseFeedsViewsTestCase):
    """
    Test "feeds:entry_list" view with various options.
    """

    def test_entry_list_mode_all_view(self):
        """
        Mode "all"
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        # Do the actual test
        url = reverse("feeds:entry_list", kwargs={"mode": "all"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["mode"], "all")
        self.assertEqual(
            response.context["entry_count"],
            self.MODE_QUERYSETS["all"].count(),
        )
        self.assertEqual(
            len(response.context["feeds"]), Feed.objects.filter(user=self.user).count()
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

    def test_entry_list_mode_today_view(self):
        """
        Mode "today"
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        # Do the actual test
        url = reverse("feeds:entry_list", kwargs={"mode": "today"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["mode"], "today")
        self.assertEqual(
            response.context["entry_count"],
            self.MODE_QUERYSETS["today"].filter(feed__user=self.user).count(),
        )
        self.assertEqual(
            len(response.context["feeds"]), Feed.objects.filter(user=self.user).count()
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

    def test_entry_list_mode_unread_view(self):
        """
        Mode "unread"
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        # Do the actual test
        url = reverse("feeds:entry_list", kwargs={"mode": "unread"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["mode"], "unread")
        self.assertEqual(
            response.context["entry_count"],
            self.MODE_QUERYSETS["unread"].count(),
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

    def test_entry_list_mode_read_view(self):
        """
        Mode "read"
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        # Do the actual test
        url = reverse("feeds:entry_list", kwargs={"mode": "read"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["mode"], "read")
        self.assertEqual(
            response.context["entry_count"],
            self.MODE_QUERYSETS["read"].count(),
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

    def test_entry_list_mode_favorites_view(self):
        """
        Mode "favorites"
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        # Do the actual test
        url = reverse("feeds:entry_list", kwargs={"mode": "favorites"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["mode"], "favorites")
        self.assertEqual(
            response.context["entry_count"],
            self.MODE_QUERYSETS["favorites"].count(),
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

    def test_entry_list_in_feed_view(self):
        """
        Test "feeds:entry_list" with all modes and all feeds using
        "in_feed" GET parameter.
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        # Do the actual test
        for mode in self.MODE_QUERYSETS.keys():
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
                    self.MODE_QUERYSETS[mode].filter(feed=feed).count(),
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
