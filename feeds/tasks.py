import shlex
import subprocess

from celery import shared_task

from feeds.models import Entry, Feed
from feeds.services import feed_update
from feeds.utils import parse_page_info_from_url


@shared_task
def parse_and_set_image_for_feed(feed_pk: int):
    """
    Parse and set image for feed, if there's none.
    Prefer favicon over meta image.
    """
    feed = Feed.objects.filter(pk=feed_pk).first()

    if not feed or feed.image_url:
        return

    if page_info := parse_page_info_from_url(url=feed.site_url):
        feed.image_url = page_info["favicon_url"] or page_info["image_url"] or None
        feed.save()
        print(f"Set image_url for '{feed}': {feed.image_url}")


@shared_task
def update_feed(feed_pk: int):
    """
    Fetch new entries for Feed.
    """
    if feed := Feed.objects.filter(pk=feed_pk).first():
        feed_update(feed=feed)


@shared_task
def download_entry_content(entry_pk: int):
    """
    Download entry content to disk using `wget`.
    """
    entry = Entry.objects.filter(pk=entry_pk).first()

    if entry:
        command_str = "wget --directory-prefix=./uploads/pages -x --mirror --convert-links --adjust-extension --page-requisites --no-parent {url}".format(
            url=entry.url
        )
        command = shlex.split(command_str)
        result = subprocess.run(command, capture_output=True)

        if result.returncode != 0:
            print("An error has occured running wget!")
            print(result.stdout.decode())
            return
        print(f"{entry} successfully downloaded.")

        # archive
        # tar -czvf ./uploads/pages.tar.gz ./uploads/pages
        # tar -czvf ./uploads/pages.tar.gz -C ./uploads/pages .

        # rm -rf ./uploads/pages dir
