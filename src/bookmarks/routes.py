from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.auth.routes import get_current_session
from src.auth.schemas import Session
from src.bookmarks.repos import bookmarks
from src.bookmarks.schemas import (
    Bookmark,
    BookmarkFilter,
    BookmarkStats,
    OrderedBy,
    PaginationParams,
    Url,
    OrderParams,
    BookmarkResponse,
)
from src.bookmarks.use_cases import add_urls, get_stats
from src.bookmarks.use_cases.delete_bookmark import delete_bookmark
from src.common.repos import get_pagination

router = APIRouter()

DEFAULT_ITEMS_PER_PAGE = 10


@router.get("/api/bookmarks", response_model=BookmarkResponse)
async def bookmarks_handler(
    current_page: int = Query(default=1),
    items_per_page: int = Query(default=DEFAULT_ITEMS_PER_PAGE),
    order_by: Optional[OrderedBy] = Query(default=OrderedBy.last_fetch_desc),
    session: Session = Depends(get_current_session),
):
    order_params = OrderParams(order_by=order_by)
    pagination = PaginationParams(
        current_page=current_page, items_per_page=items_per_page
    )
    filter_params = BookmarkFilter(only_fetched=True)
    items = await bookmarks.all(
        order_params=order_params, filter_params=filter_params, pagination=pagination
    )

    total_num_items = await bookmarks.count(filter_params=filter_params)
    pagination = get_pagination(
        current_page=pagination.current_page,
        items_per_page=pagination.items_per_page,
        total_num_items=total_num_items,
    )

    return BookmarkResponse(items=items, pagination=pagination)


@router.get("/api/bookmarks/stats", response_model=BookmarkStats)
async def bookmarks_stats_handler(
    session: Session = Depends(get_current_session),
):
    return await get_stats()


@router.post("/api/bookmarks", response_model=Bookmark)
async def add_bookmark_handler(
    url: Url,
    session: Session = Depends(get_current_session),
):
    bms = await add_urls([url.url])
    return next(iter(bms))


@router.delete("/api/bookmarks/{id}", response_model=Bookmark)
async def delete_bookmark_handler(
    id: UUID,
    session: Session = Depends(get_current_session),
):
    return await delete_bookmark(id)
