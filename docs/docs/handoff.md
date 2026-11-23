# Handoff: milestone 1a (Python basics)

Done by a cloud session on 2026-11-22/23, following
[`docs/tasks/milestone-1a-python-basics.md`](../tasks/milestone-1a-python-basics.md).
Only the first half of milestone 1 was done. No parsing, cleaning, pandera schema or web
work.

## What was done (one commit each)

1. **Chore: Remove the unused ML scaffold.** Deleted `models/` and
   `manager_tenure/modeling/`, and `MODELS_DIR` in `config.py`.
2. **Build: Tidy dependencies.** Dev tools (ruff, pytest, jupyterlab, notebook, ipython,
   mkdocs) moved to the `dev` dependency group. scikit-learn, tqdm and pip dropped.
   pandera, lxml, requests and pyarrow added. Python pinned to 3.12, and `uv.lock`
   committed. Makefile targets use `uv run`. ruff covers `tests/` with the E, F, I, B, UP
   and SIM rules. The tqdm demo loops were removed from the placeholder `features.py`
   and `plots.py` so they still import.
3. **Chore: .gitignore.** `data/raw/` is committed. `data/interim/`, `data/processed/`
   and `data/external/` are ignored.
4. **Feat(pipeline): `dataset.py`.** Small plain functions to download the page with a
   polite User-Agent, save it as `data/raw/wiki_premier_league_managers_<date>.html`
   plus `metadata.json` (url, retrieved_at, filename, sha256, bytes), and skip the
   download if a snapshot exists unless `--refresh` is passed. Settings are in
   `config.py`.
5. **Data: raw snapshot from 2026-11-23** (2.4 MB, sha256 `be6bac2d…`).
6. **Test:** 8 small tests for the snapshot and metadata helpers. They never use the
   network.
7. **CI:** `.github/workflows/python.yml` runs `uv sync --locked`, ruff check, ruff
   format check, pytest and the dataset step.
8. **Docs:** a README quickstart, this file, `open-questions.md` and the CLAUDE.md status.

## How to run it

```bash
uv sync
make lint
make test
make data                                          # no download: snapshot exists
uv run python -m manager_tenure.dataset --refresh  # take a new snapshot
```

## Worth knowing

- The cloud environment blocked Wikipedia at first. A personal cloud environment called
  `football-manager-tenure` was created with `en.wikipedia.org` allowed, so future cloud
  sessions can use it.
- The work is on branch `claude/milestone-1a-python-basics-q4sxhi`, not
  `setup-python-basics` (see open question 6).

## Open questions

See [open-questions.md](open-questions.md). The main one for the next session is which
Wikipedia table(s) to parse.

## Suggested next step (together)

Milestone 1b: write the parsing in `features.py`: read the snapshot with
`pandas.read_html` (lxml), make the interim table, then clean it (dates, "Present" †,
caretaker ‡), add a pandera schema and tests with "known facts", and write
`spells.parquet` and `spells.json`.
