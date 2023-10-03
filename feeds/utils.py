import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def parse_meta_from_url(url: str) -> dict | None:
    """
    Parse meta tags from `url`.

    :param str url: URL to parse meta tags from.
    :return: `{"title": "...", "description": "...", "image_url": "..."}` on success, or None otherwise.
    """
    try:
        response = requests.get(url, timeout=5.0)
        html = BeautifulSoup(response.content, "html.parser")
    except Exception:
        logger.error("Failed to get content from %s", url)
        return None

    title = html.title.string if html.title else "Unknown Title"
    description = html.find("meta", property="og:description")
    image_url = html.find("meta", property="og:image")

    return {
        "title": title if title else "No title set",
        "description": description["content"] if description else "",
        "image_url": image_url["content"] if image_url else "",
    }
