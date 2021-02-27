from datetime import datetime, timezone

from src.db import database
from src.repos import bookmarks
from src.schemas import Bookmark

MAX_FAILED_ERRORS = 5


async def url_error(url: str):
    async with database.transaction():
        bm = await bookmarks.get(url=url)

        if bm is None:
            bm = Bookmark(url=url)

        bm.failed_attempts += 1
        bm.last_fetch_at = datetime.now(timezone.utc)

        if bm.failed_attempts >= MAX_FAILED_ERRORS:
            bm.is_active = False

        await bookmarks.add(bm)
