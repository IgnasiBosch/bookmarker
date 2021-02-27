from contextlib import asynccontextmanager

import databases
import sqlalchemy as sa

from src.config import settings


database = databases.Database(settings.database_url)
metadata = sa.MetaData()
engine = sa.create_engine(settings.database_url, echo=True)


@asynccontextmanager
async def connection():
    await database.connect()
    try:
        yield
    finally:
        await database.disconnect()
