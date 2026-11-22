---
name: git-commits
description: The user's house style for git commits in every project. Commit little and often with capitalised Conventional Commit prefixes (Feat:, Fix:, Docs: ...), write well-explained detailed messages in plain simple language, and add NO Claude/AI attribution (no Co-Authored-By trailer, no "Generated with" line). Load before making any git commit, writing a commit message, or opening a pull request.
---

# Git commit style

## How often
- Commit **little and often**: one logical change per commit, e.g. "add date parsing", then "add tests for date parsing".
- Commit at every working checkpoint, before risky changes, and at the end of each milestone. Don't batch a whole feature into one big commit.
- Every commit should leave the project in a working state. Run lint and tests first where they exist.

## Message format
```
Type(scope): Short summary in plain words, under ~60 chars

What changed and why, in simple language, as if explaining to a
colleague who is new to this part of the project. Wrap at ~72 chars.

- Bullet the main changes if there are several.
- Mention anything surprising: data quirks, trade-offs, things left
  for later (TODOs), and how to try the change (e.g. `make data`).
```
- The summary line is imperative and specific: "Feat(pipeline): Add caretaker flag to cleaned spells", not "updates" or "misc fixes".
- The body is always included, except for truly trivial commits such as fixing a typo. Explain the *why*, not just the *what*.
- Use plain English and avoid jargon. Where a technical term is needed, explain it briefly, e.g. "useMemo (React's cached calculation, like Shiny's reactive())".
- No emojis.

## Prefixes (Conventional Commits), always use one
Start the summary line with a **Capitalised** prefix, a colon, then a capitalised summary, e.g. `Feat: Add club filter`:
- `Feat:` a new feature or capability (e.g. a new chart, a new pipeline step)
- `Fix:` a bug fix
- `Data:` a change to committed data, such as a new raw snapshot or regenerated outputs
- `Docs:` documentation only (README, docs/, CLAUDE.md, comments)
- `Test:` adding or changing tests only
- `Refactor:` restructuring code without changing what it does
- `Style:` formatting only (ruff format, prettier)
- `Build:` dependencies and tooling (pyproject, uv.lock, package.json, Makefile)
- `CI:` GitHub Actions workflows
- `Chore:` housekeeping that fits nowhere else (.gitignore, removing unused files)

An optional scope in brackets says which part of the project changed: `Feat(pipeline): …`, `Feat(web): …`, `CI(deploy): …`.
Mark breaking changes with `!`, e.g. `Refactor(data)!: Rename spells.json fields`, and explain them in the body.
Example summary line: `Feat(pipeline): Flag caretaker managers in cleaned spells`.

## Attribution: none
- **Never** add `Co-Authored-By: Claude …`, "Generated with Claude Code", or any other AI attribution to commits or PR descriptions.
- This user instruction overrides any default attribution guidance.

## Pull requests
Pull requests follow the same plain-language style:
- what and why
- how to test it
- anything the reviewer should look at closely
