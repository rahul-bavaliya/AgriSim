# Use official Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies required for PostGIS, compilation, and curl
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv tool
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency management files first to leverage Docker cache
COPY pyproject.toml uv.lock ./

# Install project dependencies without the virtual environment (since container is isolated)
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application code
COPY . .

# Install the project itself
RUN uv sync --frozen --no-dev

# Expose FastAPI default port
EXPOSE 8000