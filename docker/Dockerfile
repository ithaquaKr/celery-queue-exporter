# syntax=docker/dockerfile:1.4

# Build stage
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Create non-root user
RUN useradd -m -u 1000 exporter

WORKDIR /app

# Copy only dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN /root/.cargo/bin/uv pip install --system .

# Runtime stage
FROM python:3.12-slim

# Create non-root user
RUN useradd -m -u 1000 exporter

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY exporter ./exporter

# Set ownership to non-root user
RUN chown -R exporter:exporter /app

# Switch to non-root user
USER exporter

# TODO: (@ithaquaKr) Health check

# Use tini as init
ENTRYPOINT ["/usr/bin/tini", "--"]

# Default command
CMD ["python3", "-m", "exporter"]
