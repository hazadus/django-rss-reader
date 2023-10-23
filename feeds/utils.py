import logging
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def parse_best_favicon_url(html: BeautifulSoup, host_url: str) -> str | None:
    """
    TODO:
    """
    icons = []
    link_tags = html.find_all("link", attrs={"rel": re.compile(".*icon.*", re.I)})
    for link_tag in link_tags:
        href = str(link_tag.get("href"))
        rel = link_tag.get("rel")
        sizes = link_tag.get("sizes", None)

        # Make absolute url
        if not href.startswith("http"):
            href = host_url + href[1:]

        # Get size in pixels
        size = None
        if sizes:
            size = str(sizes).split("x")[0]

        logger.info("%s", "-" * 80)
        logger.info("href.: %s", href)
        logger.info("rel..: %s", rel)
        logger.info("size.: %s", size)

        # Add to `icons`: {href, rel, type, size}
        icons.append(
            {
                "href": href,
                "rel": rel,
                "size": size,
            },
        )

    # Choose best icon from `icons` list
    logger.error("icons: %s", str(icons))
    return None


def parse_meta_from_url(url: str) -> dict | None:
    """
    Parse meta tags from `url`.
    TODO: +favicon stuff

    :param str url: URL to parse meta tags from.
    :return: `{"title": "...", "description": "...", "image_url": "..."}` on success, or None otherwise.
    """
    try:
        response = requests.get(url, timeout=5.0)
        html = BeautifulSoup(response.content, "html.parser")
    except Exception as exc:
        logger.exception(f"Failed to get content from {url}", exc_info=exc)
        return None

    # We need host url to build full link to favicon in case it presented
    # in <link> tag as relative URL.
    parsed_uri = urlparse(url)
    host_url = "{uri.scheme}://{uri.netloc}/".format(uri=parsed_uri)

    title = html.title.string if html.title else "Unknown Title"
    description = html.find("meta", property="og:description")
    image_url = html.find("meta", property="og:image")
    favicon_url = parse_best_favicon_url(html=html, host_url=host_url)

    return {
        "title": title if title else "No title set",
        "description": description["content"] if description else "",
        "image_url": image_url["content"] if image_url else "",
        "favicon_url": favicon_url,
    }
