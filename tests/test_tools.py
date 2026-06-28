import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


@pytest.mark.asyncio
async def test_tools_are_discoverable(streamable_http_url: str) -> None:
    async with streamable_http_client(streamable_http_url) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()

    tool_names = {tool.name for tool in tools.tools}
    assert "solar_to_lunar" in tool_names
    assert "lunar_to_solar" in tool_names
    assert "conversion_limits" in tool_names


@pytest.mark.asyncio
async def test_solar_to_lunar_tool_success(streamable_http_url: str) -> None:
    async with streamable_http_client(streamable_http_url) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                "solar_to_lunar",
                {"year": 2017, "month": 6, "day": 24},
            )

    assert result.isError is False
    assert result.content
    assert result.content[0].text
    assert "양력날짜:" in result.content[0].text
    assert "음력날짜:" in result.content[0].text
    assert "2017-06-24 (토요일)" in result.content[0].text
    assert "2017-05-01 (윤달) (토요일)" in result.content[0].text
    assert "토요일" in result.content[0].text
    assert result.structuredContent is not None
    structured = result.structuredContent
    assert structured["solar"]["weekday"] == "토요일"
    assert structured["lunar"]["year"] == 2017
    assert structured["lunar"]["month"] == 5
    assert structured["lunar"]["day"] == 1
    assert structured["lunar"]["is_intercalation"] is True
    assert structured["lunar"]["weekday"] == "토요일"


@pytest.mark.asyncio
async def test_lunar_to_solar_tool_success_text_includes_weekday(streamable_http_url: str) -> None:
    async with streamable_http_client(streamable_http_url) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                "lunar_to_solar",
                {"year": 1956, "month": 1, "day": 21, "is_intercalation": False},
            )

    assert result.isError is False
    assert result.content
    assert result.content[0].text
    assert "양력날짜:" in result.content[0].text
    assert "음력날짜:" in result.content[0].text
    assert "1956-03-03 (토요일)" in result.content[0].text
    assert "1956-01-21 (토요일)" in result.content[0].text
    assert "토요일" in result.content[0].text
    assert result.structuredContent is not None
    structured = result.structuredContent
    assert structured["lunar"]["weekday"] == "토요일"
    assert structured["solar"]["weekday"] == "토요일"


@pytest.mark.asyncio
async def test_lunar_to_solar_tool_error_payload(streamable_http_url: str) -> None:
    async with streamable_http_client(streamable_http_url) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                "lunar_to_solar",
                {"year": 2017, "month": 3, "day": 1, "is_intercalation": True},
            )

    assert result.isError is True
    assert result.structuredContent is not None
    structured = result.structuredContent
    assert structured["code"] == "LEAP_MONTH_MISMATCH"


@pytest.mark.asyncio
async def test_solar_to_lunar_defaults_year_from_current_year(streamable_http_url: str) -> None:
    async with streamable_http_client(streamable_http_url) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                "solar_to_lunar",
                {"month": 8, "day": 20, "current_year": 2026},
            )

    assert result.isError is False
    assert result.structuredContent is not None
    structured = result.structuredContent
    assert structured["solar"]["year"] == 2026
    assert structured["solar"]["month"] == 8
    assert structured["solar"]["day"] == 20
    assert structured["lunar"]["year"] == 2026
    assert structured["lunar"]["month"] == 7
    assert structured["lunar"]["day"] == 8


@pytest.mark.asyncio
async def test_lunar_to_solar_defaults_year_from_current_year(streamable_http_url: str) -> None:
    async with streamable_http_client(streamable_http_url) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                "lunar_to_solar",
                {"month": 7, "day": 8, "is_intercalation": False, "current_year": 2026},
            )

    assert result.isError is False
    assert result.structuredContent is not None
    structured = result.structuredContent
    assert structured["lunar"]["year"] == 2026
    assert structured["lunar"]["month"] == 7
    assert structured["lunar"]["day"] == 8
    assert structured["solar"]["year"] == 2026
    assert structured["solar"]["month"] == 8
    assert structured["solar"]["day"] == 20
