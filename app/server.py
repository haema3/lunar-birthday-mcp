from __future__ import annotations

import contextlib
import os
from datetime import date

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent, ToolAnnotations
from starlette.applications import Starlette
from starlette.routing import Mount

from app.converter import LunarSolarConverter
from app.errors import ConversionCode, ConversionError
from app.models import ErrorPayload, LunarDateInput, SolarDateInput

mcp = FastMCP(
    "lunar-birthday",
    instructions=(
        "Convert birthday dates between Korean lunar and Gregorian solar calendars. "
        "Supports leap month input for lunar dates. "
        "If a prompt omits year, pass current_year and default to it. "
        "Always include the weekday in every conversion output."
    ),
    stateless_http=True,
    json_response=True,
)

_converter = LunarSolarConverter()
_READONLY_TOOL_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


def _error_result(error: ConversionError) -> CallToolResult:
    payload = ErrorPayload(code=error.code.value, message=error.message, hint=error.hint)
    return CallToolResult(
        content=[TextContent(type="text", text=f"{payload.code}: {payload.message}")],
        structuredContent=payload.model_dump(),
        isError=True,
    )


def _ok_result(payload: dict, text: str = "Conversion completed.") -> CallToolResult:
    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        structuredContent=payload,
    )


def _format_solar(solar: dict) -> str:
    return (
        f"{int(solar['year']):04d}-{int(solar['month']):02d}-{int(solar['day']):02d}"
        f" ({solar['weekday']})"
    )


def _format_lunar(lunar: dict) -> str:
    leap = " (윤달)" if lunar.get("is_intercalation") else ""
    return (
        f"{int(lunar['year']):04d}-{int(lunar['month']):02d}-{int(lunar['day']):02d}"
        f"{leap} ({lunar['weekday']})"
    )


def _format_output_text(solar_date: str, lunar_date: str) -> str:
    return f"양력날짜: {solar_date}\n음력날짜: {lunar_date}"


def _resolve_year(year: int | None, current_year: int | None) -> int:
    if year is not None:
        return year
    if current_year is not None:
        return current_year
    return date.today().year


@mcp.tool(
    description=(
        "양력<->음력 변환 MCP: 양력 날짜를 한국 표준 음력 날짜로 변환합니다. "
        "결과에 양력/음력 요일 정보를 포함합니다."
    ),
    annotations=_READONLY_TOOL_ANNOTATIONS,
)
def solar_to_lunar(
    month: int,
    day: int,
    year: int | None = None,
    current_year: int | None = None,
) -> CallToolResult:
    try:
        resolved_year = _resolve_year(year, current_year)
        result = _converter.solar_to_lunar(
            SolarDateInput(year=resolved_year, month=month, day=day)
        )
        payload = result.model_dump()
        text = _format_output_text(
            solar_date=_format_solar(payload["solar"]),
            lunar_date=_format_lunar(payload["lunar"]),
        )
        return _ok_result(payload, text)
    except ConversionError as error:
        return _error_result(error)
    except Exception:
        return _error_result(
            ConversionError(
                code=ConversionCode.INTERNAL_ERROR,
                message="Unexpected error during solar-to-lunar conversion.",
                hint="Retry with valid inputs. If issue persists, check server logs.",
            )
        )


@mcp.tool(
    description=(
        "양력<->음력 변환 MCP: 음력 날짜를 한국 표준 양력 날짜로 변환합니다. "
        "윤달 입력을 지원하며 결과에 양력/음력 요일 정보를 포함합니다."
    ),
    annotations=_READONLY_TOOL_ANNOTATIONS,
)
def lunar_to_solar(
    month: int,
    day: int,
    is_intercalation: bool = False,
    year: int | None = None,
    current_year: int | None = None,
) -> CallToolResult:
    try:
        resolved_year = _resolve_year(year, current_year)
        result = _converter.lunar_to_solar(
            LunarDateInput(
                year=resolved_year,
                month=month,
                day=day,
                is_intercalation=is_intercalation,
            )
        )
        payload = result.model_dump()
        text = _format_output_text(
            solar_date=_format_solar(payload["solar"]),
            lunar_date=_format_lunar(payload["lunar"]),
        )
        return _ok_result(payload, text)
    except ConversionError as error:
        return _error_result(error)
    except Exception:
        return _error_result(
            ConversionError(
                code=ConversionCode.INTERNAL_ERROR,
                message="Unexpected error during lunar-to-solar conversion.",
                hint="Retry with valid inputs. If issue persists, check server logs.",
            )
        )


@mcp.tool(
    description="양력<->음력 변환 MCP: 지원되는 변환 가능 연도 범위를 조회합니다.",
    annotations=_READONLY_TOOL_ANNOTATIONS,
)
def conversion_limits() -> CallToolResult:
    return _ok_result(_converter.conversion_limits().model_dump())


def create_starlette_app() -> Starlette:
    @contextlib.asynccontextmanager
    async def lifespan(_app: Starlette):
        async with mcp.session_manager.run():
            yield

    return Starlette(
        routes=[Mount("/", app=mcp.streamable_http_app())],
        lifespan=lifespan,
    )


def _configure_runtime_settings() -> None:
    mcp.settings.host = os.getenv("MCP_HOST", "127.0.0.1")
    mcp.settings.port = int(os.getenv("MCP_PORT", "8000"))


def main() -> None:
    _configure_runtime_settings()
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
