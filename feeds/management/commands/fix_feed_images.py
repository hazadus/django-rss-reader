import logging
import time

from django.core.management.base import BaseCommand

from feeds.models import Feed
from feeds.utils import parse_meta_from_url

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Find and set image URLs for Feeds without those.
    """

    help = """
    Find and set image URLs for Feeds without those.
    """

    def handle(self, *args, **options):
        """
        Handles the flow of the command.
        """
        feeds = Feed.objects.all()

        start_time = time.time()
        total_feeds = 0
        for feed in feeds:
            if not feed.image_url:
                logger.info("Feed '%s' has no image", feed)
                meta = parse_meta_from_url(url=feed.site_url)
                # logger.info("Meta: %s", meta)

        logger.info("Total feeds ...: %s", total_feeds)
        logger.info("--- Completed in: %s seconds ---" % (time.time() - start_time))
