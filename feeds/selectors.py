from django.db.models import QuerySet

from feeds.models import Entry


def get_previous_entry(entry: Entry, queryset: QuerySet = Entry.objects.all()):
    return queryset.filter(pub_date__gt=entry.pub_date).last()


def get_next_entry(entry: Entry, queryset: QuerySet = Entry.objects.all()):
    return queryset.filter(pub_date__lt=entry.pub_date).first()
