"""Tests for the KS tab's ranking and grouping helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from spotify_tracks_app import config
from spotify_tracks_app.tabs import ks_tab


def test_ranked_features_orders_by_ks_descending():
    rng = np.random.default_rng(0)
    n = 300
    # "f_diff" is strongly shifted between groups; "f_same" is not.
    bottom = pd.DataFrame(
        {"f_same": rng.normal(0, 1, n), "f_diff": rng.normal(0, 1, n)}
    )
    top = pd.DataFrame({"f_same": rng.normal(0, 1, n), "f_diff": rng.normal(5, 1, n)})

    ranked = ks_tab._ranked_features(bottom, top, ["f_same", "f_diff"])
    features = [name for name, _ in ranked]
    scores = [score for _, score in ranked]

    assert features[0] == "f_diff"
    assert scores == sorted(scores, reverse=True)


def test_split_groups_sizes():
    df = pd.DataFrame({config.POPULARITY_COLUMN: range(100)})
    bottom, top, group_size = ks_tab._split_groups(df)

    assert group_size == 5  # 5% of 100
    assert bottom[config.POPULARITY_COLUMN].max() < top[config.POPULARITY_COLUMN].min()
