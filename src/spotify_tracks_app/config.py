"""Central configuration: paths, feature definitions, and sampling settings.

Everything that another module might want to tweak lives here, so there is a
single, obvious place to look. Paths default to sensible values but can be
overridden with environment variables, which keeps the code portable and keeps
data strictly outside the repository (code/data hygiene).
"""

from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------------- #
# Data location (kept OUTSIDE the repository).                                 #
# --------------------------------------------------------------------------- #
# The data directory holds precomputed artefacts (e.g. the UMAP parquet). It is
# deliberately outside the repo tree. Override with SPOTIFY_DATA_DIR.
DATA_DIR: Path = Path(
    os.environ.get("SPOTIFY_DATA_DIR", "/home/wo222/spotify-tracks-web-app-data")
)

# Kaggle dataset that backs the app. Fetched via kagglehub on first precompute.
KAGGLE_DATASET: str = "zaheenhamidani/ultimate-spotify-tracks-db"
RAW_CSV_NAME: str = "SpotifyFeatures.csv"

# Optional escape hatch: point directly at a local CSV instead of downloading.
RAW_CSV_OVERRIDE: str | None = os.environ.get("SPOTIFY_RAW_CSV")

# Precomputed artefacts written by scripts/precompute.py.
UMAP_PARQUET: Path = DATA_DIR / "umap.parquet"
NUMERIC_FEATURES_JSON: Path = DATA_DIR / "numeric_features.json"

# --------------------------------------------------------------------------- #
# Feature definitions.                                                         #
# --------------------------------------------------------------------------- #
# Candidate features considered "numeric". The actual numeric set is resolved
# in the preprocessing step by keeping only those with at least
# MIN_UNIQUE_FOR_NUMERIC distinct values (see preprocessing.py). In the raw CSV
# `key`, `mode` and `time_signature` are strings / low-cardinality and are
# therefore dropped automatically by that rule.
CANDIDATE_NUMERIC_FEATURES: list[str] = [
    "acousticness",
    "danceability",
    "duration_ms",
    "energy",
    "instrumentalness",
    "key",
    "liveness",
    "loudness",
    "mode",
    "speechiness",
    "tempo",
    "time_signature",
    "valence",
]

# A feature counts as numeric only if it has at least this many unique values.
MIN_UNIQUE_FOR_NUMERIC: int = 20

# `popularity` is the target for the top/bottom comparison (Tab 2) and must
# never be fed into UMAP (Tab 1).
POPULARITY_COLUMN: str = "popularity"
GENRE_COLUMN: str = "genre"

# --------------------------------------------------------------------------- #
# Sampling (development speed-up).                                             #
# --------------------------------------------------------------------------- #
# During development we work on a reproducible fraction of the rows. Set
# SAMPLE_FRAC = 1.0 to use the full dataset -- this single toggle removes (or
# restores) the sampling step; see data.apply_sampling.
SAMPLE_FRAC: float = 1.0
SAMPLE_RANDOM_STATE: int = 42
