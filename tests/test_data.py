"""Tests for the development sampling step."""

from __future__ import annotations

import pandas as pd

from spotify_tracks_app import config, data


def test_apply_sampling_is_reproducible(monkeypatch):
    monkeypatch.setattr(config, "SAMPLE_FRAC", 0.1)
    df = pd.DataFrame({"a": range(1000)})

    first = data.apply_sampling(df)
    second = data.apply_sampling(df)

    assert len(first) == 100
    pd.testing.assert_frame_equal(first, second)


def test_apply_sampling_disabled_returns_input(monkeypatch):
    monkeypatch.setattr(config, "SAMPLE_FRAC", 1.0)
    df = pd.DataFrame({"a": range(10)})

    result = data.apply_sampling(df)

    pd.testing.assert_frame_equal(result, df)
