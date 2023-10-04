import logging
import time

from django.core.management.base import BaseCommand

from feeds.services import feed_subscribe
from users.models import CustomUser

logger = logging.getLogger(__name__)

FEED_URLS = [
    "https://hazadus.ru",
    "http://adamj.eu/tech/atom.xml",
    "https://antfu.me/feed.xml",
    "https://www.apollographql.com/blog/rss.xml",
    "https://www.bencodezen.io/rss.xml",
    "https://www.better-simple.com/atom.xml",
    "https://brntn.me/rss/",
    "https://css-tricks.com/feed/",
    "https://daniel.feldroy.com/feeds/atom.xml",
    "https://www.digitalocean.com/community/articles/feed.atom",
    "https://www.freecodecamp.org/news/rss/",
    "https://joshcollinsworth.com/api/rss.xml",
    "https://www.joshwcomeau.com/rss.xml",
    "https://martinfowler.com/feed.atom",
    "https://mokkapps.de/rss.xml",
    "https://quickwit.io/blog/rss.xml",
    "https://realpython.com/atom.xml",
    "https://www.stefanjudis.com/rss.xml",
    "http://www.snarky.ca/feed",
    "http://testdriven.io/feed.xml",
    "https://github.com/blog/all.atom",
    "https://github.com/readme.rss",
    "https://this-week-in-rust.org/rss.xml",
    "http://blog.wesleyac.com/feed.xml",
    "https://www.macworld.com/feed",
    "http://www.residentadvisor.net/xml/review-album.xml",
    "https://teletype.in/rss/temalebedev",
    "https://autoreview.ru/feed/news/rss",
    "http://www.3dnews.ru/news/main/rss",
    "https://www.mirf.ru/feed",
    "http://stopgame.ru/rss/rss_news.xml",
    "https://dtf.ru/rss/all",
    "http://feeds.howtogeek.com/HowToGeek",
    "http://disgustingmen.com/feed/",
]


class Command(BaseCommand):
    """
    Load default feeds for debug purposes.
    """

    help = """
    Load default feeds for debug purposes. 
    """

    def handle(self, *args, **options):
        """
        Handles the flow of the command.
        """
        user = CustomUser.objects.get(email="hazadus7@gmail.com")

        start_time = time.time()
        total_items = 0
        for feed_url in FEED_URLS:
            feed_instance = feed_subscribe(user=user, feed_url=feed_url)
            if feed_instance:
                total_items += 1
                logger.info("Created subscription to feed: %s", feed_instance)

        logger.info("Total items fetched: %s", total_items)
        logger.info("--- Completed in: %s seconds ---" % (time.time() - start_time))