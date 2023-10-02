from django.contrib.auth import get_user_model
from django.db import models


class Tag(models.Model):
    """
    Represents a tag assigned to the feed item.
    """

    title = models.CharField(
        verbose_name="title",
        max_length=256,
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "tag"
        verbose_name_plural = "tags"

    def __str__(self):
        return self.title


class Folder(models.Model):
    """
    Represents user-created folder containing some Feeds.
    """

    user = models.ForeignKey(
        verbose_name="user",
        to=get_user_model(),
        on_delete=models.CASCADE,
        related_name="folders",
    )
    title = models.CharField(
        verbose_name="title",
        max_length=256,
    )
    created = models.DateTimeField(verbose_name="created at", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="updated at", auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "folder"
        verbose_name_plural = "folders"

    def __str__(self):
        return self.title


class Feed(models.Model):
    """
    Represents an RSS feed subscription of the user.
    """

    user = models.ForeignKey(
        verbose_name="user",
        to=get_user_model(),
        on_delete=models.CASCADE,
        related_name="feeds",
    )
    title = models.CharField(
        verbose_name="title",
        max_length=256,
    )
    url = models.URLField(
        verbose_name="Feed URL",
        max_length=1024,
    )
    image_url = models.URLField(
        verbose_name="Feed image URL",
        max_length=1024,
        blank=True,
        null=True,
    )
    folder = models.ForeignKey(
        verbose_name="folder",
        to=Folder,
        on_delete=models.SET_NULL,
        related_name="feeds",
        blank=True,
        null=True,
    )
    created = models.DateTimeField(verbose_name="created at", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="updated at", auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "feed"
        verbose_name_plural = "feeds"

    def __str__(self):
        return self.title


class Entry(models.Model):
    """
    Represents an entry of the RSS feed.
    """

    feed = models.ForeignKey(
        verbose_name="Feed",
        to=Feed,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    title = models.CharField(
        verbose_name="title",
        max_length=512,
    )
    author = models.CharField(
        verbose_name="author",
        max_length=512,
        blank=True,
        null=True,
    )
    url = models.URLField(
        verbose_name="Entry URL",
        max_length=1024,
    )
    image_url = models.URLField(
        verbose_name="Entry image URL",
        max_length=1024,
        blank=True,
        null=True,
    )
    description = models.TextField(
        verbose_name="description",
        blank=True,
        null=True,
    )
    summary = models.TextField(
        verbose_name="summary",
        blank=True,
        null=True,
    )
    content = models.TextField(
        verbose_name="content",
        blank=True,
        null=True,
    )
    pub_date = models.DateTimeField(
        verbose_name="publication date",
        blank=True,
        null=True,
    )
    upd_date = models.DateTimeField(
        verbose_name="update date",
        blank=True,
        null=True,
    )
    is_read = models.BooleanField(
        verbose_name="read",
        default=False,
    )
    is_favorite = models.BooleanField(
        verbose_name="favorite (starred)",
        default=False,
    )
    tags = models.ManyToManyField(
        verbose_name="tags",
        to=Tag,
        related_name="entries",
        blank=True,
    )
    created = models.DateTimeField(verbose_name="created at", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="updated at", auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "entry"
        verbose_name_plural = "entries"

    def __str__(self):
        return self.title
