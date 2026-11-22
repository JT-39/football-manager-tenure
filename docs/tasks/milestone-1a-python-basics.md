# Task brief: milestone 1a (Python basics)

Written 2026-11-22 for a Claude Code cloud session. Start the session with: *"Do the task in docs/tasks/milestone-1a-python-basics.md"*.

Read CLAUDE.md first and follow it exactly, along with the skills in .claude/skills (python-data-science, git-commits).

Scope: ONLY the first half of milestone 1 (Python basics). Work on a new branch `setup-python-basics`, push it, and open a pull request into main. Do NOT merge, and do NOT start any React/web work.

Tasks, each as its own small commit with a Capitalised prefix (e.g. "Chore: Remove unused ML scaffold") with a detailed, plain-English message and NO Claude attribution:
1. Chore: remove the unused ML scaffold (models/, manager_tenure/modeling/).
2. Build: tidy pyproject.toml with uv:
   - Move ruff, pytest, jupyterlab, notebook, ipython and mkdocs into a dev dependency group.
   - Drop scikit-learn, tqdm and pip.
   - Add pandera, lxml, requests and pyarrow.
   - Run `uv python pin 3.12` and commit uv.lock.
   - Make Makefile targets use `uv run`.
   - Extend ruff to cover tests/ and add the E, F, I, B, UP, SIM rules.
3. Chore: update .gitignore so data/raw/ IS committed (RAP raw snapshot), and data/interim/ and data/processed/ stay ignored for now.
4. Feat(pipeline): write manager_tenure/dataset.py as plain functions:
   - Download the Wikipedia "List of Premier League managers" page HTML with a polite User-Agent.
   - Save it as data/raw/wiki_premier_league_managers_<YYYY-MM-DD>.html with metadata.json (url, retrieved_at, sha256).
   - Skip the download if a snapshot exists, unless --refresh is passed.
   - Put config in config.py. Run it once and commit the snapshot as a separate Data: commit.
5. Test: replace the placeholder test with small tests for the snapshot and metadata helpers. Make `make lint` and `make test` pass.
6. CI: add .github/workflows/python.yml (setup-uv, uv sync --locked, ruff check, ruff format --check, pytest).
7. Docs: write a plain-English README quickstart. Add docs/docs/handoff.md listing what you did, how to run it, and open questions/decisions for the user. Update the "Current status" section in CLAUDE.md.

Stop there. Do NOT write the cleaning/parsing logic (features.py) or any pandera schema. The user wants to review and learn from those together. Don't make big decisions: if anything is ambiguous, write it in the open questions file instead of choosing.
