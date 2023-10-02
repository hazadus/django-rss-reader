import time
from io import BytesIO

import feedparser
import requests

FEED_URLS = [
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
    "http://www.b-list.org/feeds/entries",
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
]

TAGS = []


def read_feed(url: str):
    # Do request using requests library and timeout
    try:
        response = requests.get(url, timeout=10.0)
    except requests.exceptions.ConnectTimeout:
        print("Timeout when reading RSS %s", url)
        return None
    except requests.exceptions.ConnectionError:
        print("Failed to resolve %s", url)
        return None

    # Put it to memory stream object universal feedparser
    content = BytesIO(response.content)

    # Parse content
    return feedparser.parse(content)


def print_feed(feed):
    print("Title:", feed.channel.get("title"))
    print("URL..:", feed.channel.get("link"))

    image = feed.channel.get("image")
    print("Image:", image)

    print("")
    for item in feed.entries:
        print("-" * 120)
        print("Title:", item.get("title"), "\n")
        print("Description:", item.get("description"), "\n")
        print("Link:", item.get("link"), "\n")
        print("Published:", item.get("published"), "\n")
        print("Updated:", item.get("updated"), "\n")
        print("Author:", item.get("author"), "\n")
        print("Id:", item.get("id"), "\n")
        print("Guidislink:", item.get("guidislink"), "\n")
        print("Summary:", item.get("summary"), "\n")
        print("Content:", item.get("content"), "\n")

        tags = item.get("tags")
        if tags:
            print("Tags:", tags, "\n")
            for tag_item in tags:
                term: str = tag_item["term"]
                if term:
                    TAGS.append(term.replace(",", "").lstrip().rstrip().capitalize())


start_time = time.time()
total_items = 0
for feed_url in FEED_URLS:
    feed = read_feed(feed_url)
    if feed:
        total_items += len(feed.entries)
        print_feed(feed)

print("-" * 120)
print("All tags: ", ", ".join(set(TAGS)))
print("\nTotal items fetched:", total_items)
print("--- Completed in: %s seconds ---" % (time.time() - start_time))
