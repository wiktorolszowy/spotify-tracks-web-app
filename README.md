# Spotify Tracks Web App

A [Dash](https://dash.plotly.com/) + [Plotly](https://plotly.com/python/) app for
exploring the [Ultimate Spotify Tracks DB](https://www.kaggle.com/datasets/zaheenhamidani/ultimate-spotify-tracks-db).

Two tabs:

1. **UMAP map** — every track is one point in a 2-D UMAP projection of its numeric
   audio features, coloured by genre.
2. **Top vs. bottom popularity** — for a chosen genre, compares the audio-feature
   distributions of the top-5% and bottom-5% most popular tracks, ranked by the
   two-sample Kolmogorov–Smirnov statistic.

## Data hygiene

**No data lives in this repo.** Code and data are strictly separated:

- Code: this repository.
- Data: `/home/wo222/spotify-tracks-web-app-data` (override with the
  `SPOTIFY_DATA_DIR` environment variable).

The raw CSV is fetched automatically from Kaggle via `kagglehub` on the first
precompute run, so the project is reproducible from a clean checkout.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.
Requires **uv >= 0.5** (for PEP 735 dependency groups; developed with uv 0.11.28).
Update uv with `uv self update`, or install it via
`curl -LsSf https://astral.sh/uv/install.sh | sh`.

```bash
uv sync                 # create .venv and install runtime + dev deps
uv run pre-commit install
```

## Workflow

```bash
# 1. Precompute: fetch data, detect numeric features, run UMAP, write parquet.
uv run python scripts/precompute.py

# 2. Run the app locally.
uv run python -m spotify_tracks_app.app

# 3. Quality checks.
uv run pre-commit run --all-files
uv run pytest
```

## Sampling (development speed-up)

During development the pipeline uses a reproducible **10% sample** of the rows.
To run on the full dataset, set `SAMPLE_FRAC = 1.0` in
`src/spotify_tracks_app/config.py` (single toggle point) and re-run the precompute.

## Deployment

- **Local container:** the image never contains data; mount the data directory
  as a volume at `/data`:

  ```bash
  docker build -t spotify-tracks-app .
  docker run --rm -p 8050:8050 \
      -v /home/wo222/spotify-tracks-web-app-data:/data:ro \
      spotify-tracks-app
  # open http://localhost:8050
  ```
- **Plotly Cloud:** `scripts/deploy_prep.py` builds a temporary folder combining the
  code with the precomputed data files for the Dash/Plotly CLI, keeping the repo
  itself data-free.
