import logging
from datetime import datetime
from io import BytesIO

import feedparser
import requests
from dateutil import parser as date_parser
from dateutil import tz
from django.conf import settings
from feedparser import FeedParserDict

from feeds.models import Entry, Feed, Folder, Tag
from feeds.utils import parse_meta_from_url
from users.models import CustomUser

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
        logger.warning("Timeout when connecting to %s", url)
        return None
    except requests.exceptions.ReadTimeout:
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


def tag_get_or_create(title: str) -> Tag:
    """
    Get or create Tag with capitalized `title` (trimming spaces and removing commas).

    :param str title: title of the tag.
    :return: Tag instance.
    """
    title = title.replace(",", "").lstrip().rstrip().capitalize()
    queryset = Tag.objects.filter(title=title)
    if queryset.exists():
        return queryset.first()
    else:
        return Tag.objects.create(title=title)


def entry_exists(feed: Feed, url: str) -> bool:
    return Entry.objects.filter(feed=feed, url=url).exists()


def entry_create(
    feed: Feed,
    title: str,
    url: str,
    author: str | None,
    image_url: str | None,
    description: str | None,
    summary: str | None,
    content: str | None,
    pub_date: datetime | None,
    upd_date: datetime | None,
) -> Entry | None:
    """
    Create and return Entry instance using passed parameters.

    :return: created Entry instance.
    """

    # Some feeds will have no `pub_date`, but they usually have `upd_date` instead.
    # Because we heavily use `pub_date` for navigation, ensure that it is not None.
    if not pub_date:
        app_tz = tz.gettz(settings.TIME_ZONE)
        pub_date = upd_date if upd_date else datetime.now(tz=app_tz)

    return Entry.objects.create(
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


def get_content_from_entry_data(entry_data: dict) -> str | None:
    """
    Retrieve `text/html` content from entry data parsed by `feedparser` from feed url.

    :return: text/html content, if found, else None.
    """
    content = None

    if content_list := entry_data.get("content", None):
        for item in content_list:
            if item.get("type", None) == "text/html":
                content = item.get("value", None)
                break

    return content


def entry_create_from_data_if_not_exists(feed: Feed, entry_data: dict) -> Entry | None:
    """
    Create Entry instance from data parsed by `feedparser`. Add all tags (if present) for the Entry.
    Tags will be created, if necessary.

    :return: created `Entry` or `None`
    """
    entry_instance = None
    title = entry_data.get("title")
    link = entry_data.get("link")
    if title and link and not entry_exists(feed=feed, url=link):
        logger.info(" -- Adding new Entry: %s", title)
        pub_date = (
            date_parser.parse(entry_data.get("published"))
            if entry_data.get("published")
            else None
        )
        upd_date = (
            date_parser.parse(entry_data.get("updated"))
            if entry_data.get("updated")
            else None
        )
        meta_info = parse_meta_from_url(url=link)
        entry_instance = entry_create(
            feed=feed,
            title=title,
            url=link,
            author=entry_data.get("author", None),
            image_url=meta_info["image_url"] if meta_info else None,
            description=entry_data.get("description", None),
            summary=entry_data.get("summary", None),
            content=get_content_from_entry_data(entry_data=entry_data),
            pub_date=pub_date,
            upd_date=upd_date,
        )

        # Add tags to entry instance
        if tags := entry_data.get("tags"):
            for tag_item in tags:
                if term := tag_item["term"]:
                    entry_instance.tags.add(tag_get_or_create(term))

    return entry_instance


def feed_update(feed: Feed):
    """
    Fetch entries for the feed using `feedparser`, then create new Entry instance for each fetched entry
    if there's no entry with the same link already.

    :param Feed feed: feed to update.
    """
    logger.info("Updating feed: %s", feed)
    feed_content = get_parsed_feed_from_url(feed.url)
    entries = feed_content.entries if feed_content else None

    if not entries:
        logger.warning("No 'entries' fetched from %s", feed.url)
        return

    logger.info(" - Number of entries: %s", len(entries))

    # For each entry in feed_content.entries, try to get Entry from the database by `url`
    # If not exists, create one.
    new_entry_count = 0
    for entry_data in entries:
        if entry_create_from_data_if_not_exists(feed=feed, entry_data=entry_data):
            new_entry_count += 1

    logger.info(" -- Created %s new Entries in %s", new_entry_count, feed.title)


def update_all_feeds():
    """
    Fetch new entries for all feeds in the database.
    """
    feeds = Feed.objects.all()
    logger.info("Feeds to update: %s", feeds.count())

    # Call feed_update() for each feed
    for feed in feeds:
        feed_update(feed)


def mark_entry_as_read(pk: int):
    """
    Mark entry as read and save it.

    :param int pk: primary key of the entry to mark as read.
    """
    Entry.objects.filter(pk=pk).update(is_read=True)


def mark_feed_as_read(feed_pk: int):
    """
    Mark all entries in the feed as read.

    :param int feed_pk: primary key of the feed where to mark all entries as read.
    """
    Entry.objects.filter(feed_id=feed_pk, is_read=False).update(is_read=True)


def toggle_entry_is_favorite(pk: int):
    """
    Toggle entry's favorite status and save it.

    :param int pk: primary key of the entry to toggle favorite status.
    """
    entry = Entry.objects.get(pk=pk)
    Entry.objects.filter(pk=pk).update(is_favorite=not entry.is_favorite)
