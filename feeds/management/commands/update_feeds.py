import logging
import time

from django.core.management.base import BaseCommand

from feeds.services import update_all_feeds

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Fetch entries and create new `Entry` instances for all feeds in the database.
    """

    help = """
    Fetch entries and create new `Entry` instances for all feeds in the database.
    """

    def handle(self, *args, **options):
        """
        Fetch entries and create new `Entry` instances for all feeds in the database.
        """
        start_time = time.time()
        update_all_feeds()
        logger.info("--- Completed in: %s seconds ---" % (time.time() - start_time))
