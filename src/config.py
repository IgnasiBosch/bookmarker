from pydantic import BaseSettings


class Config(BaseSettings):

    class Config:
        case_sensitive = True
