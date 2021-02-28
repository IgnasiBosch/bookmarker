import asyncio
import os
from pathlib import Path

import typer

from src.bookmarks.use_cases.add_bookmark import (
    update_urls,
    import_urls_from_browser_bookmarks,
)
from src.db import connection

app = typer.Typer()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def _scrape_batch():
    async with connection():
        await update_urls()


@app.command()
def scrape_batch():
    asyncio.run(_scrape_batch())
    print("Scraped!")


async def _add_from_file(filepath):
    async with connection():
        await import_urls_from_browser_bookmarks(filepath)


@app.command()
def add_from_file(filename: str):
    filepath = BASE_DIR / Path("tmp") / Path(filename)
    asyncio.run(_add_from_file(filepath))
    print("Imported from file!")


if __name__ == "__main__":
    app()
