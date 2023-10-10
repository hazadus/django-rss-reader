from datetime import datetime

from django.db.models import Count, QuerySet

from feeds.models import Entry, Feed, Tag

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


def get_entry_queryset(user, mode: str) -> QuerySet:
    """
    Return Entry queryset for "mode", where mode is one of "Smart Feed" names,
    i.e. all, today, unread, read, favorites.
    """
    if mode not in MODE_QUERYSETS.keys():
        raise KeyError(f"Incorrect mode '{mode}', must be in {MODE_QUERYSETS.keys()}")
    return MODE_QUERYSETS[mode].filter(feed__user=user)


def get_entry_count(user, mode: str) -> int:
    """
    Return TOTAL number of entries in specified "Smart Feed".
    """
    # NB: `all()` is workaround for queryset caching
    # Reference: https://docs.djangoproject.com/en/4.2/topics/db/optimization/#understand-cached-attributes
    return get_entry_queryset(user=user, mode=mode).all().count()


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
    return Feed.objects.filter(user=user).prefetch_related("entries")


def get_feed(pk: int) -> Feed:
    return Feed.objects.get(pk=pk)


def get_all_tags() -> QuerySet:
    return (
        Tag.objects.all()
        .annotate(num_entries=Count("entries"))
        .order_by("-num_entries")
    )
