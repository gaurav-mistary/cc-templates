# syntax=docker/dockerfile:1
ARG BUILD=prod

FROM python:{{ cookiecutter.python_version }}-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set env for uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Install necessary system dependencies (like git if needed for some packages)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and lockfile (if generated)
COPY pyproject.toml uv.lock* ./

ARG BUILD
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
ARG BUILD
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
FROM python:{{ cookiecutter.python_version }}-slim AS runtime

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY . .

# By default run the python module (or override with just run)
CMD ["python", "-m", "{{ cookiecutter.project_slug.replace('-', '_') }}"]
