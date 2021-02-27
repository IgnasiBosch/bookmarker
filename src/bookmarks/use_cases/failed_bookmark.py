from datetime import datetime, timezone

from src.db import database
from src.bookmarks.repos import bookmarks
from src.bookmarks.schemas import Bookmark
from src.config import settings


async def url_error(url: str):
    async with database.transaction():
        bm = await bookmarks.get(url=url)

        if bm is None:
            bm = Bookmark(url=url)

        bm.failed_attempts += 1
        bm.last_fetch_at = datetime.now(timezone.utc)

        if bm.failed_attempts >= settings.max_failed_url_extractions:
            bm.is_active = False

        await bookmarks.add(bm)
