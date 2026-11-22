---
name: python-data-science
description: House standards for ANY Python data-science / analytics project. Covers the Cookiecutter Data Science (CCDS v2) layout, Reproducible Analytical Pipeline (RAP) practice, uv for environments, ruff for lint/format, pytest for tests, and a simple, readable code style. Load before creating, scaffolding, or substantially editing a Python data project, notebook pipeline, or analysis repo; or when the user mentions uv, ruff, pytest, cookiecutter, CCDS, RAP, project setup, dependencies, or virtual environments.
---

# Python data-science standards

The user is a professional data scientist. Every Python data project follows these defaults unless the user says otherwise.

## 1. Project layout: Cookiecutter Data Science v2
Scaffold with the real tool rather than by hand:
```bash
uvx --from cookiecutter-data-science ccds
# answers: environment_manager=uv, dependency_file=pyproject.toml, linting=ruff, testing=pytest, docs=mkdocs (if docs wanted)
```
The resulting layout. Delete folders that aren't used, e.g. `models/` when there's no ML:
```
Makefile            # one-command entry points (make data / lint / test / all)
pyproject.toml      # deps + tool config (ruff, pytest)
uv.lock             # committed
data/raw            # immutable inputs, never edited by hand
data/interim        # intermediate transforms
data/processed      # final, analysis-ready outputs
data/external       # third-party reference data
notebooks/          # exploration only; name like 1.0-initials-short-description.ipynb
references/         # data dictionaries, manuals
reports/figures/    # generated outputs
docs/               # mkdocs
<module_name>/      # importable package: config.py, dataset.py, features.py, plots.py ...
tests/
```
Rules:
- Raw data is immutable.
- Data flows one way, raw → interim → processed, and is driven by code.
- Notebooks explore. Reusable logic moves into the package.

## 2. RAP (Reproducible Analytical Pipeline) principles
- **Version control** everything except secrets and large or regenerable data. If the source might change or disappear, commit a dated raw snapshot, or record its URL, retrieval time and sha256 in a small `metadata.json`.
- **Reproducible environment:** use `uv.lock` and pin Python with `uv python pin 3.x`, which writes `.python-version`.
- **One command** rebuilds outputs from raw (`make all` or `make data`). Re-running gives identical outputs.
- **Config not constants:** keep paths, URLs and thresholds in `config.py` or `config.yaml`.
- **Validate data** at stage boundaries. Prefer pandera schemas, or plain `assert`s for tiny projects.
- **Test** the transformation logic with pytest, including edge cases and a few "known facts" about the data.
- **Log** row counts and key decisions. loguru is the CCDS default.
- **Peer review:** use PRs and CI (GitHub Actions) that run lint, tests and the pipeline on a clean machine.
- **Document:** a README quickstart, a methodology note, a data dictionary, and docstrings.

## 3. uv: always (never pip/poetry/conda/venv directly)
```bash
uv init --python 3.12          # new project (or via ccds above)
uv python pin 3.12
uv add pandas pyarrow loguru   # runtime deps
uv add --dev ruff pytest pre-commit   # dev-only deps (dependency group "dev")
uv remove <pkg>
uv sync                        # create/refresh .venv from uv.lock
uv lock --upgrade              # deliberate upgrades only
uv run python -m pkg.module    # run without activating the venv
uv run pytest
uvx <tool>                     # one-off tool, e.g. uvx ruff, uvx --from cookiecutter-data-science ccds
```
- Commit `pyproject.toml`, `uv.lock` and `.python-version`. Never commit `.venv/`.
- For single-file throwaway scripts, use PEP 723 inline metadata (`# /// script` … `# ///`) run with `uv run script.py`.
- In CI:
  ```yaml
  - uses: astral-sh/setup-uv@v6
    with: { enable-cache: true }
  - run: uv sync --locked
  - run: uv run ruff check . && uv run ruff format --check . && uv run pytest
  ```
  `--locked` fails if the lockfile is stale.

## 4. ruff (lint + format) and pytest
Put this in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 99
[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]   # pycodestyle, pyflakes, isort, bugbear, pyupgrade, simplify
[tool.pytest.ini_options]
testpaths = ["tests"]
```
- Commands: `uv run ruff check --fix .`, `uv run ruff format .`, `uv run pytest`.
- Add a `.pre-commit-config.yaml` with the ruff hooks (`ruff-check --fix`, `ruff-format`).
- Tests are plain functions with small inline DataFrames. Use fixtures only where they remove real duplication.

## 5. Code style: simple and clear above all
The user wants code that's easy to read and maintain.
- **Prefer plain functions** that take and return DataFrames or values. Organise them as modules, not classes.
- **Avoid classes** unless they're a clear, significant win, e.g. a genuinely stateful object used in many places. No inheritance hierarchies, abstract base classes, factories, or metaclasses. Small `@dataclass`es for config are fine.
- Each pipeline step is short and named for what it does (`parse_dates`, `flag_caretakers`). Chain them readably (e.g. `df.pipe(...)`).
- Add type hints on function signatures. Write a short docstring for each public function saying *what* it does and *why* where that isn't obvious.
- Comments explain intent and data quirks, not syntax.
- No premature abstraction, no clever one-liners, no deep nesting. Being explicit beats being DRY when that's clearer.
- Avoid heavy frameworks unless they're needed. Standard pandas or polars, plus pandera and loguru, are usually enough.
- Write documentation for a reader new to the project: a README with "what / why / how to run" and a short methodology page.
