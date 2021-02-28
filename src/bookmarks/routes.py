from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from src.auth.routes import get_current_session
from src.auth.schemas import Session
from src.bookmarks.repos import bookmarks
from src.bookmarks.schemas import Bookmark, PaginationParams, Url, OrderedBy
from src.bookmarks.use_cases.add_bookmark import add_urls

router = APIRouter()


@router.get("/api/bookmarks", response_model=List[Bookmark])
async def bookmarks_handler(
    current_page: int = Query(default=1),
    items_per_page: int = Query(default=10),
    order_by: Optional[OrderedBy] = Query(default=OrderedBy.last_fetch_desc),
    session: Session = Depends(get_current_session),
):
    pagination = PaginationParams(
        current_page=current_page, items_per_page=items_per_page, order_by=order_by
    )
    return await bookmarks.all(pagination)


@router.post("/api/bookmarks", response_model=Bookmark)
async def add_bookmark_handler(
    url: Url,
    session: Session = Depends(get_current_session),
):
    bms = await add_urls([url.url])
    return next(iter(bms))
