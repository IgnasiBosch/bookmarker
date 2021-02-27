class InvalidCredentials(ValueError):
    ...


class MaxFailedAttemptsRaised(ValueError):
    ...


class DuplicatedToken(ValueError):
    ...


class EmailAlreadyUsed(ValueError):
    ...


class ExpiredToken(Exception):
    ...


class NotExpiredToken(Exception):
    ...


class TokenError(ValueError):
    ...
