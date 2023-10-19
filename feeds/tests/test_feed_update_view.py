from django.urls import reverse

from feeds.models import Feed, Folder
from feeds.views import FeedUpdateView

from .base_test_case import BaseFeedsViewsTestCase


class FeedUpdateViewTest(BaseFeedsViewsTestCase):
    """
    Test "feeds:update_feed" view with various options.
    """

    def test_feed_update_view_fails_without_login(self):
        """Check that "Update Feed" page fails for anonymous user."""
        feed = Feed.objects.filter(user=self.user).first()

        url = reverse("feeds:update_feed", kwargs={"pk": feed.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_feed_update_view_with_login(self):
        """Check that "Update Feed" page works with logged in user."""
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        feed = Feed.objects.filter(user=self.user).first()

        url = reverse("feeds:update_feed", kwargs={"pk": feed.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_feed_update_view_fails_for_other_user(self):
        """Check that "Update Feed" page fails when another user tries to open it."""
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        feed = Feed.objects.exclude(user=self.user).first()

        url = reverse("feeds:update_feed", kwargs={"pk": feed.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_feed_update_view_works_with_correct_data(self):
        """Check that "Update Feed" page works correct data."""
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        feed = Feed.objects.filter(user=self.user).first()
        feed_pk = feed.pk

        title = "New Feed Title"
        feed_url = "https://example.com/rss.xml"
        site_url = "https://example.com"
        image_url = "https://example.com/images/logo.png"
        folder = Folder.objects.create(user=self.user, title="Test Folder")

        url = reverse("feeds:update_feed", kwargs={"pk": feed.pk})
        response = self.client.post(
            url,
            data={
                "user": self.user.pk,
                "title": title,
                "url": feed_url,
                "site_url": site_url,
                "image_url": image_url,
                "folder": folder.pk,
            },
            follow=True,
        )

        updated_feed = Feed.objects.get(pk=feed_pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, FeedUpdateView.success_message)
        self.assertEqual(updated_feed.title, title)
        self.assertEqual(updated_feed.url, feed_url)
        self.assertEqual(updated_feed.site_url, site_url)
        self.assertEqual(updated_feed.image_url, image_url)
        self.assertEqual(updated_feed.folder, folder)
