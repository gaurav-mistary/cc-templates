# Arguments
# ==========================================

# Build version. If you are executing this locally or on servr.
ARG BUILD=dev

# ==========================================
# STAGE 1: Builder
# ==========================================
FROM python:3.12-slim AS builder
ARG BUILD

# Install git (required by gitpython and cookiecutter)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# The officially recommended way to install uv in Docker!
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Force uv to use the system python (from the python:3.12-slim image) 
# instead of downloading a managed version, so the symlink survives the multi-stage copy!
ENV UV_PYTHON_PREFERENCE=system

WORKDIR /app

# Copy package definitions
COPY pyproject.toml uv.lock* ./

# Install dependencies into a virtual environment in /app/.venv
# (Using --no-install-project to cache the dependencies layer!)
RUN if [ "$BUILD" = "prod" ]; then \
        EXTRA_FLAGS="--no-dev"; \
    elif [ "$BUILD" = "dev" ]; then \
        EXTRA_FLAGS=""; \
    else \
        echo "Invalid BUILD argument: $BUILD"; \
        exit 1; \
    fi; \
    uv sync --python /usr/local/bin/python --no-install-project $EXTRA_FLAGS

# Copy the actual source code
COPY . .

# Sync again to install the cc package itself into the .venv
RUN if [ "$BUILD" = "prod" ]; then \
        EXTRA_FLAGS="--no-dev"; \
    elif [ "$BUILD" = "dev" ]; then \
        EXTRA_FLAGS=""; \
    else \
        echo "Invalid BUILD argument: $BUILD"; \
        exit 1; \
    fi; \
    uv sync --python /usr/local/bin/python $EXTRA_FLAGS


# ==========================================
# STAGE 2: Runtime
# ==========================================
FROM python:3.12-slim

# Cookiecutter and GitPython strictly require git at runtime
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the fully built environment and source code from the builder stage
COPY --from=builder /app /app

# Add the uv virtual environment to the system PATH
ENV PATH="/app/.venv/bin:$PATH"

# Tell Python where to find the "cc" source code directory
ENV PYTHONPATH="/app"

# Make the container behave natively
ENTRYPOINT ["python",  "-m", "cc.cli"]