"""Loading the raw dataset and the (optional) development sampling step.

The raw CSV is fetched from Kaggle with ``kagglehub`` so the project is
reproducible from a clean checkout: the first call downloads (and caches) the
data, later calls reuse the cache. A local override is available for offline use.
"""

from __future__ import annotations

from pathlib import Path

import kagglehub
import pandas as pd

from . import config


def get_raw_csv_path() -> Path:
    """Return the path to the raw ``SpotifyFeatures.csv``.

    Resolution order:

    1. ``SPOTIFY_RAW_CSV`` environment variable, if set (offline escape hatch).
    2. Kaggle download via ``kagglehub`` (cached after the first run).

    Returns:
        Path to the raw CSV file.

    Raises:
        FileNotFoundError: If the resolved CSV path does not exist.
    """
    if config.RAW_CSV_OVERRIDE:
        csv_path = Path(config.RAW_CSV_OVERRIDE)
    else:
        dataset_dir = Path(kagglehub.dataset_download(config.KAGGLE_DATASET))
        csv_path = dataset_dir / config.RAW_CSV_NAME

    if not csv_path.is_file():
        raise FileNotFoundError(f"Raw dataset CSV not found at: {csv_path}")
    return csv_path


def load_raw() -> pd.DataFrame:
    """Load the full raw dataset into a DataFrame.

    Returns:
        The raw Spotify tracks data, unmodified.
    """
    return pd.read_csv(get_raw_csv_path())


def apply_sampling(df: pd.DataFrame) -> pd.DataFrame:
    """Return a reproducible sample of the rows (development speed-up).

    Controlled by :data:`config.SAMPLE_FRAC`. When it is ``1.0`` the input is
    returned unchanged, so the sampling step can be disabled (or re-enabled)
    from a single place without touching call sites.

    Args:
        df: The DataFrame to sample.

    Returns:
        A row-sample of ``df`` (or ``df`` itself when sampling is disabled).
    """
    if config.SAMPLE_FRAC >= 1.0:
        return df
    return df.sample(
        frac=config.SAMPLE_FRAC,
        random_state=config.SAMPLE_RANDOM_STATE,
    ).reset_index(drop=True)


def load_sampled() -> pd.DataFrame:
    """Load the raw data and apply the development sampling step.

    Returns:
        The (optionally) sampled Spotify tracks data.
    """
    return apply_sampling(load_raw())
