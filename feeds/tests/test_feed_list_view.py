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


class FeedListViewTest(TestCase):
    """
    Test "feeds:feed_list" view.
    """

    email = "anon@mail.com"
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
        cls.user = CustomUser.objects.get(email=cls.email)

    def test_feed_list_url(self):
        """
        Ensure "feeds:feed_list" view is not accessible without login.
        """
        # Redirect when not logged in
        url = reverse("feeds:feed_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_feed_list_view(self):
        """
        Check that correct data required in the template is present in context.
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        # Do the actual test
        url = reverse("feeds:feed_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
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
