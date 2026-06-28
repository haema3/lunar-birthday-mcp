from __future__ import annotations

from enum import StrEnum


class ConversionCode(StrEnum):
    OUT_OF_RANGE = "OUT_OF_RANGE"
    INVALID_DATE = "INVALID_DATE"
    LEAP_MONTH_MISMATCH = "LEAP_MONTH_MISMATCH"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ConversionError(Exception):
    def __init__(self, code: ConversionCode, message: str, hint: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint
