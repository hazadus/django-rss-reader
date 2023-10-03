from django.contrib import admin

from .models import Entry, Feed, Folder, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Configures admin panel views for Tag.
    """

    model = Tag
    list_display = [
        "title",
    ]


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    """
    Configures admin panel views for Folder.
    """

    model = Folder
    list_display = [
        "title",
        "user",
    ]


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    """
    Configures admin panel views for Feed.
    """

    model = Feed
    list_display = [
        "title",
        "user",
        "folder",
        "created",
    ]


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    """
    Configures admin panel views for Entry.
    """

    model = Entry
    list_display = [
        "title",
        "feed",
        "pub_date",
        "is_read",
        "is_favorite",
        "created",
    ]
    readonly_fields = [
        "created",
        "updated",
    ]
    fieldsets = [
        (
            "Main",
            {
                "fields": [
                    "feed",
                    "title",
                    "author",
                    "url",
                    "image_url",
                ]
            },
        ),
        (
            "Status",
            {
                "fields": [
                    "is_read",
                    "is_favorite",
                ]
            },
        ),
        (
            "Content",
            {
                "fields": [
                    "description",
                    "summary",
                    "content",
                    "pub_date",
                    "upd_date",
                    "tags",
                ]
            },
        ),
        (
            "Timestamps",
            {
                "fields": [
                    "created",
                    "updated",
                ]
            },
        ),
    ]
