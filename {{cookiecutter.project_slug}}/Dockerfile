# syntax=docker/dockerfile:1
ARG BUILD=prod

FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Force uv to use system python so symlinks don't break in multi-stage builds
ENV UV_PYTHON_PREFERENCE=system

# Set env for uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Install necessary system dependencies (like git if needed for some packages)
RUN apt-get update && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy pyproject.toml and lockfile (if generated)
COPY pyproject.toml uv.lock* ./

RUN if [ "$BUILD" = "prod" ]; then \
        EXTRA_FLAGS="--no-dev"; \
    elif [ "$BUILD" = "dev" ]; then \
        EXTRA_FLAGS=""; \
    else \
        echo "Invalid BUILD argument: $BUILD"; \
        exit 1; \
    fi; \
    uv sync --no-install-project $EXTRA_FLAGS

# Copy project files
COPY . .

# Install the project itself
RUN if [ "$BUILD" = "prod" ]; then \
        EXTRA_FLAGS="--no-dev"; \
    elif [ "$BUILD" = "dev" ]; then \
        EXTRA_FLAGS=""; \
    else \
        echo "Invalid BUILD argument: $BUILD"; \
        exit 1; \
    fi; \
    uv sync $EXTRA_FLAGS

# Runtime Stage
FROM python:3.12-slim AS runtime

RUN apt-get update && rm -rf /var/lib/apt/lists/*


# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY . .
