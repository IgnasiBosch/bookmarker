import asyncio

import typer

from src.bookmarks.use_cases.add_bookmark import update_urls
from src.db import connection

app = typer.Typer()


async def _scrape_batch():
    async with connection():
        await update_urls()


@app.command()
def scrape_batch():
    asyncio.run(_scrape_batch())
    print("Scraped!")


if __name__ == "__main__":
    app()
