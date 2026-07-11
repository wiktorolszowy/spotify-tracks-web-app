"""Tab 2: top vs. bottom popularity feature comparison.

For a chosen genre we sort its tracks by ``popularity``, take the bottom 5% and
top 5% as two groups, and compare the two groups' distribution for each numeric
feature (the same features used by UMAP). Each feature gets an overlaid double
histogram so the two groups can be compared visually (hover, zoom, toggle).

Features are ranked by the **two-sample Kolmogorov-Smirnov (KS) statistic**,
shown descending, so the features that separate popular from unpopular tracks
appear first. The KS statistic is used because it compares the *whole*
distribution, not just means or medians.

This tab is computed on the fly (no precompute): the KS test and histograms are
cheap even on the full dataset.
"""

from __future__ import annotations

import functools

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from dash.development.base_component import Component
from plotly.subplots import make_subplots
from scipy.stats import ks_2samp

from .. import config, preprocessing

TAB_LABEL: str = "2 - Top vs. bottom popularity"
TAB_VALUE: str = "ks"

# Fraction of each genre taken as the bottom / top popularity group.
_POP_FRACTION: float = 0.05
_BOTTOM_COLOR: str = "#636EFA"
_TOP_COLOR: str = "#EF553B"
_DEFAULT_GENRE: str = "Pop"


@functools.lru_cache(maxsize=1)
def _load_df() -> pd.DataFrame:
    """Load the (sampled) dataset with all columns (cached).

    Reuses the precomputed parquet, which already holds every original column.

    Returns:
        The dataset used for the comparison.
    """
    return pd.read_parquet(config.UMAP_PARQUET)


def _split_groups(genre_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """Split a genre's tracks into bottom-5% and top-5% popularity groups.

    Args:
        genre_df: Tracks belonging to a single genre.

    Returns:
        A ``(bottom, top, group_size)`` tuple.
    """
    n = len(genre_df)
    group_size = max(1, round(_POP_FRACTION * n))
    ordered = genre_df.sort_values(config.POPULARITY_COLUMN)
    return ordered.head(group_size), ordered.tail(group_size), group_size


def _ranked_features(
    bottom: pd.DataFrame, top: pd.DataFrame, features: list[str]
) -> list[tuple[str, float]]:
    """Rank features by how different the two groups' distributions are.

    Args:
        bottom: Bottom-popularity group.
        top: Top-popularity group.
        features: Numeric feature names to compare.

    Returns:
        ``(feature, ks_statistic)`` pairs sorted by KS statistic, descending.
    """
    scores = [
        (feature, float(ks_2samp(bottom[feature], top[feature]).statistic))
        for feature in features
    ]
    scores.sort(key=lambda item: item[1], reverse=True)
    return scores


def _build_figure(genre: str) -> go.Figure:
    """Build the ranked overlaid-histogram figure for a genre.

    Args:
        genre: The genre to analyse.

    Returns:
        A Plotly figure with one overlaid double histogram per feature.
    """
    df = _load_df()
    features = preprocessing.load_numeric_features()
    genre_df = df[df[config.GENRE_COLUMN] == genre]
    bottom, top, group_size = _split_groups(genre_df)
    ranked = _ranked_features(bottom, top, features)

    pct = int(_POP_FRACTION * 100)
    titles = [f"{feature}: KS = {ks:.3f}" for feature, ks in ranked]
    fig = make_subplots(rows=len(ranked), cols=1, subplot_titles=titles)

    for row, (feature, _) in enumerate(ranked, start=1):
        first = row == 1  # only the first row contributes legend entries.
        fig.add_trace(
            go.Histogram(
                x=bottom[feature],
                name=f"Bottom {pct}%",
                legendgroup="bottom",
                showlegend=first,
                marker_color=_BOTTOM_COLOR,
                opacity=0.6,
                nbinsx=30,
                # Normalise so each histogram's area = 1, making groups of
                # different sizes directly comparable.
                histnorm="probability density",
            ),
            row=row,
            col=1,
        )
        fig.add_trace(
            go.Histogram(
                x=top[feature],
                name=f"Top {pct}%",
                legendgroup="top",
                showlegend=first,
                marker_color=_TOP_COLOR,
                opacity=0.6,
                nbinsx=30,
                histnorm="probability density",
            ),
            row=row,
            col=1,
        )

    fig.update_layout(
        barmode="overlay",
        height=260 * len(ranked),
        legend_title_text="Group (click to toggle)",
        title_text=(
            f"{genre}: bottom vs top {pct}% by popularity "
            f"(n = {group_size} tracks per group)"
        ),
        margin={"l": 40, "r": 40, "t": 90, "b": 40},
    )
    fig.update_yaxes(title_text="Density")
    return fig


def _explanation() -> Component:
    """Return the on-page explanation, including a KS-test note.

    Returns:
        A Markdown component describing what the plot shows.
    """
    pct = int(_POP_FRACTION * 100)
    return dcc.Markdown(
        f"""
Pick a genre. Its tracks are sorted by **popularity**; the least popular {pct}%
and most popular {pct}% form two groups. For each numeric audio feature we
overlay the two groups' histograms, so you can see how the feature's
distribution differs between unpopular and popular tracks. Charts are ordered by
the **KS statistic** (largest difference first), which is also shown in each
title.

**What is the KS test?** The two-sample **Kolmogorov-Smirnov**
test measures how different two distributions are by taking the *largest
vertical gap* between their cumulative distribution functions (CDFs). The
statistic runs from **0** (identical distributions) to **1** (no overlap at
all). Unlike comparing only means or medians, it is sensitive to differences
*anywhere* in the distribution - shifts, spread, or shape - which is why we use
it to rank the features.
""",
        style={
            "backgroundColor": "#f7f7f7",
            "padding": "12px",
            "borderRadius": "6px",
        },
    )


def layout() -> Component:
    """Return the popularity-comparison tab content.

    Returns:
        The tab's Dash layout, or a friendly message if data is missing.
    """
    if not config.UMAP_PARQUET.is_file():
        return html.Div(
            [
                html.H2("Top vs. bottom popularity"),
                html.P(
                    "Precomputed data not found. Run "
                    "`uv run python scripts/precompute.py` first."
                ),
            ]
        )

    genres = sorted(_load_df()[config.GENRE_COLUMN].unique())
    default_genre = _DEFAULT_GENRE if _DEFAULT_GENRE in genres else genres[0]
    return html.Div(
        [
            html.H2("Top vs. bottom popularity"),
            _explanation(),
            html.P(
                "Interesting pattern: (when selecting 'Comedy') in comedy tracks "
                "loudness seems to be associated with higher popularity "
                "(closer to 0 -> louder).",
                style={"fontWeight": "bold", "color": "#1DB954"},
            ),
            # Wrapped in a positioned, high-z-index container so the open
            # dropdown menu renders solidly above the graph below it.
            html.Div(
                [
                    html.Label("Genre:", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="ks-genre",
                        options=[{"label": g, "value": g} for g in genres],
                        value=default_genre,
                        clearable=False,
                        style={"maxWidth": "360px"},
                    ),
                ],
                style={
                    "position": "relative",
                    "zIndex": 1000,
                    "marginBottom": "12px",
                },
            ),
            dcc.Graph(id="ks-graph"),
        ]
    )


def register_callbacks(app: Dash) -> None:
    """Register this tab's callbacks.

    Args:
        app: The Dash app to register callbacks on.
    """

    @app.callback(Output("ks-graph", "figure"), Input("ks-genre", "value"))
    def _update(genre: str) -> go.Figure:
        """Rebuild the ranked histograms when the selected genre changes.

        Args:
            genre: The genre chosen in the dropdown.

        Returns:
            The updated figure.
        """
        return _build_figure(genre)
