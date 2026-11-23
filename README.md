# The Managerial Merry-Go-Round

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

How long do Premier League managers last? This project builds a reproducible data
pipeline from Wikipedia's
[List of Premier League managers](https://en.wikipedia.org/wiki/List_of_Premier_League_managers)
and (later) an interactive React + D3 chart of every managerial spell since 1992.

Data from Wikipedia is licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

## Quickstart

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). uv installs the
right Python (3.12, pinned in `.python-version`) and every package, so nothing else is
needed.

```bash
git clone https://github.com/jt-39/football-manager-tenure.git
cd football-manager-tenure
uv sync          # create .venv with the exact versions in uv.lock
make data        # run the pipeline (uses the committed raw snapshot)
make test        # run the tests
make lint        # check code style with ruff
```

`make help` lists every command. You never need to activate the virtual environment:
the Makefile runs everything through `uv run`.

## How the pipeline works

Data flows one way: **raw → interim → processed**.

1. **Raw** (`manager_tenure/dataset.py`). Downloads the Wikipedia page once and saves it,
   untouched, as `data/raw/wiki_premier_league_managers_<YYYY-MM-DD>.html` with a
   matching `wiki_premier_league_managers_<YYYY-MM-DD>.metadata.json` (URL, retrieval
   time, sha256). Older snapshots are kept; the pipeline uses the newest. The snapshot is committed to git, so
   the pipeline can be rebuilt even if Wikipedia changes. If a snapshot already exists
   the download is skipped. To take a fresh one:

   ```bash
   uv run python -m manager_tenure.dataset --refresh
   ```

2. **Interim and processed** (not built yet). Parse the table, clean it, validate it with
   pandera and write `data/processed/spells.parquet` and `spells.json`.

Settings such as the URL and file names live in `manager_tenure/config.py`.

## Project layout

```
├── Makefile               <- one-command entry points: make data / lint / test
├── pyproject.toml         <- dependencies and tool settings (ruff, pytest)
├── uv.lock                <- exact locked versions (committed)
├── data
│   ├── raw                <- immutable dated snapshots + their .metadata.json (committed)
│   ├── interim            <- intermediate tables (git-ignored, rebuilt by make data)
│   └── processed          <- final cleaned data (git-ignored, rebuilt by make data)
├── docs                   <- mkdocs site, including handoff notes and open questions
├── notebooks              <- exploration only
├── manager_tenure         <- the Python package
│   ├── config.py          <- paths, URL and other settings
│   ├── dataset.py         <- download and snapshot the raw page
│   ├── features.py        <- (placeholder) cleaning and parsing, to be written
│   └── plots.py           <- (placeholder) static figures
├── tests                  <- pytest tests
└── .github/workflows      <- CI: lint, test and run the pipeline on every PR
```
