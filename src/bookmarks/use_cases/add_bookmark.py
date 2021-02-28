import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from dateutil.relativedelta import relativedelta

from src.db import database
from src.bookmarks.extract import scrape_url
from src.bookmarks.repos import bookmarks
from src.bookmarks.schemas import BookmarkFilter, Bookmark, PaginationParams
from src.bookmarks.utils import read_json_file
from src.bookmarks.use_cases.failed_bookmark import url_error
from src.config import settings

logger = logging.getLogger(__name__)


async def add_urls(urls: Iterable[str]) -> Iterable[Bookmark]:
    created_bookmarks = []
    async with database.transaction():
        for url in urls:
            bm = await bookmarks.add(Bookmark(url=url))
            created_bookmarks.append(bm)

    return created_bookmarks


async def import_urls_from_browser_bookmarks(path: Path):
    contents = await read_json_file(path)

    def get_urls(node):
        if "children" in node:
            for entry in node["children"]:
                if "children" in entry:
                    yield from get_urls(node["children"])
                elif "uri" in entry:
                    yield entry["uri"]

    urls = get_urls(contents)
    await add_urls(urls)


async def update_urls():
    filter_params = BookmarkFilter(
        is_active=True,
        pending_to_fetch=True,
        last_fetched_before=datetime.now(timezone.utc)
        - relativedelta(days=settings.refresh_urls_older_than_days),
    )

    pagination = PaginationParams(
        current_page=1, items_per_page=settings.batch_url_extractions
    )
    entries = await bookmarks.all(filter_params, pagination)

    for bookmark in entries:
        logger.info(f"Scraping... {bookmark.url}")
        bm = await scrape_url(bookmark.url)
        if bm is None:
            continue
        try:
            await bookmarks.add(bm)
        except Exception as exc:
            logger.error(f"Error when scrapping: {exc}")
            await url_error(bookmark.url)
