FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl

# Install Poetry
RUN pip install poetry

# Copy dependency files first (for Docker caching)
COPY pyproject.toml poetry.lock* /app/

# Disable Poetry virtualenv (Docker already isolates environment)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy project files
COPY . .

# Expose Flask port
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]