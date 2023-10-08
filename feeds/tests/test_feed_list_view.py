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


class FeedListViewTest(TestCase):
    """
    Test "feeds:feed_list" view.
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

    def test_feed_list_view(self):
        """
        Check that correct data required in the template is present in context.
        """
        url = reverse("feeds:feed_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["feeds"]), Feed.objects.all().count())
        self.assertEqual(
            response.context["all_entries_count"], MODE_QUERYSETS["all"].count()
        )
        self.assertEqual(
            response.context["today_entries_count"], MODE_QUERYSETS["today"].count()
        )
        self.assertEqual(
            response.context["unread_entries_count"], MODE_QUERYSETS["unread"].count()
        )
        self.assertEqual(
            response.context["read_entries_count"], MODE_QUERYSETS["read"].count()
        )
        self.assertEqual(
            response.context["favorites_entries_count"],
            MODE_QUERYSETS["favorites"].count(),
        )
