import logging
import time

from django.core.management.base import BaseCommand

from feeds.services import CantSubscribeToFeed, feed_subscribe
from users.models import CustomUser

logger = logging.getLogger(__name__)

FEED_URLS = [
    "https://hazadus.ru/rss.xml",
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
    "http://www.residentadvisor.net/xml/review-album.xml",
    "http://www.residentadvisor.net/xml/features.xml",
    "http://www.residentadvisor.net/xml/review-single.xml",
    "https://teletype.in/rss/temalebedev",
    "https://autoreview.ru/feed/news/rss",
    "http://www.3dnews.ru/news/main/rss",
    "http://www.3dnews.ru/video/rss/",
    "http://www.3dnews.ru/cooling/rss/",
    "http://www.3dnews.ru/display/rss/",
    "http://www.3dnews.ru/mobile/rss/",
    "http://www.3dnews.ru/smart-things/rss/",
    "https://www.mirf.ru/feed",
    "http://stopgame.ru/rss/rss_news.xml",
    "http://stopgame.ru/rss/rss_review.xml",
    "http://stopgame.ru/rss/rss_preview.xml",
    "https://dtf.ru/rss/all",
    "http://feeds.feedburner.com/RockPaperShotgun",
    "http://igromania.ru/rss/rss_articles.xml",
    "http://torick.ru/feed/",
    "http://feeds.howtogeek.com/HowToGeek",
    "https://www.macworld.com/feed",
    "https://surface-pro.ru/feed/",
    "http://disgustingmen.com/feed/",
    "https://blog.rabbitmq.com/index.xml",
    "https://wsvincent.com/feed.xml",
    "https://blog.miguelgrinberg.com/feed",
    "https://www.djangoproject.com/rss/weblog/",
    "https://django-news.com/issues.rss",
    "http://tonsky.me/blog/atom.xml",
    "https://www.blog.pythonlibrary.org/feed/",
    "https://pxlnv.com/feed",
    "https://thesweetsetup.com/feed",
    "https://www.macstories.net/feed/",
    "https://inessential.com/xml/rss.xml",
    "https://jacobian.org/feed/",
]


class Command(BaseCommand):
    """
    Create initial hard-coded feeds for superuser.
    """

    help = """
    Create initial hard-coded feeds for superuser.
    """

    def handle(self, *args, **options):
        """
        Handles the flow of the command.
        """
        user = CustomUser.objects.filter(is_superuser=True).first()

        if not user:
            logger.error("Create a superuser before running `add_feeds`!")
            return

        start_time = time.time()
        total_feeds = 0
        logger.info("Creating feed subscriptions for '%s'", user)

        for feed_url in FEED_URLS:
            try:
                feed_instance = feed_subscribe(user=user, feed_url=feed_url)
                total_feeds += 1
                logger.info("Created subscription to feed: %s", feed_instance)
            except CantSubscribeToFeed:
                logger.warning("Can't subscribe to feed URL %s", feed_url)

        logger.info("Total feed subscriptions created: %s", total_feeds)
        logger.info("--- Completed in: %s seconds ---" % (time.time() - start_time))
