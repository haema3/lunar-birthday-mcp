from __future__ import annotations

from pydantic import BaseModel, Field


class SolarDateInput(BaseModel):
    year: int = Field(ge=1)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)


class LunarDateInput(BaseModel):
    year: int = Field(ge=1)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    is_intercalation: bool = False


class SolarDate(BaseModel):
    year: int
    month: int
    day: int
    iso: str
    weekday: str


class LunarDate(BaseModel):
    year: int
    month: int
    day: int
    is_intercalation: bool
    iso: str
    weekday: str


class SolarToLunarResult(BaseModel):
    standard: str = "korean_lunar_kari"
    solar: SolarDate
    lunar: LunarDate


class LunarToSolarResult(BaseModel):
    standard: str = "korean_lunar_kari"
    lunar: LunarDate
    solar: SolarDate


class ConversionLimitsResult(BaseModel):
    standard: str = "korean_lunar_kari"
    lunar_min: str
    lunar_max: str
    solar_min: str
    solar_max: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    hint: str
