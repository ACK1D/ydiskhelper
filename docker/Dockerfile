# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12-slim-bookworm
ARG POETRY_VERSION=2.0.0
ARG APP_HOME=/ydiskhelper
ARG DJANGO_SETTINGS_MODULE=ydiskhelper.settings

# Stage 1: Base image with common settings
FROM python:${PYTHON_VERSION} AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

ARG APP_HOME
WORKDIR ${APP_HOME}

# Stage 2: Build dependencies
FROM base AS builder

ARG POETRY_VERSION
ENV POETRY_VERSION=${POETRY_VERSION} \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

COPY poetry.lock pyproject.toml ./
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" && \
    poetry self add poetry-plugin-export && \
    poetry export --without-hashes --without dev -f requirements.txt -o requirements.txt

# Stage 3: Final image
FROM base AS final

ARG DJANGO_SETTINGS_MODULE
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} \
    GRANIAN_WORKERS=2 \
    GRANIAN_THREADS=1 \
    GRANIAN_MAX_CONNECTIONS=200

COPY --from=builder ${APP_HOME}/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY docker/entrypoint.sh /entrypoint.sh
COPY . .

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
