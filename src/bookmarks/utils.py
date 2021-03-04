import json
from itertools import chain, islice
from pathlib import Path

import aiofiles
import httpx
from httpx import HTTPError, Response
from pydantic import AnyUrl


async def read_json_file(path: Path) -> dict:
    async with aiofiles.open(path) as f:
        contents = await f.read()
        return json.loads(contents)


async def fetch_url(url: AnyUrl) -> Response:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url)
            return resp
        except HTTPError as exc:
            raise ValueError(f"Error fetching {url}: {exc}")


def chunks(iterable, size=10):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))
