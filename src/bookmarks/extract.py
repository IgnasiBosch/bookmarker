import logging
from http import HTTPStatus
from typing import Optional

from httpx import HTTPError
from pydantic import AnyUrl

from src.bookmarks.extractors import extractor_factory
from src.bookmarks.schemas import Bookmark
from src.bookmarks.use_cases.failed_bookmark import url_error
from src.bookmarks.utils import fetch_url

logger = logging.getLogger(__name__)


async def scrape_url(url: AnyUrl) -> Optional[Bookmark]:
    try:
        resp = await fetch_url(url)

        if resp.status_code == HTTPStatus.OK:
            content_type = resp.headers.get("content-type")
            content = resp.text
            extractor = extractor_factory(
                url=url, content=content, content_type=content_type
            )
            return extractor.to_bookmark()
        elif resp.status_code == HTTPStatus.GONE:
            logger.debug(f"Content removed: {url}")
        else:
            logger.debug(f"Other response status {resp.status_code}: {url}")

        await url_error(url)

    except HTTPError as exc:
        logger.debug(f"Fetch error {url}: {exc}")
        await url_error(url)
    except Exception as exc:
        logger.debug(f"Unexpected error {url} : {exc}")
        await url_error(url)

    return None
