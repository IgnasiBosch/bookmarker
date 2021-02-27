from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from dateutil.relativedelta import relativedelta

from src.db import database
from src.fetch import scrape_url
from src.repos import bookmarks
from src.schemas import BookmarkFilter, Bookmark, PaginationParams
from src.utils import read_json_file

NUM_FETCH_ENTRIES = 20


async def add_urls(urls: Iterable[str]):
    async with database.transaction():
        for url in urls:
            await bookmarks.add(Bookmark(url=url))


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
        last_fetched_before=datetime.now(timezone.utc) - relativedelta(months=1),
    )

    pagination = PaginationParams(current_page=1, items_per_page=NUM_FETCH_ENTRIES)
    entries = await bookmarks.filter(filter_params, pagination)

    # bm = await bookmarks.get(url="https://www.youtube.com/channel/UCRF82wX0EPwqvKMBwvB4fQg/videos")
    # entries = [bm]

    for bookmark in entries:
        print(f"Scraping... {bookmark.url}")
        bm = await scrape_url(bookmark.url)
        if bm is None:
            continue
        await bookmarks.add(bm)
