import logging
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, JSONResponse, RedirectResponse

from src.auth.routes import router as auth_router
from src.auth.use_cases.session import prune_old_sessions
from src.bookmarks.routes import router as bookmark_router
from src.bookmarks.use_cases.add_bookmark import update_urls
from src.common.exceptions import BaseError
from src.config import settings
from src.db import database

logger = logging.getLogger(__name__)

additional_cnf = {}
if not settings.debug:
    additional_cnf["openapi_url"] = None

app = FastAPI(debug=settings.debug, **additional_cnf)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.ignasibosch.com",
        "http://localhost:8080",
        "http://localhost:8081",
    ],
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


@app.exception_handler(BaseError)
async def custom_errors_http_exception_handler(request, exc: BaseError):
    return JSONResponse(exc.to_json(), status_code=exc.status_code)


@app.on_event("startup")
async def connect_services():
    await database.connect()


# @app.on_event("startup")
# @repeat_every(
#     seconds=settings.run_refresh_url_task_every_seconds * 10,
#     wait_first=True,
#     raise_exceptions=True,
# )
# async def clean_sessions():
#     await prune_old_sessions()


# @app.on_event("startup")
# @repeat_every(
#     seconds=settings.run_refresh_url_task_every_seconds, raise_exceptions=True
# )
# async def fetch_urls():
#     await update_urls()


@app.on_event("shutdown")
async def disconnect_services():
    await database.disconnect()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
async def home():
    return FileResponse("public/index.html")


app.include_router(auth_router)
app.include_router(bookmark_router)
