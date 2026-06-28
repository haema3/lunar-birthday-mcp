FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY app /app/app

RUN pip install --upgrade pip \
    && pip install .

EXPOSE 8000

CMD ["python", "-m", "app.server"]