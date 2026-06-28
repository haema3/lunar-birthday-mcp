FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SHIP_MCP_TRANSPORT=streamable-http \
    SHIP_MCP_HOST=0.0.0.0 \
    SHIP_MCP_PORT=8000 \
    SHIP_MCP_DB_PATH=/data/lunar-birthday.db

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY app /app/app

RUN pip install --upgrade pip \
    && pip install .

EXPOSE 8000

CMD ["sh", "-c", "lunar-birthday-mcp --transport ${SHIP_MCP_TRANSPORT} --host ${SHIP_MCP_HOST} --port ${SHIP_MCP_PORT} --db-path ${SHIP_MCP_DB_PATH}"]