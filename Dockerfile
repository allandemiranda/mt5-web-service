# ──────────────────────────────────────────────────────────────────────────────
# Stage 1 – Builder: install Python dependencies into a clean virtual-env
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# System dependencies needed to compile certain wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Create venv and install only non-Windows dependencies
# (MetaTrader5 package is Windows-only and excluded automatically via platform_system marker)
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ──────────────────────────────────────────────────────────────────────────────
# Stage 2 – Runtime: minimal image with only the installed packages
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy virtual-env from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application source
COPY app/ ./app/

# Make sure the venv binaries are used
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Default runtime port (must match .env PORT)
EXPOSE 8000

USER appuser

# Entrypoint: run uvicorn directly (honours HOST/PORT env vars via app/main.py)
CMD ["python", "-m", "app.main"]
