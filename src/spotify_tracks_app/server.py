"""Server objects shared across the app.

Dash runs on Flask, so we create the Flask ``server`` explicitly and hand it to
Dash. The deployable WSGI target is ``spotify_tracks_app.app:server`` -- app.py
imports this module, sets the layout, and re-exports ``server`` (importing this
module alone leaves the Dash layout unset). This is also the single place to
attach plain Flask API routes (see api.py).
"""

from __future__ import annotations

from dash import Dash
from flask import Flask
from flask_compress import Compress

from .api import register_api

server: Flask = Flask(__name__)

# Gzip responses (notably the large UMAP figure payload) before sending them to
# the browser. This is a no-op for already-small responses.
Compress(server)

app: Dash = Dash(
    __name__,
    server=server,
    title="Spotify Tracks Explorer",
    # Tab content is added by callbacks after load, so its components are not in
    # the initial layout; allow that.
    suppress_callback_exceptions=True,
)

# Attach the JSON API routes so they exist for any WSGI entrypoint.
register_api(server)
