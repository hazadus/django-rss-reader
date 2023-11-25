from datetime import datetime

from dateutil import tz
from django.conf import settings
from django.test import TestCase

from feeds.models import Entry, Feed, Folder, Tag
from feeds.services import (
    FeedAlreadyExists,
    _tag_get_or_create,
    entry_create,
    entry_exists,
    feed_create,
)
from users.models import CustomUser


class ServicesTest(TestCase):
    fixtures = [
        "users/tests/fixtures/users.json",
        "feeds/tests/fixtures/tags.json",
        "feeds/tests/fixtures/feeds.json",
        "feeds/tests/fixtures/entries.json",
    ]

    def test_feed_create(self):
        """
        Test that `feed_create()` create and return new Feed when correct parameters were passed,
        and user is not yet subscribed to `feed_url`.
        """
        user = CustomUser.objects.create_user(username="testuser", password="password")
        folder = Folder.objects.create(user=user, title="Test Folder")
        title = "Amazing Blog"
        feed_url = "https://superblog.com/rss.xml"
        site_url = "https://superblog.com"
        image_url = "https://superblog.com/logo.jpg"

        feed = feed_create(
            user=user,
            title=title,
            feed_url=feed_url,
            site_url=site_url,
            image_url=image_url,
            folder=folder,
        )

        self.assertEqual(feed.user, user)
        self.assertEqual(feed.title, title)
        self.assertEqual(feed.url, feed_url)
        self.assertEqual(feed.site_url, site_url)
        self.assertEqual(feed.image_url, image_url)
        self.assertEqual(feed.folder, folder)

    def test_feed_create_dont_create_dupe(self):
        """
        Test that `feed_create()` won't create Feed with the same URL for the same user and return None.
        """
        feed = Feed.objects.first()

        # Try to create same feed for the same user
        with self.assertRaises(FeedAlreadyExists):
            feed_create(
                user=feed.user,
                title=feed.title,
                feed_url=feed.url,
                site_url=feed.site_url,
            )

        self.assertEqual(Feed.objects.filter(user=feed.user, url=feed.url).count(), 1)

    def test_tag_get_or_create_creates(self):
        """
        Test that `tag_get_or_create()` creates and returns Tag instance,
        if there's no such Tag in the database yet. Commas and spaces (in the beginning
        and in the end of the title) must be removed, text must be capitalized.
        """
        title = "  New Tag Title, For Tests  "
        tag = _tag_get_or_create(title=title)
        self.assertEqual(
            tag.title, title.replace(",", "").lstrip().rstrip().capitalize()
        )

    def test_tag_get_or_create_returns_existing(self):
        """
        Test that `tag_get_or_create()` returns existing Tag instance, if there's already
        Tag with the same title in the database. Note that commas and spaces (in the beginning
        and in the end of the title) are removed, and text is capitalized.
        """
        tag = Tag.objects.first()
        tag_returned = _tag_get_or_create(
            title=" {title},  ".format(
                title=tag.title,
            )
        )
        self.assertEqual(tag.pk, tag_returned.pk)

    def test_entry_exists_return_true(self):
        """
        Test that `entry_exists()` return True if entry with `url` actually exists in the `feed`.
        """
        entry = Entry.objects.first()
        self.assertTrue(entry_exists(feed=entry.feed, url=entry.url))

    def test_entry_exists_return_false(self):
        """
        Test that `entry_exists()` return False if entry with `url` does not exist in the `feed`.
        """
        feed = Feed.objects.first()
        self.assertFalse(
            entry_exists(feed=feed, url="https://aMadeUpBlogUrl.com/blog/post")
        )

    def test_entry_create(self):
        """
        Test that `entry_create()` creates and returns new Entry when correct parameters
        were passed.
        """
        app_tz = tz.gettz(settings.TIME_ZONE)
        feed = Feed.objects.first()
        title = "A New Blog Post"
        url = "https://aMadeUpBlogUrl.com/blog/new-blog-post"
        author = "Ivan Petrov"
        image_url = "https://aMadeUpBlogUrl.com/images/new-blog-post.jpg"
        description = "Description"
        summary = "Summary"
        content = "Content"
        pub_date = datetime.now(tz=app_tz)
        upd_date = datetime.now(tz=app_tz)

        entry = entry_create(
            feed=feed,
            title=title,
            url=url,
            author=author,
            image_url=image_url,
            description=description,
            summary=summary,
            content=content,
            pub_date=pub_date,
            upd_date=upd_date,
        )

        self.assertEqual(entry.feed, feed)
        self.assertEqual(entry.title, title)
        self.assertEqual(entry.url, url)
        self.assertEqual(entry.author, author)
        self.assertEqual(entry.image_url, image_url)
        self.assertEqual(entry.description, description)
        self.assertEqual(entry.summary, summary)
        self.assertEqual(entry.pub_date, pub_date)
        self.assertEqual(entry.upd_date, upd_date)

    def test_entry_create_when_pub_date_is_none(self):
        """
        Test that `entry_create()` creates and returns new Entry when correct parameters
        were passed, but `pub_date` and `upd_date` are set to None. In this case,
        `pub_date` must be set to current time by `entry_create()`.
        """
        feed = Feed.objects.first()
        title = "A New Blog Post"
        url = "https://aMadeUpBlogUrl.com/blog/new-blog-post"
        author = "Ivan Petrov"
        image_url = "https://aMadeUpBlogUrl.com/images/new-blog-post.jpg"
        description = "Description"
        summary = "Summary"
        content = "Content"
        pub_date = None
        upd_date = None

        entry = entry_create(
            feed=feed,
            title=title,
            url=url,
            author=author,
            image_url=image_url,
            description=description,
            summary=summary,
            content=content,
            pub_date=pub_date,
            upd_date=upd_date,
        )

        self.assertEqual(entry.feed, feed)
        self.assertEqual(entry.title, title)
        self.assertEqual(entry.url, url)
        self.assertEqual(entry.author, author)
        self.assertEqual(entry.image_url, image_url)
        self.assertEqual(entry.description, description)
        self.assertEqual(entry.summary, summary)
        self.assertIsNotNone(entry.pub_date)
        self.assertIsNone(entry.upd_date)
