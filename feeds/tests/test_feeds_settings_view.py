from django.urls import reverse

from feeds.models import Feed, Folder

from .base_test_case import BaseFeedsViewsTestCase


class FeedsSettingsViewTest(BaseFeedsViewsTestCase):
    """
    Test "feeds:settings_feeds" view with various options.
    """

    def test_settings_feeds_view_with_login(self):
        """Check that Settings/Feeds page works with logged in user."""
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        url = reverse("feeds:settings_feeds")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_settings_feeds_view_without_login(self):
        """Check that Settings/Feeds page is not accessible to anonymous user."""

        url = reverse("feeds:settings_feeds")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_settings_feeds_view_add_feed(self):
        """Check that Settings/Feeds page correctly creates new feed."""
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        title = "Example RSS Feed"
        feed_url = "https://www.example.com/rss.xml"
        site_url = "https://example.com/"
        image_url = "https://example.com/feed.jpg"
        folder = Folder.objects.create(title="Example Folder", user=self.user)

        url = reverse("feeds:settings_feeds")
        response = self.client.post(
            url,
            data={
                "url": feed_url,
                "title": title,
                "site_url": site_url,
                "image_url": image_url,
                "folder": folder.pk,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        new_feed = Feed.objects.get(user=self.user, url=feed_url)
        self.assertEqual(new_feed.title, title)
        self.assertEqual(new_feed.url, feed_url)
        self.assertEqual(new_feed.site_url, site_url)
        self.assertEqual(new_feed.image_url, image_url)
        self.assertEqual(new_feed.folder, folder)

    def test_settings_feeds_view_wont_add_dupe_feed(self):
        """Check that Settings/Feeds page will not add feed with the same URL twice."""
        # Login
        url = reverse("account_login")
        response = self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        feed = Feed.objects.first()

        url = reverse("feeds:settings_feeds")
        response = self.client.post(
            url,
            data={
                "url": feed.url,
                "title": feed.title,
                "site_url": feed.site_url,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You already have subscription")
        self.assertEqual(Feed.objects.filter(user=self.user, url=feed.url).count(), 1)

    def test_settings_feeds_manage_feeds(self):
        """
        Test that all user's feeds are listed in "Manage Feeds" section on Settings/Feeds tab.
        """
        # Login
        url = reverse("account_login")
        self.client.post(
            url, {"login": self.email, "password": self.password}, follow=True
        )

        feeds = Feed.objects.filter(user=self.user)

        for feed in feeds:
            with self.subTest(feed=feed):
                url = reverse("feeds:settings_feeds")
                response = self.client.get(url)
                self.assertContains(response, feed.title)
