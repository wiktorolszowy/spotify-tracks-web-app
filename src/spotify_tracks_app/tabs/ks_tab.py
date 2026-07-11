"""Tab 2: top vs. bottom popularity feature comparison (placeholder)."""

from __future__ import annotations

from dash import Dash, html
from dash.development.base_component import Component

TAB_LABEL: str = "2 - Top vs. bottom popularity"
TAB_VALUE: str = "ks"


def layout() -> Component:
    """Return the popularity-comparison tab content.

    Returns:
        The tab's Dash layout.
    """
    return html.Div(
        [
            html.H2("Top vs. bottom popularity"),
            html.P(
                "Coming soon: per-feature histograms comparing the top-5% "
                "and bottom-5% most popular tracks of a genre."
            ),
        ]
    )


def register_callbacks(app: Dash) -> None:
    """Register this tab's callbacks (none yet).

    Args:
        app: The Dash app to register callbacks on.
    """
