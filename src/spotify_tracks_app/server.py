"""Server objects shared across the app.

Dash runs on Flask, so we create the Flask ``server`` explicitly and hand it to
Dash. Exposing ``server`` at module level lets a WSGI server (gunicorn, and
Plotly Cloud) import it as ``spotify_tracks_app.server:server``. It is also the
single place to attach plain Flask API routes (see api.py).
"""

from __future__ import annotations

from dash import Dash
from flask import Flask

server: Flask = Flask(__name__)

app: Dash = Dash(
    __name__,
    server=server,
    title="Spotify Tracks Explorer",
    # Tab content is added by callbacks after load, so its components are not in
    # the initial layout; allow that.
    suppress_callback_exceptions=True,
)
