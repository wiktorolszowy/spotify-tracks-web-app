"""Tests for numeric-feature detection.

Two levels of coverage:

* Synthetic tests exercise the *rule* (numeric-only AND >= 20 unique) and run
  everywhere, including CI, without any data.
* One real-data test asserts the rule applied to the actual CSV yields exactly
  the expected 10 features. It auto-skips unless the raw data is made available
  (set ``SPOTIFY_RAW_CSV`` or ``SPOTIFY_RUN_REAL_DATA_TESTS``), so CI stays
  data-free.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
import pytest

from spotify_tracks_app import config, preprocessing

_RUN_REAL_DATA = bool(
    os.environ.get("SPOTIFY_RAW_CSV") or os.environ.get("SPOTIFY_RUN_REAL_DATA_TESTS")
)

_EXPECTED_REAL_FEATURES = [
    "acousticness",
    "danceability",
    "duration_ms",
    "energy",
    "instrumentalness",
    "liveness",
    "loudness",
    "speechiness",
    "tempo",
    "valence",
]


def _synthetic_df() -> pd.DataFrame:
    """Build a small frame covering each accept/reject case."""
    n = 100
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {
            "string_col": ["C#"] * n,  # strings -> reject
            "few_unique": [1, 2, 3, 4] * (n // 4),  # numeric but < 20 unique
            "bool_col": [True, False] * (n // 2),  # boolean -> reject
            "many_unique": rng.integers(0, 1000, n),  # numeric, >= 20 unique
        }
    )


def test_is_strictly_numeric():
    assert preprocessing.is_strictly_numeric(pd.Series([1.0, 2.0, 3.0]))
    assert not preprocessing.is_strictly_numeric(pd.Series(["a", "b", "c"]))
    assert not preprocessing.is_strictly_numeric(pd.Series([True, False, True]))


def test_detect_numeric_logic(monkeypatch):
    df = _synthetic_df()
    monkeypatch.setattr(
        config,
        "CANDIDATE_NUMERIC_FEATURES",
        ["string_col", "few_unique", "bool_col", "many_unique", "missing_col"],
    )
    assert preprocessing.detect_numeric_features(df) == ["many_unique"]


@pytest.mark.skipif(
    not _RUN_REAL_DATA,
    reason="real dataset not available; set SPOTIFY_RUN_REAL_DATA_TESTS to run",
)
def test_detect_numeric_real_data():
    from spotify_tracks_app import data

    df = data.load_raw()
    assert preprocessing.detect_numeric_features(df) == _EXPECTED_REAL_FEATURES
