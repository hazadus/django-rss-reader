from io import BytesIO
import logging

import feedparser
import requests
from feedparser import FeedParserDict

from users.models import CustomUser

from .models import Feed, Folder

logger = logging.getLogger(__name__)


def get_parsed_feed_from_url(url: str) -> FeedParserDict | None:
    """
    Read feed data using `requests` with timeout, then parse content from it
    using `feedparser`.

    :param str url: url to parse feed from.
    :return: parsed feed as `FeedParserDict` or `None`.
    """
    try:
        response = requests.get(url, timeout=5.0)
    except requests.exceptions.ConnectTimeout:
        logger.warning("Timeout when reading RSS %s", url)
        return None
    except requests.exceptions.ConnectionError:
        logger.warning("Failed to resolve %s", url)
        return None

    # Put it to memory stream object
    content = BytesIO(response.content)

    # Return parsed content
    return feedparser.parse(content)


def feed_create(
    user: CustomUser,
    title: str,
    feed_url: str,
    site_url: str,
    image_url: str | None = None,
    folder: Folder | None = None,
) -> Feed | None:
    """
    Create Feed instance for `user`, if there's no feed with this `feed_url` for this user already.

    :param CustomUser user: user instance to create feed for.
    :param str title: title of the feed.
    :param str feed_url: URL of the feed.
    :param str site_url: URL of the feed's web site.
    :param str image_url: URL of the feed's image (icon).
    :param Folder folder: folder to put the feed into.
    :return: `Feed` if it was created, `None` otherwise (if user already has `Feed` with `feed_url` or there was an
            error.
    """
    feed_exists = Feed.objects.filter(user=user, url=feed_url).exists()

    if feed_exists:
        logger.warning("%s already subscribed to %s", user, feed_url)
        feed = None
    else:
        feed = Feed.objects.create(
            user=user,
            title=title,
            url=feed_url,
            site_url=site_url,
            image_url=image_url,
            folder=folder,
        )

    return feed


def feed_subscribe(
    user: CustomUser,
    feed_url: str,
) -> Feed | None:
    """
    Read feed data from `feed_url`, then create `Feed` instance for the `user`,
    if `user` does not already have one with the same `feed_url`.

    :param CustomUser user: user instance to create feed for.
    :param str feed_url: URL of the feed.
    :return: `Feed` if it was created, `None` otherwise (if user already has `Feed` with `feed_url` or there was an
            error.
    """
    feed_instance = None
    parsed_feed = get_parsed_feed_from_url(feed_url)

    if parsed_feed:
        title = parsed_feed.channel.get("title")
        site_url = parsed_feed.channel.get("link")

        image = parsed_feed.channel.get("image")
        image_url = image.get("href") if image else None

        if title and site_url:
            feed_instance = feed_create(
                user=user,
                title=title,
                feed_url=feed_url,
                site_url=site_url,
                image_url=image_url,
            )
        else:
            logger.warning("Title and url not found in %s", feed_url)

    return feed_instance
