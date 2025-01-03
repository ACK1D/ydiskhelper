# syntax=docker/dockerfile:1

# Stage 1: Build dependencies
FROM python:3.12-slim-bookworm AS build

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.5 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/var/cache/pypoetry \
    VIRTUAL_ENV=".venv"

WORKDIR /ydiskhelper

COPY poetry.lock pyproject.toml ./
RUN pip install "poetry==$POETRY_VERSION" && \
    python -m venv $VIRTUAL_ENV && \
    poetry export --without-hashes --without dev --format requirements.txt --output requirements.txt

# Stage 2: Final image
FROM python:3.12-slim-bookworm AS final

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=ydiskhelper.settings \
    GRANIAN_WORKERS=2 \
    GRANIAN_THREADS=1 \
    GRANIAN_MAX_CONNECTIONS=200

WORKDIR /ydiskhelper

COPY --from=build /ydiskhelper/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt granian

COPY . .

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
