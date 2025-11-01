
FROM python:3.13-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . /room-booking
WORKDIR /room-booking
RUN uv sync --locked
CMD ["uv", "run", "fastapi", "run", "--port", "80"]