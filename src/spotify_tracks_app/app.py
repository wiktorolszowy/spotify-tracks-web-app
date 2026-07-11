"""Dash application entrypoint.

Builds the page shell and wires the tab registry. Tabs are rendered generically
from :data:`spotify_tracks_app.tabs.TABS`, so adding a tab needs no changes
here. The tab bar is styled to be unmistakable, so users clearly see that there
is more than one view.

Run locally:  ``uv run python -m spotify_tracks_app.app``
"""

from __future__ import annotations

from dash import Input, Output, dcc, html
from dash.development.base_component import Component

from .server import app, server  # noqa: F401  (server re-exported for WSGI)
from .tabs import TABS

# Styling that makes the (unselected) tabs obvious, and the selected one pop.
_TAB_STYLE = {
    "padding": "12px 18px",
    "fontWeight": "bold",
    "fontSize": "17px",
    "border": "1px solid #b3b3b3",
    "backgroundColor": "#f2f2f2",
}
_TAB_SELECTED_STYLE = {
    "padding": "12px 18px",
    "fontWeight": "bold",
    "fontSize": "17px",
    "color": "white",
    "backgroundColor": "#1DB954",  # Spotify green.
    "border": "1px solid #1DB954",
}


def _build_layout() -> Component:
    """Build the top-level page layout.

    Returns:
        The app's root layout.
    """
    return html.Div(
        style={"maxWidth": "1200px", "margin": "0 auto", "padding": "16px"},
        children=[
            html.H1("Spotify Tracks Explorer"),
            html.P(
                "Explore the tracks using the two tabs below - click each one.",
                style={"color": "#555"},
            ),
            dcc.Tabs(
                id="tabs",
                value=TABS[0].TAB_VALUE,
                children=[
                    dcc.Tab(
                        label=tab.TAB_LABEL,
                        value=tab.TAB_VALUE,
                        style=_TAB_STYLE,
                        selected_style=_TAB_SELECTED_STYLE,
                    )
                    for tab in TABS
                ],
            ),
            html.Div(
                id="tab-content",
                style={"marginTop": "20px"},
            ),
        ],
    )


app.layout = _build_layout()


@app.callback(Output("tab-content", "children"), Input("tabs", "value"))
def render_tab(tab_value: str) -> Component:
    """Render the content of the selected tab.

    Args:
        tab_value: The ``value`` of the selected tab.

    Returns:
        The selected tab's layout (or a fallback message).
    """
    for tab in TABS:
        if tab.TAB_VALUE == tab_value:
            return tab.layout()
    return html.Div("Unknown tab.")


# Register each tab's own callbacks once, at import time.
for _tab in TABS:
    _tab.register_callbacks(app)


if __name__ == "__main__":
    app.run(debug=True)
