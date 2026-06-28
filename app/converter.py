from __future__ import annotations

from datetime import date

from korean_lunar_calendar import KoreanLunarCalendar

from app.errors import ConversionCode, ConversionError
from app.models import (
    ConversionLimitsResult,
    LunarDate,
    LunarDateInput,
    LunarToSolarResult,
    SolarDate,
    SolarDateInput,
    SolarToLunarResult,
)

LUNAR_MIN = (1000, 1, 1)
LUNAR_MAX = (2050, 11, 18)
SOLAR_MIN = (1000, 2, 13)
SOLAR_MAX = (2050, 12, 31)
WEEKDAY_NAMES = (
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일",
)


class LunarSolarConverter:
    def solar_to_lunar(self, payload: SolarDateInput) -> SolarToLunarResult:
        self._validate_solar_input(payload)

        calendar = KoreanLunarCalendar()
        ok = calendar.setSolarDate(payload.year, payload.month, payload.day)
        if not ok:
            raise ConversionError(
                code=ConversionCode.INVALID_DATE,
                message="Invalid solar date for conversion.",
                hint="Check Gregorian date validity and supported conversion range.",
            )

        weekday = self._weekday_name(calendar.solarYear, calendar.solarMonth, calendar.solarDay)
        solar = SolarDate(
            year=calendar.solarYear,
            month=calendar.solarMonth,
            day=calendar.solarDay,
            iso=calendar.SolarIsoFormat(),
            weekday=weekday,
        )
        lunar = LunarDate(
            year=calendar.lunarYear,
            month=calendar.lunarMonth,
            day=calendar.lunarDay,
            is_intercalation=calendar.isIntercalation,
            iso=self._build_lunar_iso(
                calendar.lunarYear,
                calendar.lunarMonth,
                calendar.lunarDay,
                calendar.isIntercalation,
            ),
            weekday=weekday,
        )
        return SolarToLunarResult(solar=solar, lunar=lunar)

    def lunar_to_solar(self, payload: LunarDateInput) -> LunarToSolarResult:
        self._validate_lunar_input(payload)

        calendar = KoreanLunarCalendar()
        ok = calendar.setLunarDate(
            payload.year,
            payload.month,
            payload.day,
            payload.is_intercalation,
        )
        if not ok:
            code = (
                ConversionCode.LEAP_MONTH_MISMATCH
                if payload.is_intercalation
                else ConversionCode.INVALID_DATE
            )
            raise ConversionError(
                code=code,
                message="Invalid lunar date for conversion.",
                hint=(
                    "Verify leap-month flag and ensure the lunar date exists "
                    "in the supported range."
                ),
            )

        weekday = self._weekday_name(calendar.solarYear, calendar.solarMonth, calendar.solarDay)
        lunar = LunarDate(
            year=calendar.lunarYear,
            month=calendar.lunarMonth,
            day=calendar.lunarDay,
            is_intercalation=calendar.isIntercalation,
            iso=self._build_lunar_iso(
                calendar.lunarYear,
                calendar.lunarMonth,
                calendar.lunarDay,
                calendar.isIntercalation,
            ),
            weekday=weekday,
        )
        solar = SolarDate(
            year=calendar.solarYear,
            month=calendar.solarMonth,
            day=calendar.solarDay,
            iso=calendar.SolarIsoFormat(),
            weekday=weekday,
        )
        return LunarToSolarResult(lunar=lunar, solar=solar)

    def conversion_limits(self) -> ConversionLimitsResult:
        return ConversionLimitsResult(
            lunar_min="1000-01-01",
            lunar_max="2050-11-18",
            solar_min="1000-02-13",
            solar_max="2050-12-31",
        )

    def _validate_solar_input(self, payload: SolarDateInput) -> None:
        if not self._is_in_range((payload.year, payload.month, payload.day), SOLAR_MIN, SOLAR_MAX):
            raise ConversionError(
                code=ConversionCode.OUT_OF_RANGE,
                message="Solar date is outside supported range.",
                hint="Use a date between 1000-02-13 and 2050-12-31.",
            )

        try:
            date(payload.year, payload.month, payload.day)
        except ValueError as exc:
            raise ConversionError(
                code=ConversionCode.INVALID_DATE,
                message="Solar date is not a valid Gregorian date.",
                hint="Check day and month values.",
            ) from exc

    def _validate_lunar_input(self, payload: LunarDateInput) -> None:
        if not self._is_in_range((payload.year, payload.month, payload.day), LUNAR_MIN, LUNAR_MAX):
            raise ConversionError(
                code=ConversionCode.OUT_OF_RANGE,
                message="Lunar date is outside supported range.",
                hint="Use a date between 1000-01-01 and 2050-11-18.",
            )

    @staticmethod
    def _is_in_range(
        value: tuple[int, int, int],
        lower: tuple[int, int, int],
        upper: tuple[int, int, int],
    ) -> bool:
        return lower <= value <= upper

    @staticmethod
    def _build_lunar_iso(year: int, month: int, day: int, is_intercalation: bool) -> str:
        suffix = "-L" if is_intercalation else ""
        return f"{year:04d}-{month:02d}-{day:02d}{suffix}"

    @staticmethod
    def _weekday_name(year: int, month: int, day: int) -> str:
        return WEEKDAY_NAMES[date(year, month, day).weekday()]
