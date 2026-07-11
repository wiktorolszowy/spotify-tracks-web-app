"""Tab 1: UMAP map of tracks.

Each point is one track, positioned by a 2-D UMAP projection of its numeric
audio features (precomputed offline in scripts/precompute.py). Points are
coloured by ``genre``, which was *not* used to build the projection -- so any
genre grouping you see is structure UMAP found from the audio features alone.

Numeric features fed to UMAP (resolved by the ">= 20 unique values AND strictly
numeric" rule, see preprocessing.py):
    acousticness, danceability, duration_ms, energy, instrumentalness, liveness,
    loudness, speechiness, tempo, valence.
``popularity`` and the categorical columns (key, mode, time_signature) are
excluded on purpose.

Rendering uses Plotly ``Scattergl`` (WebGL) so it stays responsive even on the
full ~230k-row dataset. One trace per genre gives a clickable legend: clicking a
genre in the legend hides/shows its points.
"""

from __future__ import annotations

import functools

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.development.base_component import Component

from .. import config, preprocessing

TAB_LABEL: str = "1 - UMAP map"
TAB_VALUE: str = "umap"

# Columns that are plot coordinates rather than track data (kept out of hover).
_COORD_COLUMNS = ("umap_x", "umap_y")


@functools.lru_cache(maxsize=1)
def _load_umap_df() -> pd.DataFrame:
    """Load the precomputed UMAP table (cached for the app's lifetime).

    Returns:
        The parquet written by scripts/precompute.py.
    """
    return pd.read_parquet(config.UMAP_PARQUET)


def _hover_template(hover_columns: list[str]) -> str:
    """Build a hover template that shows every underlying CSV column.

    Args:
        hover_columns: Column names, in the order they appear in ``customdata``.

    Returns:
        A Plotly ``hovertemplate`` string.
    """
    lines = [
        f"<b>{col}</b>: %{{customdata[{i}]}}" for i, col in enumerate(hover_columns)
    ]
    # <extra></extra> removes Plotly's default trace-name box.
    return "<br>".join(lines) + "<extra></extra>"


@functools.lru_cache(maxsize=1)
def _build_figure() -> go.Figure:
    """Build the UMAP scatter figure (one WebGL trace per genre, cached).

    Returns:
        The Plotly figure.
    """
    df = _load_umap_df()
    hover_columns = [c for c in df.columns if c not in _COORD_COLUMNS]
    hovertemplate = _hover_template(hover_columns)

    fig = go.Figure()
    for genre in sorted(df[config.GENRE_COLUMN].unique()):
        sub = df[df[config.GENRE_COLUMN] == genre]
        fig.add_trace(
            go.Scattergl(
                x=sub["umap_x"],
                y=sub["umap_y"],
                mode="markers",
                name=str(genre),
                customdata=sub[hover_columns].to_numpy(),
                hovertemplate=hovertemplate,
                marker={"size": 4, "opacity": 0.6},
            )
        )

    fig.update_layout(
        height=720,
        legend_title_text="Genre (click to toggle)",
        xaxis_title="UMAP 1",
        yaxis_title="UMAP 2",
        margin={"l": 40, "r": 40, "t": 30, "b": 40},
    )
    return fig


def _explanation() -> Component:
    """Return the on-page explanation, including a UMAP-vs-PCA note.

    Returns:
        A Markdown component describing what the plot shows.
    """
    features = preprocessing.load_numeric_features()
    feature_list = ", ".join(f"`{f}`" for f in features)
    return dcc.Markdown(
        f"""
Every point is **one track**. Its position comes from a 2-D **UMAP** projection
of {len(features)} numeric audio features: {feature_list}. Genre was **not**
used for the projection, so genre clusters (colours) reflect real structure in
the audio features. Click a genre in the legend to hide/show it.

**What is UMAP?** UMAP is a *non-linear* dimensionality-reduction
method. Like PCA, it squeezes many features into 2 axes for plotting, but the
similarity to PCA ends there. **PCA** is *linear*: it finds straight-line
directions of maximum variance, so it preserves large-scale (global) structure
and its axes have a clear "variance explained" meaning. **UMAP** instead builds
a graph of each point's nearest neighbours and lays it out so that *local*
neighbourhoods are preserved: nearby points are genuinely similar tracks, and
tight clusters are meaningful. The trade-off: distances *between* far-apart
clusters (and the axes themselves) carry little quantitative meaning -- so read
UMAP for grouping, not for absolute distances.
""",
        style={
            "backgroundColor": "#f7f7f7",
            "padding": "12px",
            "borderRadius": "6px",
        },
    )


def layout() -> Component:
    """Return the UMAP tab content.

    Returns:
        The tab's Dash layout, or a friendly message if data is missing.
    """
    if not config.UMAP_PARQUET.is_file():
        return html.Div(
            [
                html.H2("UMAP map of tracks"),
                html.P(
                    "Precomputed UMAP data not found. Run "
                    "`uv run python scripts/precompute.py` first."
                ),
            ]
        )

    return html.Div(
        [
            html.H2("UMAP map of tracks"),
            _explanation(),
            html.P(
                "Interesting pattern: the audio features can be linked to genre "
                "differences, with some genres being quite distinct - check "
                "'Classical' vs. 'Comedy', e.g.",
                style={"fontWeight": "bold", "color": "#1DB954"},
            ),
            dcc.Graph(
                id="umap-graph",
                figure=_build_figure(),
                config={"scrollZoom": True},
            ),
        ]
    )


def register_callbacks(app: Dash) -> None:
    """Register this tab's callbacks.

    Legend clicks (hide/show a genre) are handled natively by Plotly, so no
    server-side callback is needed.

    Args:
        app: The Dash app to register callbacks on.
    """
