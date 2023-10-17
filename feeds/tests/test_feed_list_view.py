from django.urls import reverse

from feeds.models import Feed

from .base_test_case import BaseFeedsViewsTestCase


class FeedListViewTest(BaseFeedsViewsTestCase):
    """
    Test "feeds:feed_list" view.
    """

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
            self.MODE_QUERYSETS["all"].count(),
        )
        self.assertEqual(
            response.context["today_entries_count"],
            self.MODE_QUERYSETS["today"].count(),
        )
        self.assertEqual(
            response.context["all_unread_count"],
            self.MODE_QUERYSETS["all"].filter(is_read=False).count(),
        )
        self.assertEqual(
            response.context["today_unread_count"],
            self.MODE_QUERYSETS["today"].filter(is_read=False).count(),
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
