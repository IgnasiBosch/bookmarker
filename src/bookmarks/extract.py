import json
import os
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Optional, Dict, Callable

from bs4 import Tag, BeautifulSoup
from httpx import HTTPError
from pydantic import AnyUrl

from src.bookmarks.schemas import Source, Bookmark
from src.bookmarks.use_cases.failed_bookmark import url_error
from src.bookmarks.utils import fetch_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_attr_or_none(tag: Optional[Tag], attr: str):
    if tag is None:
        return None

    return tag.get(attr)


def generic_extractor(page: BeautifulSoup, url: str) -> Bookmark:
    author = get_attr_or_none(
        page.find(attrs={"name": "author"}), "content"
    ) or get_attr_or_none(page.find(attrs={"name": "twitter:creator"}), "content")

    info = {
        "title": get_attr_or_none(page.find(attrs={"property": "og:title"}), "content"),
        "url": url,
        "description": get_attr_or_none(
            page.find(attrs={"property": "og:description"}), "content"
        ),
        "image_url": get_attr_or_none(
            page.find(attrs={"property": "og:image"}), "content"
        ),
        "author": author,
        "source": Source.OTHER,
        "last_fetch_at": datetime.now(timezone.utc),
        "failed_attempts": 0,
    }

    return Bookmark(**info)


def undefined_extractor(page: BeautifulSoup, url: str) -> Bookmark:
    author = get_attr_or_none(
        page.find(attrs={"name": "author"}), "content"
    ) or get_attr_or_none(page.find(attrs={"name": "twitter:creator"}), "content")

    info = {
        "title": get_attr_or_none(page.find(attrs={"property": "og:title"}), "content"),
        "url": url,
        "description": get_attr_or_none(
            page.find(attrs={"property": "og:description"}), "content"
        ),
        "image_url": get_attr_or_none(
            page.find(attrs={"property": "og:image"}), "content"
        ),
        "author": author,
        "source": Source.UNDEFINED,
        "last_fetch_at": datetime.now(timezone.utc),
        "failed_attempts": 0,
    }

    return Bookmark(**info)


def image_extractor(_, url: str) -> Bookmark:
    info = {
        "url": url,
        "image_url": url,
        "source": Source.IMAGE,
        "last_fetch_at": datetime.now(timezone.utc),
        "failed_attempts": 0,
    }

    return Bookmark(**info)


def google_books_extractor(page: BeautifulSoup, url: str) -> Bookmark:
    info = {
        "title": get_attr_or_none(page.find(attrs={"property": "og:title"}), "content"),
        "url": url,
        "description": get_attr_or_none(
            page.find(attrs={"property": "og:description"}), "content"
        ),
        "image_url": get_attr_or_none(
            page.find(attrs={"property": "og:image"}), "content"
        ),
        "author": None,
        "source": Source.GOOGLE_BOOKS,
        "last_fetch_at": datetime.now(timezone.utc),
        "failed_attempts": 0,
    }

    return Bookmark(**info)


def medium_extractor(page: BeautifulSoup, url: str) -> Bookmark:
    info = {
        "title": get_attr_or_none(page.find(attrs={"property": "og:title"}), "content"),
        "url": url,
        "description": get_attr_or_none(
            page.find(attrs={"property": "og:description"}), "content"
        ),
        "image_url": get_attr_or_none(
            page.find(attrs={"property": "og:image"}), "content"
        ),
        "author": get_attr_or_none(page.find(attrs={"name": "author"}), "content"),
        "source": Source.MEDIUM,
        "last_fetch_at": datetime.now(timezone.utc),
        "failed_attempts": 0,
    }

    return Bookmark(**info)


def youtube_extractor(page: BeautifulSoup, url: str) -> Bookmark:
    inner_infos = page.find_all("script")
    parsed_info = {}
    image_url = None
    description = None
    for inner_info in inner_infos:
        if "var ytInitialPlayerResponse" in str(inner_info):
            content = inner_info.contents[0][29:-1]
            parsed_content = json.loads(content)
            parsed_info = parsed_content.get("videoDetails")
            thumbnail = parsed_info.get("thumbnail")["thumbnails"][0]["url"]
            image_url = thumbnail[: thumbnail.index("?")]
            description = parsed_info.get("shortDescription")
            break
        if "var ytInitialData" in str(inner_info):
            content = inner_info.contents[0][20:-1]
            parsed_content = json.loads(content)
            parsed_info = parsed_content.get("metadata")["channelMetadataRenderer"]
            image_url = parsed_info["avatar"]["thumbnails"][-1]["url"]
            description = parsed_info.get("shortDescription")
            break

    info = {
        "title": parsed_info.get("title"),
        "url": url,
        "description": description,
        "image_url": image_url,
        "author": parsed_info.get("author"),
        "source": Source.YOUTUBE,
        "last_fetch_at": datetime.now(timezone.utc),
        "failed_attempts": 0,
    }

    return Bookmark(**info)


def github_extractor(page: BeautifulSoup, _) -> Bookmark:
    author, title = get_attr_or_none(
        page.find(attrs={"property": "og:title"}), "content"
    ).split("/")

    info = {
        "title": title,
        "url": get_attr_or_none(page.find(attrs={"property": "og:url"}), "content"),
        "description": get_attr_or_none(
            page.find(attrs={"property": "og:description"}), "content"
        ),
        "image_url": "https://clickhelp.com/images/feeds/blog/2018.06/hero_github.png",
        "author": author,
        "source": Source.GITHUB,
        "last_fetch_at": datetime.now(timezone.utc),
        "failed_attempts": 0,
    }

    return Bookmark(**info)


def get_source(page: BeautifulSoup, content_type: str) -> Source:
    if "image" in content_type:
        return Source.IMAGE
    source = get_attr_or_none(page.find(attrs={"property": "og:site_name"}), "content")
    if source is None:
        return Source.UNDEFINED

    try:
        return Source(source.lower())
    except Exception:
        return Source.OTHER


extractors: Dict[Source, Callable[[BeautifulSoup, str], Bookmark]] = {
    Source.MEDIUM: medium_extractor,
    Source.GITHUB: github_extractor,
    Source.GOOGLE_BOOKS: google_books_extractor,
    Source.IMAGE: image_extractor,
    Source.OTHER: generic_extractor,
    Source.UNDEFINED: undefined_extractor,
    Source.YOUTUBE: youtube_extractor,
}


async def scrape_url(url: AnyUrl) -> Optional[Bookmark]:
    try:
        resp = await fetch_url(url)
        content_type = resp.headers.get("content-type")

        if resp.status_code == HTTPStatus.OK:
            page = BeautifulSoup(resp.text, "html.parser")
            source = get_source(page, content_type)
            extractor = extractors[source]
            return extractor(page, url)
        elif resp.status_code == HTTPStatus.GONE:
            print(f"Content removed: {url}")
        else:
            print(f"Other response status {resp.status_code}: {url}")

        await url_error(url)

    except HTTPError as exc:
        print(f"Fetch error {url}: {exc}")
        await url_error(url)
    except Exception as exc:
        print(f"Unexpected error {url} : {exc}")

    return None
