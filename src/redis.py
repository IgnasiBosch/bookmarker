import json
from contextlib import asynccontextmanager
from uuid import UUID

from broadcaster import Broadcast
from fastapi.encoders import jsonable_encoder

from src.config import settings

broadcast = Broadcast(settings.redis_url)


@asynccontextmanager
async def connection():
    await broadcast.connect()
    try:
        yield
    finally:
        await broadcast.disconnect()


async def publish(message: dict):
    await broadcast.publish(
        channel=settings.redis_publish_channel,
        message=json.dumps(message, default=str),
    )
