from uuid import UUID

from src.bookmarks.exceptions import BookmarkNotFound
from src.bookmarks.repos import bookmarks
from src.db import database


async def delete_bookmark(id: UUID):
    async with database.transaction():
        bm = await bookmarks.get(id=id)

        if bm is None:
            raise BookmarkNotFound

        await bookmarks.delete(bm)

        return bm
