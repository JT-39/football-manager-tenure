# Open questions and decisions

Questions that need the project owner's decision. Nobody should choose these alone.
Add new ones at the top; when one is decided, note the answer and the date.

## Added 2026-11-23 (milestone 1b)

8. **Our tenure vs Wikipedia's "Duration (days)".** About 4% of finished spells disagree,
   mostly by one day, but some by a lot (Alex McLeish at Birmingham: 1292 vs 1496).
   Which do we trust, and should a validation check flag the disagreements? To be decided
   after the exercises are finished. See `milestone-1b-exercises.md`.

**Decided 2026-11-23:**
- **Question 1:** the spells table is the one with a "Duration (days)" column (521
  rows).
- Spells that started before the Premier League keep both their real start date and a
  Premier League start date (15 Aug 1992), so both tenures are available.

  **Revised 2026-11-25:** the 1992 cut-off is replaced by the Premier League seasons from
  Wikipedia's "Years in League" column. Both measures are now kept: `tenure_days` (total
  time in charge) and `pl_tenure_days` (days in Premier League seasons). The 1992 cut-off
  counted lower-division years as Premier League time (e.g. Eddie Howe at Bournemouth).
  Season labels are read as start years, with ranges ending before their last year
  ("2015–2020" is 2015/16 to 2019/20), which fits most spells.

  **Found 2026-11-25 while building the notebook (not yet decided):** 71 spells show zero
  Premier League days, and several are wrong. Stewart Houston (Arsenal, 1995) and David Webb
  (Chelsea, 1993) are in the Premier League seasons, but the labels were read as the season
  that starts in that year. Checking the labels against known spells shows:
  - Ranges (`2012–2013`) match the season that *starts* in the first year. This works well.
  - Single years (`1993`) often mean the season that *ends* in that year.
  - Spells that cross two seasons only get the season Wikipedia lists, so they are undercounted
    (Mark Hughes, Southampton 2018).

  Options, to decide together:
  - **(a)** Read single years as the season that ends in that year. This fixes about 12 known
    cases but is still a guess for some rows.
  - **(b)** Use a separate table of which clubs were in the Premier League in each season. This
    is the most accurate, but it's a new data source and a bigger piece of work.
  - **(c)** Publish total tenure only for now, and leave out Premier League tenure until (b).

**Known data issue:** the labels aren't fully consistent. West Ham's spell for Graham
  Potter is labelled "2025" alone, but he was there from January to September 2025, so
  only 57 Premier League days are counted. Chelsea's "2022–2023" follows the same reading,
  so this looks like a labelling error on the Wikipedia page. Decide later whether to fix
  specific rows by hand (with a note) or to accept them.
- Nationality is read from the flag images.

## Added 2026-11-23 (milestone 1a)

1. **Which table(s) on the Wikipedia page are "the" spells table?**
   The snapshot has five `wikitable` tables (three `sortable nowrap`, one
   `sortable plainrowheaders`, one plain). The parsing session needs to decide which to
   read, and whether the page splits current and former managers across tables.

2. **One `metadata.json` or one per snapshot?**
   Right now `data/raw/metadata.json` describes the latest snapshot only (it includes the
   file name). If we take a `--refresh` snapshot later, the old snapshot's HTML stays in
   git but its metadata is overwritten (it is still in git history). Alternatives: name
   it `<snapshot>.metadata.json`, or keep a list of snapshots in one file.

   **Decided 2026-11-23:** one `<snapshot>.metadata.json` per snapshot, sitting next to
   its HTML, so no snapshot ever loses its record of where it came from.

3. **Should a refresh delete older snapshots?**
   Currently they are kept, and the pipeline always uses the newest by date. Keeping them
   grows the repo by about 2.4 MB each time.

   **Decided 2026-11-23:** keep them. Old analyses stay reproducible from the exact data
   they used, and refreshes are rare, so the size cost is small.

4. **Should `spells.json` be committed?**
   `data/processed/` is git-ignored for now. The website build could either run the
   Python pipeline in CI, or read a committed `spells.json`. This affects the deploy
   workflow in milestone 6.

5. **User-Agent contact details.**
   Wikipedia's policy asks for a contact URL or email in the User-Agent. The current one
   (in `config.py`) is generic and has no contact details, because personal details were
   not to be added without asking. You may want to add the repo URL.

6. **Branch name.** The task brief asked for a branch called `setup-python-basics`. The
   cloud session was only allowed to push to `claude/milestone-1a-python-basics-q4sxhi`,
   so the work and pull request use that branch instead.

7. **Leftover template code.** `features.py` and `plots.py` are still the CCDS
   placeholders (with a typer CLI). `typer`, `matplotlib`, `numpy` and `python-dotenv`
   are still dependencies. Keep them, or drop what we don't use once the real code
   exists?

   **Partly decided 2026-11-23:** `typer` removed. Each step is now a plain function run with
   `python -m ...`, because one rarely used flag did not justify a command-line framework.
   `matplotlib`, `numpy` and `python-dotenv` are still undecided.
