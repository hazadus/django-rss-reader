# Generated by Django 4.2.5 on 2023-10-02 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Entry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=512, verbose_name="title")),
                (
                    "author",
                    models.CharField(
                        blank=True, max_length=512, null=True, verbose_name="author"
                    ),
                ),
                ("url", models.URLField(max_length=1024, verbose_name="Entry URL")),
                (
                    "image_url",
                    models.URLField(
                        blank=True,
                        max_length=1024,
                        null=True,
                        verbose_name="Entry image URL",
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="description"),
                ),
                (
                    "summary",
                    models.TextField(blank=True, null=True, verbose_name="summary"),
                ),
                (
                    "content",
                    models.TextField(blank=True, null=True, verbose_name="content"),
                ),
                (
                    "pub_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="publication date"
                    ),
                ),
                (
                    "upd_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="update date"
                    ),
                ),
                ("is_read", models.BooleanField(default=False, verbose_name="read")),
                (
                    "is_favorite",
                    models.BooleanField(
                        default=False, verbose_name="favorite (starred)"
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
            ],
            options={
                "verbose_name": "entry",
                "verbose_name_plural": "entries",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="Feed",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=256, verbose_name="title")),
                ("url", models.URLField(max_length=1024, verbose_name="Feed URL")),
                ("site_url", models.URLField(max_length=1024, verbose_name="Site URL")),
                (
                    "image_url",
                    models.URLField(
                        blank=True,
                        max_length=1024,
                        null=True,
                        verbose_name="Feed image URL",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
            ],
            options={
                "verbose_name": "feed",
                "verbose_name_plural": "feeds",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="Folder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=256, verbose_name="title")),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
            ],
            options={
                "verbose_name": "folder",
                "verbose_name_plural": "folders",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=256, verbose_name="title")),
            ],
            options={
                "verbose_name": "tag",
                "verbose_name_plural": "tags",
                "ordering": ["title"],
            },
        ),
    ]