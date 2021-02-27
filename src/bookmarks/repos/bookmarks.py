from typing import Optional, Iterable
from uuid import UUID

from sqlalchemy import or_, and_
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import Insert

from src.db import database
from src.schemas import Bookmark, BookmarkFilter, PaginationParams
from src.tables import bookmarks


@compiles(Insert)
def append_string(insert, compiler, **kw):
    s = compiler.visit_insert(insert, **kw)
    if insert.kwargs.get("on_duplicate_key_update"):
        fields = s[s.find("(") + 1 : s.find(")")].replace(" ", "").split(",")
        generated_directive = [
            "{0}=VALUES({0})".format(field) for field in fields if field != "id"
        ]
        return s + " ON DUPLICATE KEY UPDATE " + ",".join(generated_directive)
    return s


async def add(bookmark: Bookmark):
    query = bookmarks.insert(on_duplicate_key_update=True).values(
        **bookmark.dict(exclude_none=True)
    )
    _ = await database.execute(query)
    return bookmark


async def all(pagination: Optional[PaginationParams] = None) -> Iterable[Bookmark]:
    query = bookmarks.select().order_by(bookmarks.c.last_fetch_at, bookmarks.c.id)

    if pagination:
        query = query.limit(pagination.items_per_page).offset(
            pagination.current_page * pagination.items_per_page
        )

    result = await database.fetch_all(query)
    return (Bookmark(**dict(r)) for r in result)


async def get(
    id: Optional[UUID] = None, url: Optional[str] = None
) -> Optional[Bookmark]:
    if id is None and url is None:
        raise ValueError("Id or Url are needed to get a bookmark entry")

    filters = []
    if id:
        filters.append(bookmarks.c.id == id)
    if url:
        bm = Bookmark(url=url)
        filters.append(bookmarks.c.url_hash == bm.url_hash)

    query = bookmarks.select().where(*filters).order_by(bookmarks.c.last_fetch_at.asc())
    result = await database.fetch_one(query)
    if result:
        return Bookmark(**dict(result))
    else:
        return None


async def filter(
    filter_params: BookmarkFilter, pagination: Optional[PaginationParams] = None
) -> Iterable[Bookmark]:
    filters = []
    if filter_params.last_fetched_before:
        filters.append(bookmarks.c.last_fetch_at <= filter_params.last_fetched_before)
    if filter_params.source:
        filters.append(bookmarks.c.source == filter_params.source)
    if filter_params.author:
        filters.append(bookmarks.c.author == filter_params.author)
    if filter_params.is_active:
        filters.append(bookmarks.c.is_active == filter_params.is_active)
    if filter_params.is_read:
        filters.append(bookmarks.c.is_read == filter_params.is_read)

    where_clause = and_(*filters)

    if filter_params.pending_to_fetch:
        where_clause = or_(where_clause, bookmarks.c.last_fetch_at == None)

    query = (
        bookmarks.select()
        .where(where_clause)
        .order_by(bookmarks.c.last_fetch_at, bookmarks.c.id)
    )

    if pagination:
        query = query.limit(pagination.items_per_page).offset(
            pagination.current_page * pagination.items_per_page
        )

    result = await database.fetch_all(query)
    return (Bookmark(**dict(r)) for r in result)
