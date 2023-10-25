from celery import shared_task

from feeds.models import Feed
from feeds.utils import parse_page_info_from_url


@shared_task
def get_image_for_feed(feed_pk: int):
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
