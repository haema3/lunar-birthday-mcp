import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


@pytest.mark.asyncio
async def test_streamable_http_smoke_conversion_limits(streamable_http_url: str) -> None:
    async with streamable_http_client(streamable_http_url) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool("conversion_limits", {})

    assert result.isError is False
    assert result.structuredContent is not None
    assert result.structuredContent["solar_max"] == "2050-12-31"
