# Lunar Birthday MCP Server

Python MCP server for Korean lunar<->solar birthday conversion using Streamable HTTP.

## Features

- Solar -> Lunar conversion (Korean standard)
- Lunar -> Solar conversion (including leap month)
- Streamable HTTP transport (`/mcp`)
- Structured success and error outputs

## Calendar Standard

This project uses `korean-lunar-calendar`, based on Korean lunar calendar rules (KARI/KASI).

## Prerequisites

- Python 3.11+

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install .[dev]
```

## Run

```bash
python -m app.server
```

Default server endpoint: `http://127.0.0.1:8000/mcp`

For public/server deployment, set `MCP_HOST=0.0.0.0`.

Optional host/origin allow-list environment variables:

- `MCP_ALLOWED_HOSTS` (comma-separated, e.g. `api.example.com:443,api.example.com:*`)
- `MCP_ALLOWED_ORIGINS` (comma-separated, e.g. `https://api.example.com,https://console.example.com`)

If `MCP_HOST` is non-localhost and these are not set, the server allows all hosts/origins to avoid `Invalid Host header` in public deployments.

## Verify with MCP Inspector

```bash
npx -y @modelcontextprotocol/inspector
```

Connect inspector to `http://127.0.0.1:8000/mcp`.

## Development Checks

```bash
ruff check .
pytest -q
```

## Windows Notes

- If your path contains non-ASCII characters, prefer `pip install .[dev]` over editable install.
- Bind to localhost for local development security.

## Troubleshooting

- If a tool call returns an error payload, check `code` and `hint` fields.
- Ensure date range is within supported bounds returned by `conversion_limits`.
- If you see `Invalid Host header` on a deployed server, set `MCP_ALLOWED_HOSTS` and `MCP_ALLOWED_ORIGINS` to your domain values.
