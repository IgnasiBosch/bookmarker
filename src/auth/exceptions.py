from http import HTTPStatus
from typing import Optional

from src.common.exceptions import BaseError


class Unauthorized(BaseError):
    def __init__(self, msg: Optional[str] = "Incorrect Token"):
        super().__init__(msg, 2000, HTTPStatus.UNAUTHORIZED)


class RefreshTokenError(BaseError):
    def __init__(self, msg: Optional[str] = "Expired Token"):
        super().__init__(msg, 2001, HTTPStatus.UNAUTHORIZED)


class InvalidCredentials(BaseError):
    def __init__(self, msg: Optional[str] = "Invalid credentials"):
        super().__init__(msg, 2002, HTTPStatus.UNAUTHORIZED)


class MaxFailedAttemptsRaised(BaseError):
    def __init__(self, msg: Optional[str] = "Invalid credentials"):
        super().__init__(msg, 2003, HTTPStatus.UNAUTHORIZED)


class DuplicatedToken(BaseError):
    def __init__(self, msg: Optional[str] = "Invalid credentials"):
        super().__init__(msg, 2004, HTTPStatus.CONFLICT)


class EmailAlreadyUsed(BaseError):
    def __init__(self, msg: Optional[str] = "Invalid credentials"):
        super().__init__(msg, 2005, HTTPStatus.CONFLICT)


class ExpiredToken(BaseError):
    def __init__(self, msg: Optional[str] = "Expired Token"):
        super().__init__(msg, 2006, HTTPStatus.UNAUTHORIZED)


class NotExpiredToken(BaseError):
    def __init__(self, msg: Optional[str] = "Token is not expired"):
        super().__init__(msg, 2007, HTTPStatus.UNPROCESSABLE_ENTITY)


class TokenError(BaseError):
    def __init__(self, msg: Optional[str] = "Incorrect Token"):
        super().__init__(msg, 2008, HTTPStatus.UNAUTHORIZED)
