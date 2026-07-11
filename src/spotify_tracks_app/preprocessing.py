"""Preprocessing: resolve the numeric feature set and precompute the UMAP map.

This runs *offline* (see scripts/precompute.py), never at app start. Two jobs:

1. Decide which candidate features are genuinely numeric.
2. Project those features to 2-D with UMAP for the scatter plot.

A feature qualifies as numeric only if BOTH hold:

* the column is a strictly numeric dtype -- guaranteeing it contains numbers
  only and no strings (so text/categorical columns such as ``key`` -> "C#",
  ``mode`` -> "Major", ``time_signature`` -> "4/4" are excluded); and
* it has at least :data:`config.MIN_UNIQUE_FOR_NUMERIC` distinct values (so
  low-cardinality codes do not count as continuous numeric features).
"""

from __future__ import annotations

import json

import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype

from . import config


def is_strictly_numeric(series: pd.Series) -> bool:
    """Return whether a column contains numbers only (no strings, no booleans).

    Args:
        series: The column to inspect.

    Returns:
        ``True`` if the column's dtype is numeric and not boolean, else
        ``False``. Object/string columns (e.g. "C#", "Major", "4/4") return
        ``False`` because their dtype is not numeric.
    """
    if is_bool_dtype(series):
        return False
    return is_numeric_dtype(series)


def detect_numeric_features(df: pd.DataFrame) -> list[str]:
    """Resolve which candidate features are numeric enough to analyse.

    A candidate is kept only if it is strictly numeric (no strings) and has at
    least :data:`config.MIN_UNIQUE_FOR_NUMERIC` unique non-null values. Order
    follows :data:`config.CANDIDATE_NUMERIC_FEATURES`.

    Args:
        df: The (sampled) dataset.

    Returns:
        The resolved list of numeric feature names.
    """
    features: list[str] = []
    for name in config.CANDIDATE_NUMERIC_FEATURES:
        if name not in df.columns:
            continue
        column = df[name]
        if not is_strictly_numeric(column):
            continue
        if column.nunique(dropna=True) < config.MIN_UNIQUE_FOR_NUMERIC:
            continue
        features.append(name)
    return features


def save_numeric_features(features: list[str]) -> None:
    """Persist the resolved numeric feature list to the data directory.

    Args:
        features: The numeric feature names to store.
    """
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.NUMERIC_FEATURES_JSON.write_text(json.dumps(features, indent=2))


def load_numeric_features() -> list[str]:
    """Load the numeric feature list produced by the preprocessing step.

    Returns:
        The stored numeric feature names.

    Raises:
        FileNotFoundError: If the precompute step has not been run yet.
    """
    if not config.NUMERIC_FEATURES_JSON.is_file():
        raise FileNotFoundError(
            f"Numeric features not found at {config.NUMERIC_FEATURES_JSON}. "
            "Run scripts/precompute.py first."
        )
    return json.loads(config.NUMERIC_FEATURES_JSON.read_text())


def compute_umap(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """Project the numeric features to 2-D with UMAP.

    Features are standardised (zero mean, unit variance) before UMAP so that
    columns on different scales (e.g. ``tempo`` vs ``danceability``) contribute
    comparably. ``genre`` is intentionally *not* used, so colouring by genre
    later reflects structure UMAP found on its own. ``popularity`` is also
    excluded (it is the target of Tab 2).

    Args:
        df: The (sampled) dataset containing at least ``features``.
        features: The numeric feature names to embed.

    Returns:
        A copy of ``df`` with added ``umap_x`` and ``umap_y`` columns.
    """
    # Imported lazily: umap/numba are heavy and only needed for precompute.
    import umap
    from sklearn.preprocessing import StandardScaler

    scaled = StandardScaler().fit_transform(df[features].to_numpy())
    reducer = umap.UMAP(
        n_components=2,
        random_state=config.SAMPLE_RANDOM_STATE,  # reproducible embedding.
    )
    embedding = reducer.fit_transform(scaled)

    result = df.copy()
    result["umap_x"] = embedding[:, 0]
    result["umap_y"] = embedding[:, 1]
    return result
