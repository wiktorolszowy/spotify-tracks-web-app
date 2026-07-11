"""Tab 1: UMAP map of tracks (placeholder; populated in a later phase)."""

from __future__ import annotations

from dash import Dash, html
from dash.development.base_component import Component

TAB_LABEL: str = "1 - UMAP map"
TAB_VALUE: str = "umap"


def layout() -> Component:
    """Return the UMAP tab content.

    Returns:
        The tab's Dash layout.
    """
    return html.Div(
        [
            html.H2("UMAP map of tracks"),
            html.P(
                "Coming soon: a 2-D UMAP scatter of every track, coloured " "by genre."
            ),
        ]
    )


def register_callbacks(app: Dash) -> None:
    """Register this tab's callbacks (none yet).

    Args:
        app: The Dash app to register callbacks on.
    """
