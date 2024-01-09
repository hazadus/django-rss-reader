import logging
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime
from functools import partial
from io import BytesIO
from typing import NamedTuple

import feedparser
import requests
from dateutil import parser as date_parser
from dateutil import tz
from django.conf import settings
from feedparser import FeedParserDict

from feeds.exceptions import (
    CantGetFeedFromURL,
    CantGetFeedInfoFromURL,
    CantSubscribeToFeed,
    FeedAlreadyExists,
)
from feeds.models import Entry, Feed, Folder, Tag
from feeds.utils import CantGetPageInfoFromURL, parse_page_info_from_url
from users.models import CustomUser


class FeedInfo(NamedTuple):
    """Feed info needed to created Feed instance."""

    title: str
    feed_url: str
    site_url: str
    image_url: str | None
    favicon_url: str | None


logger = logging.getLogger(__name__)


def update_all_feeds() -> None:
    """
    Fetch new entries for all feeds in the database.
    """
    feeds = Feed.objects.all()
    logger.info("Feeds to update: %s", feeds.count())

    # Call feed_update() for each feed
    [feed_update(feed) for feed in feeds]


def feed_subscribe(
    user: CustomUser,
    feed_url: str,
) -> Feed:
    """
    Read and parse feed data from `feed_url`, then create `Feed` instance for the `user`,
    if `user` does not already have one with the same `feed_url`.

    :param CustomUser user: user instance to create feed for.
    :param str feed_url: URL of the feed.
    :return: new `Feed` instance
    :raises CantSubscribeToFeed: in case of any error, or if `user` is already subscribed to the `feed_url`.
    """
    if user_subscribed_to_feed(user, feed_url):
        raise CantSubscribeToFeed

    try:
        feed_info: FeedInfo = _get_feed_info_from_url(feed_url)
    except CantGetFeedInfoFromURL:
        logger.error("Can't retrieve mandatory feed info from URL %s", feed_url)
        raise CantSubscribeToFeed

    return feed_create(
        user=user,
        title=feed_info.title,
        feed_url=feed_info.feed_url,
        site_url=feed_info.site_url,
        image_url=feed_info.favicon_url or feed_info.image_url or None,
    )


def _get_feed_info_from_url(feed_url: str) -> FeedInfo:  # noqa: C901
    """
    Get data and parse mandatory feed info, required to create Feed instance, from `feed_url`.

    :param feed_url: URL to parse feed info from.
    :return: `FeedInfo` instance with mandatory feed info.
    :raises CantGetFeedInfoFromURL: in case mandatory feed info can't be retrieved.
    """
    try:
        parsed_feed = _get_parsed_feed_from_url(feed_url)
    except CantGetFeedFromURL:
        logger.error("Can't get feed data from URL %s", feed_url)
        raise CantGetFeedInfoFromURL

    title = parsed_feed.channel.get("title")
    site_url = parsed_feed.channel.get("link")
    image = parsed_feed.channel.get("image")
    image_url = image.get("href") if image else None

    if not title and site_url:
        logger.error("Title and URL not found in %s", feed_url)
        raise CantGetFeedInfoFromURL

    # Try to get favicon from feed's site
    favicon_url = None
    try:
        page_info = parse_page_info_from_url(url=site_url)
        favicon_url = page_info["favicon_url"]
    except CantGetPageInfoFromURL:
        logger.warning("Can't get page info for URL %s", site_url)

    return FeedInfo(
        title=title,
        feed_url=feed_url,
        site_url=site_url,
        image_url=image_url,
        favicon_url=favicon_url,
    )


def feed_create(
    user: CustomUser,
    title: str,
    feed_url: str,
    site_url: str,
    image_url: str | None = None,
    folder: Folder | None = None,
) -> Feed:
    """
    Create Feed instance for `user`, if there's no feed with `feed_url` for this user already.

    :param CustomUser user: user instance to create feed for.
    :param str title: title of the feed.
    :param str feed_url: URL of the feed.
    :param str site_url: URL of the feed's web site.
    :param str image_url: URL of the feed's image (icon).
    :param Folder folder: folder to put the feed into.
    :return: new `Feed` instance.
    :raises FeedAlreadyExists: if `user` is already subscribed to the `feed_url`.
    """
    feed_exists = Feed.objects.filter(user=user, url=feed_url).exists()

    if feed_exists:
        logger.warning("%s already subscribed to %s", user, feed_url)
        raise FeedAlreadyExists

    return Feed.objects.create(
        user=user,
        title=title,
        url=feed_url,
        site_url=site_url,
        image_url=image_url,
        folder=folder,
    )


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
) -> Entry:
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


def mark_entry_as_read(pk: int) -> None:
    """
    Mark entry as read and save it.

    :param int pk: primary key of the entry to mark as read.
    """
    Entry.objects.filter(pk=pk).update(is_read=True)


def toggle_entry_is_favorite(pk: int) -> None:
    """
    Toggle entry's favorite status and save it.

    :param int pk: primary key of the entry to toggle favorite status.
    """
    entry = Entry.objects.get(pk=pk)
    Entry.objects.filter(pk=pk).update(is_favorite=not entry.is_favorite)


def entry_exists(feed: Feed, url: str) -> bool:
    return Entry.objects.filter(feed=feed, url=url).exists()


def user_subscribed_to_feed(user: CustomUser, feed_url: str) -> bool:
    """
    Check if `user` is already subscribed to `feed_url`.

    :param user: User to check for subscription.
    :param feed_url: feed URL to check for subscription.
    :return: True if `user` is already subscribed to `feed_url`, False otherwise.
    """
    return Feed.objects.filter(user=user, url=feed_url).exists()


def mark_feed_as_read(feed_pk: int) -> None:
    """
    Mark all entries in the feed as read.

    :param int feed_pk: primary key of the feed where to mark all entries as read.
    """
    Entry.objects.filter(feed_id=feed_pk, is_read=False).update(is_read=True)


def feed_update(feed: Feed) -> None:  # noqa: C901
    """
    Fetch entries for the feed using `feedparser`, then create new Entry instance for each fetched entry
    if there's no entry with the same link already.

    :param Feed feed: feed to update.
    """
    logger.info("Updating feed: %s", feed)

    try:
        feed_content = _get_parsed_feed_from_url(feed.url)
    except CantGetFeedFromURL as ex:
        logger.exception(
            "An error has occured while trying to get parsed feed from URL %s",
            feed.url,
            exc_info=ex,
        )
        return

    entries = feed_content.entries if feed_content else None

    if not entries:
        logger.warning("No 'entries' fetched from %s", feed.url)
        return

    logger.info(" - Number of entries: %s", len(entries))

    # For each entry in feed_content.entries, try to get Entry from the database by `url`
    # If not exists, create one.
    with ThreadPoolExecutor(max_workers=20) as executor:
        tasks: list[Future] = []
        future_to_url: dict[Future, str] = {}
        task = partial(_entry_create_from_data_if_not_exists, feed)

        for entry_data in entries:
            future = executor.submit(task, entry_data)
            tasks.append(future)
            future_to_url[future] = entry_data.get("link")

        new_entry_count = 0
        for future in as_completed(tasks):
            try:
                res = future.result()
                new_entry_count = new_entry_count + 1 if res else new_entry_count
            except Exception as ex:
                logger.exception(
                    "An error has occured while trying to create entry fron link=%s",
                    future_to_url[future],
                    exc_info=ex,
                )

        logger.info(" -- Created %s new Entries in %s", new_entry_count, feed.title)


def _get_parsed_feed_from_url(url: str) -> FeedParserDict:
    """
    Read feed data using `requests` with timeout, then parse content from it
    using `feedparser`.

    :param str url: url to parse feed from.
    :return: parsed feed as `FeedParserDict` or `None`.
    :raises CantGetFeedFromURL: in case of any error.
    """
    try:
        response = requests.get(url, timeout=5.0)
    except requests.exceptions.ConnectTimeout:
        logger.warning("Timeout when connecting to %s", url)
        raise CantGetFeedFromURL
    except requests.exceptions.ReadTimeout:
        logger.warning("Timeout when reading RSS %s", url)
        raise CantGetFeedFromURL
    except requests.exceptions.ConnectionError:
        logger.warning("Failed to resolve %s", url)
        raise CantGetFeedFromURL

    # Put it to memory stream object
    content = BytesIO(response.content)

    # Return parsed content
    return feedparser.parse(content)


def _get_content_from_entry_data(entry_data: dict) -> str | None:
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


def _entry_create_from_data_if_not_exists(feed: Feed, entry_data: dict) -> Entry | None:
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
        page_info = parse_page_info_from_url(url=link)
        entry_instance = entry_create(
            feed=feed,
            title=title,
            url=link,
            author=entry_data.get("author", None),
            image_url=page_info["image_url"] if page_info else None,
            description=entry_data.get("description", None),
            summary=entry_data.get("summary", None),
            content=_get_content_from_entry_data(entry_data=entry_data),
            pub_date=pub_date,
            upd_date=upd_date,
        )

        # Add tags to entry instance
        if tags := entry_data.get("tags"):
            for tag_item in tags:
                if term := tag_item["term"]:
                    entry_instance.tags.add(_tag_get_or_create(term))

    return entry_instance


def _tag_get_or_create(title: str) -> Tag:
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
