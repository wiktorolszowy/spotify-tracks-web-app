"""Minimal JSON API served by the Dash app's Flask server.

Dash already runs on Flask, so the API is just a few plain Flask routes attached
to the same ``server`` (no extra framework). Endpoints:

* ``GET /api/health``   -> liveness check.
* ``GET /api/features`` -> the resolved numeric feature list.
* ``GET /api/genres``   -> the available genres.

Routes are attached via :func:`register_api` (called from server.py) so they
exist whenever the WSGI ``server`` is imported, including under gunicorn.
"""

from __future__ import annotations

import functools

import pandas as pd
from flask import Flask, jsonify
from werkzeug.wrappers import Response

from . import config, preprocessing


@functools.lru_cache(maxsize=1)
def _genres() -> list[str]:
    """Return the sorted list of genres (cached).

    Reads only the genre column from the precomputed parquet.

    Returns:
        The available genre names.
    """
    df = pd.read_parquet(config.UMAP_PARQUET, columns=[config.GENRE_COLUMN])
    return sorted(df[config.GENRE_COLUMN].unique().tolist())


def register_api(server: Flask) -> None:
    """Attach the JSON API routes to a Flask server.

    Args:
        server: The Flask server to register routes on.
    """

    @server.route("/api/health")
    def health() -> Response:
        """Liveness check.

        Returns:
            ``{"status": "ok"}``.
        """
        return jsonify({"status": "ok"})

    @server.route("/api/features")
    def features() -> Response | tuple[Response, int]:
        """Return the resolved numeric feature list.

        Returns:
            The feature list, or a 503 error if precompute has not run.
        """
        try:
            return jsonify({"numeric_features": preprocessing.load_numeric_features()})
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 503

    @server.route("/api/genres")
    def genres() -> Response | tuple[Response, int]:
        """Return the available genres.

        Returns:
            The genre list, or a 503 error if precompute has not run.
        """
        if not config.UMAP_PARQUET.is_file():
            return jsonify({"error": "Precomputed data not found."}), 503
        return jsonify({"genres": _genres()})
