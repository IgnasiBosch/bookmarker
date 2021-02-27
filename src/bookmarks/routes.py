from typing import List

from fastapi import APIRouter, Depends

from src.auth.routes import get_current_session
from src.auth.schemas import Session
from src.bookmarks.repos import bookmarks
from src.bookmarks.schemas import Bookmark, PaginationParams

router = APIRouter()


@router.get("/api/bookmarks", response_model=List[Bookmark])
async def bookmarks_handle(
    session: Session = Depends(get_current_session),
):
    pagination = PaginationParams(current_page=1, items_per_page=50)
    return await bookmarks.all(pagination)


# @app.post("/notes/", response_model=Note)
# async def create_note(note: NoteIn):
#     query = notes.insert().values(text=note.text, completed=note.completed)
#     last_record_id = await database.execute(query)
#     return {**note.dict(), "id": last_record_id}
