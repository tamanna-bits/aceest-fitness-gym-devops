FROM python:3.12-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files first (for Docker caching)
COPY pyproject.toml poetry.lock* /app/

# Disable Poetry virtualenv (Docker already isolates environment)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy project files
COPY . .

# ── Stage 2: Test ─────────────────────────────────────────────────────────
FROM base AS test
RUN python -m pytest tests/ -v --tb=short

# ── Stage 3: Production ────────────────────────────────────────────────────
FROM base AS production

ENV FLASK_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser
USER appuser

CMD ["python", "main.py"]