# ─────────────────────────────────────────────────────────────────────────────
# Secure Production Dockerfile — MLOps Training Container
#
# Security controls implemented:
#   ✔  Slim base image (minimal attack surface)
#   ✔  Non-root user (UID/GID 10001 — avoids root privilege escalation)
#   ✔  Read-only filesystem compatible (data written to /app/outputs only)
#   ✔  No unnecessary OS packages
#   ✔  .dockerignore recommended to exclude secrets/git history
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage: base ───────────────────────────────────────────────────────────────
FROM python:3.10-slim AS base

# OCI standard labels for image provenance (important in regulated environments)
LABEL org.opencontainers.image.title="secure-mlops-trainer"
LABEL org.opencontainers.image.description="Anomaly detection training container"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/your-org/secure-mlops-pipeline"

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ── Install system-level dependencies (minimal) ───────────────────────────────
# libpq-dev is required by psycopg2-binary at runtime on slim images
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Install Python dependencies ───────────────────────────────────────────────
COPY src/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application source ───────────────────────────────────────────────────
COPY src/ ./src/

# ── Security: create and switch to a non-root user ───────────────────────────
# Using a static UID/GID avoids conflicts with host users and is auditable.
RUN groupadd --gid 10001 mlops \
    && useradd --uid 10001 --gid mlops --shell /bin/false --no-create-home mlops \
    && chown -R mlops:mlops /app

USER mlops

# ── Runtime ───────────────────────────────────────────────────────────────────
# MLFLOW_TRACKING_URI can be overridden at container launch time:
#   docker run -e MLFLOW_TRACKING_URI=http://your-server:5000 ...
ENV MLFLOW_TRACKING_URI=http://localhost:5000

CMD ["python", "src/train.py"]
