import logging
import time

from django.core.management.base import BaseCommand

from feeds.services import feed_subscribe
from users.models import CustomUser

logger = logging.getLogger(__name__)

USERS_SUBSCTIPTIONS = [
    {
        "username": "anonymous",
        "email": "anon@mail.com",
        "password": "12345678",
        "is_superuser": True,
        "feeds": [
            "https://hazadus.ru/rss.xml",
            "https://css-tricks.com/feed/",
            "https://daniel.feldroy.com/feeds/atom.xml",
            "https://this-week-in-rust.org/rss.xml",
            "http://www.residentadvisor.net/xml/review-album.xml",
            "https://surface-pro.ru/feed/",
        ],
    },
    {
        "username": "unknown",
        "email": "unknown@mail.com",
        "password": "12345678",
        "is_superuser": False,
        "feeds": [
            "http://www.residentadvisor.net/xml/review-album.xml",
            "http://www.residentadvisor.net/xml/features.xml",
            "http://www.residentadvisor.net/xml/review-single.xml",
            "http://torick.ru/feed/",
            "https://hazadus.ru/rss.xml",
        ],
    },
]


class Command(BaseCommand):
    """
    Create two users and add some subscriptions for them.
    This command is designed to create data for test fixtures.
    """

    help = """
    Create two users and add some subscriptions for them.
    This command is designed to create data for test fixtures.
    """

    def handle(self, *args, **options):
        """
        Handles the flow of the command.
        """
        start_time = time.time()

        for user_sub in USERS_SUBSCTIPTIONS:
            user = CustomUser.objects.create_user(
                username=user_sub["username"],
                email=user_sub["email"],
                password=user_sub["password"],
                is_superuser=user_sub["is_superuser"],
            )
            logging.info("Created user '%s'", user)

            total_feeds = 0
            logger.info("-- Creating feed subscriptions for '%s'", user)
            for feed_url in user_sub["feeds"]:
                feed_instance = feed_subscribe(user=user, feed_url=feed_url)
                if feed_instance:
                    total_feeds += 1
                    logger.info("-- Created subscription to feed: %s", feed_instance)

            logger.info("-- Created %s feed subscriptions for '%s'", total_feeds, user)

        logger.info("--- Done in: %s sec ---", round((time.time() - start_time), 2))
