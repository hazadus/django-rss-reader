from django.urls import reverse

from feeds.models import Entry
from feeds.tests.base_test_case import BaseFeedsViewsTestCase


class MiscViewTest(BaseFeedsViewsTestCase):
    """
    Test misc. views.
    """

    def test_entry_toggle_is_favorite_view(self):
        """
        Test `entry_toggle_is_favorite` view works as expected.
        """
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        # Do the actual test
        entry = Entry.objects.filter(is_favorite=False).first()
        entry_pk = entry.pk
        url = reverse("feeds:entry_toggle_is_favorite", kwargs={"entry_pk": entry_pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Entry.objects.get(pk=entry_pk).is_favorite, True)

    def test_feed_mark_as_read_view(self):
        """
        Test `feeds:feed_mark_as_read` view works as expected.
        """
        # Login
        url = reverse("account_login")
        self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        # Mark each feed as read and check unread count equals 0
        for feed in self.user.feeds.all():
            with self.subTest(feed=feed):
                url = reverse("feeds:feed_mark_as_read", kwargs={"feed_pk": feed.pk})
                self.client.post(url)
                self.assertEqual(feed.entries.filter(is_read=False).count(), 0)
