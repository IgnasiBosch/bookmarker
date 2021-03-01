from http import HTTPStatus
from typing import Optional


class BaseError(Exception):
    def __init__(
        self,
        msg: Optional[str] = None,
        code: Optional[int] = 1000,
        status_code: Optional[int] = HTTPStatus.UNPROCESSABLE_ENTITY,
    ):
        self.msg = msg
        self.code = code
        self.status_code = status_code

    def to_json(self):
        return {"code": self.code, "detail": self.msg}

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return (
            f"{class_name}(status_code={self.status_code!r}, "
            f"detail={self.msg!r}, code={self.code!r})"
        )


class InternalError(BaseError):
    def __init__(self, msg: Optional[str] = None):
        super().__init__(msg, 1001, HTTPStatus.INTERNAL_SERVER_ERROR)


class BadRequest(BaseError):
    def __init__(self, msg: Optional[str] = None):
        super().__init__(msg, 1002, HTTPStatus.BAD_REQUEST)


class UnprocessableEntity(BaseError):
    def __init__(self, msg: Optional[str] = None):
        super().__init__(msg, 1003, HTTPStatus.UNPROCESSABLE_ENTITY)
