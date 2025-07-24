# syntax=docker/dockerfile:1.4
# Reference: https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile
# Build stage
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
# Copy only dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Runtime stage
FROM python:3.12-alpine

# Create non-root user
RUN adduser -D -u 1000 exporter

# Install runtime dependencies
RUN apk add --no-cache tini curl

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder --chown=exporter:exporter /app /app

# Copy application code
COPY --chown=exporter:exporter exporter ./exporter

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER exporter

HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl --fail http://localhost:9726/metrics || exit 1

# Use tini as init
ENTRYPOINT ["/sbin/tini", "--"]

# Default command
CMD ["python3", "-m", "exporter"]
