# ==============================================================================
# Multi-Stage Production Dockerfile for Project FORESIGHT
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Builder
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --user --no-warn-script-location -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Runtime Base
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/foresight/.local/bin:${PATH}" \
    PYTHONPATH="/app/src:${PYTHONPATH}"

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash foresight

# Copy installed Python packages from builder stage
COPY --from=builder --chown=foresight:foresight /root/.local /home/foresight/.local

# Copy application source code and configurations
COPY --chown=foresight:foresight . /app

# Switch to unprivileged security user
USER foresight

# Create runtime directories
RUN mkdir -p logs data/raw data/processed models reports

EXPOSE 8000 8501

CMD ["python", "-m", "foresight.api.main"]
