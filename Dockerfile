# syntax=docker/dockerfile:1
# Container image for the Dash app. Data is NEVER baked in -- it is mounted at
# runtime as a volume at /data (see SPOTIFY_DATA_DIR), keeping code/data hygiene.
FROM python:3.12-slim

# Bring in the uv binary from its official image.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Put the venv on PATH so gunicorn is found directly.
    PATH="/app/.venv/bin:$PATH" \
    # App reads precomputed artefacts from here (mounted volume).
    SPOTIFY_DATA_DIR=/data

WORKDIR /app

# 1) Install dependencies first (cached layer), without the project itself.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev

# 2) Install the project.
COPY src ./src
RUN uv sync --frozen --no-dev

# Data is provided at runtime via a volume mount (never copied into the image).
VOLUME ["/data"]
EXPOSE 8050

# Run as a non-root user.
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

# WSGI entrypoint is app:server -- app.py sets the Dash layout and registers the
# API; server.py alone would have no layout.
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "--workers", "2", \
     "spotify_tracks_app.app:server"]
