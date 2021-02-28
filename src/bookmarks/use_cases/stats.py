from src.bookmarks.repos import bookmarks
from src.bookmarks.schemas import BookmarkFilter, BookmarkStats


async def get_stats() -> BookmarkStats:

    total = await bookmarks.count()
    pending = await bookmarks.count(
        BookmarkFilter(
            pending_to_fetch=True,
        )
    )
    inactive = await bookmarks.count(
        BookmarkFilter(
            is_active=False,
        )
    )
    available = total - pending - inactive

    return BookmarkStats(
        pending=pending,
        total=total,
        inactive=inactive,
        available=available
    )
