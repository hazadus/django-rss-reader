from django.urls import reverse

from feeds.models import Feed

from .base_test_case import BaseFeedsViewsTestCase


class FeedDeleteViewTest(BaseFeedsViewsTestCase):
    """
    Test "feeds:delete_feed" view.
    """

    def test_feed_delete_view_fails_without_login(self):
        """Check that "Delete Feed" view fails for anonymous user."""
        feed = Feed.objects.filter(user=self.user).first()

        url = reverse("feeds:delete_feed", kwargs={"pk": feed.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_feed_delete_view_with_login(self):
        """Check that "Delete Feed" view works with logged in user."""
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        feed = Feed.objects.filter(user=self.user).first()
        feed_pk = feed.pk

        url = reverse("feeds:delete_feed", kwargs={"pk": feed.pk})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Feed.objects.filter(pk=feed_pk).exists())

    def test_feed_delete_view_wont_delete_others_user_feed(self):
        """Check that "Delete Feed" view won't delete other user's feed."""
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        feed = Feed.objects.exclude(user=self.user).first()

        url = reverse("feeds:delete_feed", kwargs={"pk": feed.pk})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Feed.objects.filter(pk=feed.pk).exists())
