# Use official lightweight Python 3.12 image
FROM python:3.12-slim

# Install system dependencies required for PostGIS/psycopg2 and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for ultra-fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory inside the container
WORKDIR /app

# Enable bytecode compilation and copy dependency files first for optimal caching
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency configuration files, packaging readme, and source structure
COPY pyproject.toml uv.lock README.md* ./
COPY src/ ./src/

# Install project dependencies using uv (standard virtual environment build)
RUN uv sync --frozen --no-dev

# Copy the rest of the application source code (tests, scripts, etc.)
COPY . .

# Set Python path to include the src directory and virtual environment binaries
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/src

# Expose FastAPI application port
EXPOSE 8000

# Default command (overridden by docker-compose for celery workers)
CMD ["uv", "run", "uvicorn", "agrisim.main:app", "--host", "0.0.0.0", "--port", "8000"]