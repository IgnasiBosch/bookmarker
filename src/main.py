from http import HTTPStatus

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import (
    FileResponse,
    RedirectResponse,
    JSONResponse,
)
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.auth.use_cases.session import prune_old_sessions
from src.bookmarks.use_cases.add_bookmark import update_urls
from src.config import settings
from src.db import database
from src.auth.routes import router as auth_router
from src.bookmarks.routes import router as bookmark_router


additional_cnf = {}
if not settings.debug:
    additional_cnf["openapi_url"] = None

app = FastAPI(debug=settings.debug, **additional_cnf)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    if exc.status_code == HTTPStatus.NOT_FOUND:
        response = RedirectResponse(url="/")
        return response
    if exc.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        if settings.debug:
            raise exc

        return JSONResponse({"status": "Oops"}, status_code=exc.status_code)

    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.on_event("startup")
async def db_connect():
    await database.connect()


@app.on_event("startup")
@repeat_every(
    seconds=settings.run_refresh_url_task_every_seconds,
    wait_first=True,
    raise_exceptions=True,
)
async def clean_sessions():
    await prune_old_sessions()


@app.on_event("startup")
@repeat_every(
    seconds=settings.run_refresh_url_task_every_seconds, raise_exceptions=True
)
async def fetch_urls():
    await update_urls()


@app.on_event("shutdown")
async def db_disconnect():
    await database.disconnect()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
async def home():
    return FileResponse("public/index.html")


app.include_router(auth_router)
app.include_router(bookmark_router)
