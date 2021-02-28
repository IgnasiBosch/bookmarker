from typing import Optional, Iterable
from uuid import UUID

from sqlalchemy import or_, and_, func
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Query
from sqlalchemy.sql import Insert

from src.db import database
from src.bookmarks.schemas import Bookmark, BookmarkFilter, PaginationParams, OrderedBy
from src.bookmarks.tables import bookmarks


async def add(bookmark: Bookmark) -> Bookmark:
    query = bookmarks.insert(on_duplicate_key_update=True).values(
        **bookmark.dict(exclude_none=True)
    )
    _ = await database.execute(query)
    return bookmark


async def all(
    filter_params: Optional[BookmarkFilter] = None,
    pagination: Optional[PaginationParams] = None,
) -> Iterable[Bookmark]:
    query = filtered_query(filter_params=filter_params, pagination=pagination)
    result = await database.fetch_all(query)
    return (Bookmark(**dict(r)) for r in result)


async def count(filter_params: Optional[BookmarkFilter] = None) -> int:
    query = filtered_query(filter_params=filter_params).alias("t").count()
    rs = await database.fetch_one(query)
    return rs.tbl_row_count


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

    where_clause = or_(*filters)

    query = (
        bookmarks.select().where(where_clause).order_by(bookmarks.c.last_fetch_at.asc())
    )
    result = await database.fetch_one(query)
    if result:
        return Bookmark(**dict(result))
    else:
        return None


def filtered_query(
    filter_params: Optional[BookmarkFilter] = None,
    pagination: Optional[PaginationParams] = None,
) -> Query:
    filter_params = filter_params or BookmarkFilter()

    filters = []
    if filter_params.last_fetched_before:
        filters.append(bookmarks.c.last_fetch_at <= filter_params.last_fetched_before)
    if filter_params.source:
        filters.append(bookmarks.c.source == filter_params.source)
    if filter_params.author:
        filters.append(bookmarks.c.author == filter_params.author)
    if filter_params.is_active is not None:
        filters.append(bookmarks.c.is_active == filter_params.is_active)
    if filter_params.is_read is not None:
        filters.append(bookmarks.c.is_read == filter_params.is_read)

    where_clause = and_(*filters) if filters else None

    if filter_params.only_fetched:
        w = and_(bookmarks.c.last_fetch_at != None, bookmarks.c.is_active == True)
        if where_clause is not None:
            where_clause = or_(where_clause, w)
        else:
            where_clause = w


    if filter_params.pending_to_fetch:
        w = and_(bookmarks.c.last_fetch_at == None, bookmarks.c.is_active == True)
        if where_clause is not None:
            where_clause = or_(where_clause, w)
        else:
            where_clause = w

    query = bookmarks.select()

    if where_clause is not None:
        query = query.where(where_clause)

    if pagination:
        query = query.limit(pagination.items_per_page).offset(
            (pagination.current_page - 1) * pagination.items_per_page
        )

        if pagination.order_by == OrderedBy.random:
            query = query.order_by(func.rand())
        elif pagination.order_by == OrderedBy.last_fetch_asc:
            query = query.order_by(bookmarks.c.last_fetch_at, bookmarks.c.id)
        elif pagination.order_by == OrderedBy.last_fetch_desc:
            query = query.order_by(bookmarks.c.last_fetch_at.desc(), bookmarks.c.id)
        else:
            query = query.order_by(bookmarks.c.last_fetch_at.desc(), bookmarks.c.id)

    return query


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
