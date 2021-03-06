from typing import Optional

from pydantic import BaseModel


def to_camel(string: str) -> str:
    """Camel-case a given string e.g. camel_case -> camelCase"""
    return "".join(
        word.capitalize() if i else word for i, word in enumerate(string.split("_"))
    )


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class PaginationResult(CamelModel):
    items_per_page: int
    current_page: int
    previous_page: Optional[int]
    next_page: Optional[int]
    has_previous: bool
    has_next: bool
    total_num_items: int
    total_num_pages: int
