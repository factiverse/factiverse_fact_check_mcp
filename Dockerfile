FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

WORKDIR /app
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y

COPY . .
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache --no-dev

EXPOSE 80

CMD ["uv", "run", "mcp_server.py"]
