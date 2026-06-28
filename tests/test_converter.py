import pytest

from app.converter import LunarSolarConverter
from app.errors import ConversionCode, ConversionError
from app.models import LunarDateInput, SolarDateInput


def test_solar_to_lunar_happy_path_intercalation() -> None:
    converter = LunarSolarConverter()

    result = converter.solar_to_lunar(SolarDateInput(year=2017, month=6, day=24))

    assert result.solar.weekday == "토요일"
    assert result.lunar.year == 2017
    assert result.lunar.month == 5
    assert result.lunar.day == 1
    assert result.lunar.is_intercalation is True
    assert result.lunar.weekday == "토요일"


def test_lunar_to_solar_happy_path() -> None:
    converter = LunarSolarConverter()

    result = converter.lunar_to_solar(
        LunarDateInput(year=1956, month=1, day=21, is_intercalation=False)
    )

    assert result.lunar.weekday == "토요일"
    assert result.solar.year == 1956
    assert result.solar.month == 3
    assert result.solar.day == 3
    assert result.solar.weekday == "토요일"


def test_lunar_to_solar_leap_month_happy_path() -> None:
    converter = LunarSolarConverter()

    result = converter.lunar_to_solar(
        LunarDateInput(year=1727, month=3, day=1, is_intercalation=True)
    )

    assert result.solar.year == 1727
    assert result.solar.month == 4
    assert result.solar.day == 21


def test_lunar_to_solar_rejects_non_leap_month_request() -> None:
    converter = LunarSolarConverter()

    with pytest.raises(ConversionError) as exc_info:
        converter.lunar_to_solar(LunarDateInput(year=2017, month=3, day=1, is_intercalation=True))

    assert exc_info.value.code == ConversionCode.LEAP_MONTH_MISMATCH


def test_solar_out_of_range_raises_out_of_range() -> None:
    converter = LunarSolarConverter()

    with pytest.raises(ConversionError) as exc_info:
        converter.solar_to_lunar(SolarDateInput(year=2051, month=1, day=1))

    assert exc_info.value.code == ConversionCode.OUT_OF_RANGE


def test_solar_invalid_gregorian_gap_raises_invalid_date() -> None:
    converter = LunarSolarConverter()

    with pytest.raises(ConversionError) as exc_info:
        converter.solar_to_lunar(SolarDateInput(year=1582, month=10, day=8))

    assert exc_info.value.code == ConversionCode.INVALID_DATE


def test_conversion_limits_documented_bounds() -> None:
    converter = LunarSolarConverter()

    result = converter.conversion_limits()

    assert result.lunar_min == "1000-01-01"
    assert result.lunar_max == "2050-11-18"
    assert result.solar_min == "1000-02-13"
    assert result.solar_max == "2050-12-31"
