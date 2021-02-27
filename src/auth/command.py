import asyncio

import typer

from src.auth.schemas import UserCreate
from src.auth.use_cases.user import create_new_user
from src.db import connection

app = typer.Typer()


async def _create_user(email, password):
    async with connection():
        await create_new_user(UserCreate(email=email, password=password))


@app.command()
def create_user(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True
    ),
):
    asyncio.run(_create_user(email, password))
    print("User created!")


if __name__ == "__main__":
    app()
