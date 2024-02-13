from enum import Enum
from typing import Any

from fastapi_users.exceptions import FastAPIUsersException


class ErrorCode(str, Enum):
    REGISTER_INVALID_NAME = "REGISTER_INVALID_NAME"


class InvalidLoginException(FastAPIUsersException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason
