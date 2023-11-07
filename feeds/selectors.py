from datetime import datetime

from django.db.models import (
    Case,
    Count,
    IntegerField,
    OuterRef,
    QuerySet,
    Subquery,
    When,
)

from feeds.models import Entry, Feed, Folder, Tag


def get_entry_queryset(user, mode: str) -> QuerySet:
    """
    Return Entry queryset for `user` and `mode`, where mode is one of "Smart Feed" names,
    i.e. all, today, unread, read, favorites.

    :param user: `CustomUser` instance
    :param str mode: all | today | unread | read | favorites
    """
    mode_querysets = {
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

    if mode not in mode_querysets.keys():
        raise KeyError(f"Incorrect mode '{mode}', must be in {mode_querysets.keys()}")
    return mode_querysets[mode].filter(feed__user=user)


def get_total_entry_count(user, mode: str) -> int:
    """
    Return TOTAL number of entries in specified "Smart Feed".
    """
    # NB: `all()` is workaround for queryset caching
    # Reference: https://docs.djangoproject.com/en/4.2/topics/db/optimization/#understand-cached-attributes
    return get_entry_queryset(user=user, mode=mode).all().count()


def get_unread_entry_count(user, mode: str) -> int:
    """
    Return number of UNREAD entries in specified "Smart Feed".
    """
    return get_entry_queryset(user=user, mode=mode).filter(is_read=False).count()


def get_previous_entry(user, entry: Entry, queryset: QuerySet = Entry.objects.all()):
    if not queryset or not entry or not entry.pub_date:
        return None

    queryset = queryset.filter(feed__user=user, pub_date__gt=entry.pub_date)
    if queryset.exists():
        return queryset.last()
    return None


def get_next_entry(user, entry: Entry, queryset: QuerySet = Entry.objects.all()):
    if not queryset or not entry or not entry.pub_date:
        return None

    queryset = queryset.filter(feed__user=user, pub_date__lt=entry.pub_date)
    if queryset.exists():
        return queryset.first()
    return None


def get_all_feeds(user) -> QuerySet:
    """
    Return all user's Feeds, annotated with:
    - `unread_entry_count` - number of unread entries in the Feed.
    - `latest_entry_pub_date` - pub_date of the newest entry in the feed.

    Queryset will be ordered by "-latest_entry_pub_date".
    """
    queryset = (
        Feed.objects.filter(user=user)
        # .prefetch_related("entries")
        .annotate(
            unread_entry_count=Count(
                Case(
                    When(entries__is_read=False, then=1),
                    output_field=IntegerField(),
                )
            )
        ).annotate(total_entry_count=Count("entries"))
    )

    latest_entry_pub_date = Subquery(
        Entry.objects.filter(
            feed_id=OuterRef("id"),
        )
        .order_by("-pub_date")
        .values("pub_date")[:1]
    )

    queryset = queryset.annotate(
        latest_entry_pub_date=latest_entry_pub_date,
    ).order_by("-latest_entry_pub_date")

    return queryset


def get_all_folders(user) -> QuerySet:
    """
    Return QuerySet with all user's folders.
    """
    return Folder.objects.filter(user=user).prefetch_related("feeds")


def get_feed(pk: int) -> Feed:
    return Feed.objects.get(pk=pk)


def get_all_tags() -> QuerySet:
    return (
        Tag.objects.all()
        .annotate(num_entries=Count("entries"))
        .order_by("-num_entries")
    )
