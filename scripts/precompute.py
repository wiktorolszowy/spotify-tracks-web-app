"""Offline precompute step: fetch data, resolve numeric features, run UMAP.

Run once (and whenever the sampling changes):

    uv run python scripts/precompute.py

Writes two artefacts into the data directory (outside the repo):

* ``numeric_features.json`` -- the resolved numeric feature list.
* ``umap.parquet``          -- all columns plus ``umap_x`` / ``umap_y``.

The Dash app only reads these; it never runs UMAP itself.
"""

from __future__ import annotations

from spotify_tracks_app import config, data, preprocessing


def main() -> None:
    """Fetch the data, resolve numeric features, run UMAP, and save artefacts."""
    print(f"Data directory: {config.DATA_DIR}")
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading data (sampling: " f"frac={config.SAMPLE_FRAC}) ...")
    df = data.load_sampled()
    print(f"  rows={len(df):,} cols={df.shape[1]}")

    features = preprocessing.detect_numeric_features(df)
    preprocessing.save_numeric_features(features)
    print(f"Numeric features ({len(features)}): {features}")

    print("Running UMAP (this can take a while) ...")
    embedded = preprocessing.compute_umap(df, features)

    embedded.to_parquet(config.UMAP_PARQUET, index=False)
    print(f"Wrote {config.UMAP_PARQUET} ({len(embedded):,} rows)")


if __name__ == "__main__":
    main()
