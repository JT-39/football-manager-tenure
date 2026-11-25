# CLAUDE.md: project brief for any Claude Code session (local or cloud)

## What this project is
"The Managerial Merry-Go-Round" is an interactive chart of how long Premier League managers last. It covers every managerial spell since 1992, drawn as a timeline, plus a chart asking "is patience dying?".

- **Data:** Wikipedia's "List of Premier League managers" (CC BY-SA; credit it on the site).
  - One row per spell, with columns Name, Nat., Club, From, Until, and Duration (days).
  - Ongoing spells show "Present" and are marked †. Caretakers are marked ‡.
- **Python pipeline:** Cookiecutter Data Science layout, following RAP principles. The package is `manager_tenure/`.
- **Website:** Vite + React + TypeScript + D3 in `web/` (not created yet). It deploys to GitHub Pages through GitHub Actions.

## Who the user is: read this first
- They're a professional data scientist (R, Python, Shiny, some HTML and CSS) and **new to React and web development**. They want to **learn**, not just receive finished code.
- **Don't build everything.** Do the agreed step, explain it, then stop. Leave the learning-heavy parts (React components, D3 charts) to be built *together* in an interactive session.
- **Don't make big decisions alone.** That includes chart design, adding frameworks or major libraries, changing the data source, restructuring the repo, or anything that's hard to undo. Write the question down in `docs/docs/open-questions.md` and move on, or stop.
- Explain web concepts with Shiny analogies:
  - `useState` ≈ `reactiveVal`
  - `useMemo` ≈ `reactive()`
  - `useEffect` ≈ `observe()`
  - components ≈ modules

## Standards (non-negotiable)
- **Python:** follow the `python-data-science` skill in `.claude/skills/`:
  - Use uv only (`uv add`, `uv sync`, `uv run …`), ruff, pytest, and loguru logging.
  - **Keep code simple:** plain typed functions with short docstrings, no classes unless they're a big win, and no clever abstractions.
- **Git:** follow the `git-commits` skill in `.claude/skills/`:
  - Commit little and often, with detailed messages in plain, simple language that explain what and why.
  - **No Claude or AI attribution, ever:** no Co-Authored-By trailer and no "Generated with" line.
  - **Commit as the repo owner.** Before the first commit in any session (especially cloud sessions), run
    `git config user.name "Jake Tufts"` and `git config user.email "137207796+JT-39@users.noreply.github.com"`.
- **Charts:** use the `dataviz-skills` plugin, which is enabled in `.claude/settings.json`.
  - Use `d3` for React + D3 work: D3 does the math, React renders; use a MARGIN object with bounds, `useDimensions` plus `Responsive*` wrappers, and no `d3.select`.
  - Use `inspiration` before designing a chart, `roast-my-chart` before publishing, and `matplotlib` for static figures.
- **RAP:**
  - Raw data is immutable, saved as a dated snapshot with its URL, retrieval time and sha256.
  - One command (`make data`, later `make all`) rebuilds everything from raw.
  - Validate data at stage boundaries with pandera.
  - Put settings in `manager_tenure/config.py`, not magic numbers in the code.
  - CI runs lint, tests and the pipeline.

## The agreed plan (milestones)
1. **Python basics and the data pipeline.**
   - Tidy the scaffold.
   - Raw snapshot → interim table → cleaned `data/processed/spells.parquet` + `spells.json`.
   - pandera schema, pytest tests, Python CI.
2. **Static React page** (Vite + React + TS) that loads `spells.json`. *Build this together.*
3. **First chart:** Tenure Timeline swimlane (club rows × time, bars coloured by tenure). *Together.*
4. **Interactivity:** tooltip, highlight the same manager across clubs, filters. *Together.*
5. **Second chart:** median tenure by season with an IQR band. Then responsiveness and animation (Motion). *Together.*
6. **Deploy:** GitHub Actions → GitHub Pages, at `https://jt-39.github.io/football-manager-tenure/`.

## Current status
Kept up to date by whoever works on the repo. Newest first.
- 2026-11-25: Milestone 1b written on branch `milestone-1b-clean-spells`. The user asked for the six cleaning functions to be written with explanations, instead of as exercises. All 22 tests pass and `make data` produces `data/interim/spells.parquet` (521 spells). Next: the duration investigation (open question 8), then the React side.
- 2026-11-23: **Milestone 1a done** (PR #1, merged).
  - Scaffold tidied, deps sorted with uv, `uv.lock` and `.python-version` committed.
  - `dataset.py` downloads and snapshots the Wikipedia page into `data/raw/` (snapshot from 2026-11-23 committed).
  - Tests and Python CI are in place.
  - Next is milestone 1b, built together: parse and clean into `spells.parquet`/`spells.json` with a pandera schema.
  - See `docs/docs/handoff.md` and `docs/docs/open-questions.md`.
- 2026-11-22: CCDS scaffold committed. Brief and skills added. A cloud session was asked to do the **first half of milestone 1 only**. See `docs/docs/handoff.md` once it exists.

## Useful commands
```bash
uv sync                 # install the exact locked environment
make lint / make format / make test / make data
uv run python -m manager_tenure.dataset   # fetch the raw snapshot
```
