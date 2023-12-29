import logging
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from urllib3.exceptions import ReadTimeoutError

logger = logging.getLogger(__name__)


class CantGetPageInfoFromURL(Exception):
    """Some error has occured while trying to get page meta info and favicon."""

    pass


def check_url_status_code(
    url: str, status_code: int = 200, timeout: float = 5.0
) -> bool:
    """
    Try to GET page from `url` and check the status code.

    :param str url: URL to check status code for
    :param int status_code: expected HTTP status code
    :param int timeout: timeout to use in `request.get()` call, in seconds
    :return: True if resulting status code is equal to expected, False otherwise (or in case of error)
    """
    try:
        response = requests.get(url, timeout=timeout)
    except ReadTimeoutError as exc:
        logger.exception(f"Failed to request.get from {url}", exc_info=exc)
        return False

    if response.status_code == status_code:
        return True
    return False


def parse_link_tag(link_tag: Tag, host_url: str) -> dict:
    """
    Parse full URL and image size from link Tag, which in turn was parsed by BeautifulSoup
    from HTML document.

    :param Tag link_tag: <link> tag parsed by BeautifulSoup from HTML document.
    :param str host_url: host's full URL (e.g. http://hazadus.ru/), used to build full
                         URL of the icon file.
    :return: dict with link (str) and size (int), e.g. {"href": "http://hazadus.ru/image.png", "size": 192}
    """

    href = str(link_tag.get("href"))

    # Make absolute URL
    if not href.startswith("http"):
        href = host_url + href[1:]

    # Get size in pixels as integer
    size = 0
    if sizes := link_tag.get("sizes", None):
        try:
            # Sizes are presented as "192x192" string
            size = int(str(sizes).split("x")[0])
        except ValueError:
            size = 0

    return {"href": href, "size": size}


def parse_best_favicon_url(html: BeautifulSoup, host_url: str) -> str | None:
    """
    Parse URL of "best" favicon in `html` document.
    We assume that the "best" icon is the one with max "size" attribute, in case there's multiple
    links to icons in the document, with "sizes" attributes.

    :param BeautifulSoup html: HTML document parsed by BeautifulSoup
    :param str host_url: host's full URL (e.g. http://hazadus.ru/), used to build full
                         URL of the icon file.
    :return: full URL of the icon file, or None if there were no icons found. This URL is tested for
             accessibility (`requests.get()` on it returned 200).
    """
    icons = []
    # Parse all <link> tags, where "rel" attribute contains word "icon":
    link_tags = html.find_all("link", attrs={"rel": re.compile(".*icon.*", re.I)})

    # Parse each <link> tag found for icon's URL and size
    for link_tag in link_tags:
        # Add to `icons`: {href, size}
        icons.append(parse_link_tag(link_tag=link_tag, host_url=host_url))

    # No icon links found
    if not len(icons):
        return None

    # Multiple icons found - sort `icons` list by size in descending order.
    # We assume that the "best" icon is the one with max "size" attribute.
    if len(icons) > 1:
        icons = sorted(icons, key=lambda icon: icon.get("size"), reverse=True)

    url = icons[0]["href"]

    if check_url_status_code(url=url):
        return url
    return None


def parse_page_meta(html: BeautifulSoup, host_url: str) -> dict:
    """
    Parse page title and meta info - description, image - from `html` document.

    :param BeautifulSoup html: HTML document parsed by BeautifulSoup
    :param str host_url: host's full URL (e.g. http://hazadus.ru/), used to build full
                         URL of the image file.
    :return: dict `{"title": "...", "description": "...", "image_url": "...",}`.
    """
    title = html.title.string if html.title else "Unknown Title"
    description_soup = html.find("meta", property="og:description")
    image_url_soup = html.find("meta", property="og:image")

    image_url = ""
    if image_url_soup:
        image_url = image_url_soup["content"]
        if not image_url.startswith("http"):
            image_url = host_url + image_url[1:]

    return {
        "title": title,
        "description": description_soup["content"] if description_soup else "",
        "image_url": image_url,
    }


def parse_page_info_from_url(url: str) -> dict:
    """
    Parse meta info and favicon URL from `url`.

    :param str url: URL to parse meta tags and favicon link from.
    :return: `{"title": "...", "description": "...", "image_url": "...", "favicon_url": "..."}` on success,
             or None otherwise.
    :raises CantGetPageInfoFromURL: in case of any error.
    """
    # TODO: refactor return type to custom, e.g. PageInfo
    try:
        response = requests.get(url, timeout=5.0)
    except Exception as exc:
        logger.exception(f"Failed to get content from {url}", exc_info=exc)
        raise CantGetPageInfoFromURL

    html = BeautifulSoup(response.content, "html.parser")

    # We need host URL to build full link to favicon or image in case it is set as relative path.
    parsed_uri = urlparse(url)
    host_url = "{uri.scheme}://{uri.netloc}/".format(uri=parsed_uri)

    meta = parse_page_meta(html=html, host_url=host_url)
    favicon_url = parse_best_favicon_url(html=html, host_url=host_url)

    return {
        "title": meta["title"],
        "description": meta["description"],
        "image_url": meta["image_url"],
        "favicon_url": favicon_url,
    }
