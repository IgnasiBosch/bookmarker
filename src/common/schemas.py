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
