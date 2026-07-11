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
- **Plotly Cloud:** the app folder must contain the data (Cloud has no volume
  mounts), while the repo stays data-free. `scripts/deploy_prep.py` assembles a
  self-contained folder **outside** the repo that combines the code, the
  precomputed data, a runtime-only `pyproject.toml`, and an `app.py`
  entrypoint:

  ```bash
  # 1. Precompute first (writes umap.parquet to the data dir).
  uv run python scripts/precompute.py

  # 2. Build the deploy folder (default: ../spotify-tracks-web-app-deploy).
  uv run python scripts/deploy_prep.py

  # 3. Publish it (any one of):
  cd ../spotify-tracks-web-app-deploy
  pip install plotly-cloud     # provides the `plotly` CLI
  deactivate
  plotly user login            # authenticate (OAuth in the browser)
  plotly app publish           # publish to Plotly Cloud
  #   or: pip install "dash[cloud]" && python app.py, then use the dev-tools panel
  #   or: upload the folder at https://cloud.plotly.com (< 80 MiB)
  ```

  The bundle is ~17 MiB and installs no umap/precompute dependencies, so Cloud
  builds are small and fast.

## What's next (if there was time)

- **Align on user needs.** Talk to end users about which patterns they actually
  want to explore, and shape the tabs around those questions.
- **Review with a frontend expert.** Discuss the current UI/UX and architecture
  with an experienced frontend engineer.
- **Harden the CI pipeline.** Add Sonar (code quality) and Snyk (dependency /
  security) checks.
- **Expand the test suite.** Add many more tests, including end-to-end browser
  tests with Playwright.
- **Add analytical sanity checks.** Independently regenerate the same plots as
  non-interactive figures to confirm the patterns match. I have not run any such
  sanity checks yet.
- **Automate deployment.** Make the release to Plotly Cloud a one-command (or
  fully automated) step.
- **Speed up the UMAP tab.** Rendering was instant on the 10% sample but takes a
  few seconds on the full ~230k-row dataset; investigate faster loading /
  rendering.
- **Investigate duplicates.** Some `track_id` values appear multiple times;
  understand why and decide how to handle them.
- **Enforce PR-only workflow for `develop`.** Currently only `main` is protected
  via PRs; require PRs for `develop` too and drop direct pushes.
- **Improve feature selection.** Find a more principled way to decide which
  features are used for the UMAP projection (and the other analyses); the current
  "numeric-only + >= 20 unique" heuristic is a bit ad hoc.
- **Fix the histogram flash.** The KS histograms briefly render with bare axes
  (under a second) before the bars appear; investigate whether there is a fix.
- **Slim the Docker image.** The image is ~3.5 GB. Split precompute-only
  dependencies (`umap-learn`, `scikit-learn`, `numba`) into a separate
  dependency group so the runtime image is much smaller.
- **Align the local and Plotly Cloud environments.** Local development uses the
  Docker image (full `pyproject.toml` + gunicorn), while the Cloud deploy bundle
  has its own runtime-only `pyproject.toml`. Converge these so the two
  environments (dependencies, Python version, run command) stay in sync and
  cannot drift.
