import logging
import os

from dotenv import load_dotenv
from pydantic import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Settings(BaseSettings):
    debug: bool = os.getenv("DEBUG", default=False)
    base_url: str = os.getenv("BASE_URL")
    database_url: str = os.getenv("DATABASE_URL")
    redis_url: str = os.getenv("REDIS_URL")
    redis_publish_channel: str = "ws"
    access_token_secret_key: str = os.getenv(  # to create a key: $ openssl rand -hex 32
        "TOKEN_SECRET_KEY",
        default="311ab81a83e1dcfcf5b4575399fce69c71ae36c9c73929984b4ccc0e03a22851",
    )
    access_token_algorithm: str = os.getenv("TOKEN_ALGORITHM", default="HS256")
    access_token_expire_minutes: int = os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES", default=30
    )
    access_token_max_refreshable_days: int = os.getenv(
        "MAX_REFRESHABLE_TOKEN_DAYS", default=30
    )
    remove_sessions_older_than_days: int = os.getenv(
        "REMOVE_SESSIONS_OLDER_THAN_DAYS", default=30
    )

    max_failed_login_attempts: int = os.getenv("MAX_FAILED_LOGIN_ATTEMPTS", default=5)
    max_failed_url_extractions: int = os.getenv("MAX_FAILED_URL_EXTRACTIONS", default=5)
    batch_url_extractions: int = os.getenv("BATCH_URL_EXTRACTIONS", default=20)
    refresh_urls_older_than_days: int = os.getenv(
        "REFRESH_URLS_OLDER_THAN_DAYS", default=20
    )
    run_refresh_url_task_every_seconds: int = os.getenv(
        "RUN_REFRESH_URL_TASK_EVERY_SECONDS", default=24 * 3600
    )


settings = Settings()

log_level = logging.DEBUG if settings.debug else logging.INFO
FORMAT = "%(asctime)-15s - %(levelname)s -  %(name)s - %(message)s"
logging.basicConfig(level=log_level, format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
