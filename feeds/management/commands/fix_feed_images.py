import logging
import time

from django.core.management.base import BaseCommand

from feeds.models import Feed
from feeds.utils import parse_page_info_from_url

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Find and set image URLs for Feeds without those.
    Use favicon, if there's one, otherwise image from page meta.
    """

    help = """
    Find and set image URLs for Feeds without those.
    Use favicon, if there's one, otherwise image from page meta.
    """

    def handle(self, *args, **options):
        """
        Handles the flow of the command.
        """
        feeds = Feed.objects.filter(image_url=None)

        start_time = time.time()
        total_feeds = 0
        for feed in feeds:
            logger.info("Feed '%s' has no image", feed)
            info = parse_page_info_from_url(url=feed.site_url)
            # Use favicon first, or meta image otherwise
            image_url = info.get("favicon_url") or info.get("image_url") or None
            if image_url:
                feed.image_url = image_url
                feed.save()
                total_feeds += 1
                logger.info("Image set: %s", image_url)

        logger.info("Total feeds updated: %s", total_feeds)
        logger.info("--- Completed in: %s seconds ---" % (time.time() - start_time))
