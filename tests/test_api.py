"""Test the API health endpoint (no data required)."""

from __future__ import annotations


def test_health_endpoint_returns_ok():
    import spotify_tracks_app.app  # noqa: F401  (imports set the Dash layout)
    from spotify_tracks_app.server import server

    client = server.test_client()
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
